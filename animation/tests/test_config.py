"""Configuration contract probes without renderers, models or network access."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import wave

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import config
import narration
import processes
import voice_review


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='animation-config-')
        self.root=Path(self.temporary.name).resolve()
        self.example=self.root/'local.example.json'
        self.example.write_text(json.dumps({'ffmpeg':'ffmpeg'}))
        self.env=patch.dict(os.environ,{},clear=False)
        self.env.start()
        os.environ.pop('ANIMATION_CONFIG',None)
        self.scripts=patch.object(config,'SCRIPTS',self.root)
        self.scripts.start()

    def tearDown(self):
        self.scripts.stop();self.env.stop();self.temporary.cleanup()

    def write(self,name,value):
        path=self.root/name;path.write_text(json.dumps(value));return path

    def test_fallback_then_private_then_explicit_selection(self):
        self.assertEqual(config.settings().source,self.example)
        private=self.write('local.json',{'ffmpeg':'private-tool'})
        self.assertEqual(config.settings().source,private)
        explicit=self.write('custom.json',{'ffmpeg':'custom-tool'})
        os.environ['ANIMATION_CONFIG']=str(explicit)
        self.assertEqual(config.settings().source,explicit)
        self.assertEqual(config.settings()['ffmpeg'],'custom-tool')

    def test_missing_explicit_configuration_does_not_silently_fall_back(self):
        os.environ['ANIMATION_CONFIG']=str(self.root/'missing.json')
        with self.assertRaisesRegex(ValueError,'Cannot read animation configuration'):
            config.settings()

    def test_blank_explicit_configuration_is_an_error(self):
        os.environ['ANIMATION_CONFIG']=' '
        with self.assertRaisesRegex(ValueError,'must name a JSON file'):config.settings()

    def test_malformed_configuration_is_an_actionable_error(self):
        path=self.root/'bad.json';path.write_text('{')
        with self.assertRaisesRegex(ValueError,'Cannot read animation configuration'):config.settings(path)
        for value in ([],{'ffmpeg':True},{'ffmpeg':{}}):
            self.write('bad.json',value)
            with self.assertRaises(ValueError):config.settings(path)

    def test_relative_paths_anchor_to_selected_config_not_working_directory(self):
        custom=self.root/'profile';custom.mkdir()
        profile=custom/'runtime.json';profile.write_text(json.dumps({'model':'../assets/model.bin'}))
        value=config.settings(profile)
        self.assertEqual(config.configured(value,'model'),self.root/'assets/model.bin')

    def test_bare_executables_resolve_on_path(self):
        value=config.settings(self.write('custom.json',{'python':Path(sys.executable).name}))
        with patch('config.shutil.which',return_value=sys.executable):
            self.assertEqual(config.configured(value,'python'),Path(sys.executable).absolute())

    def test_null_optional_value_produces_configuration_instruction(self):
        value=config.settings(self.write('custom.json',{'model':None}))
        with self.assertRaisesRegex(ValueError,'Configure model in ANIMATION_CONFIG'):
            config.configured(value,'model')

    def test_configured_private_speech_interpreter_is_used(self):
        speech=self.root/'speech';(speech/'models').mkdir(parents=True)
        for name in ('synthesize.py','models/kokoro-v1.0.onnx','models/voices-v1.0.bin'):
            (speech/name).write_bytes(b'test runtime fingerprint')
        profile=self.write('custom.json',{'speech_root':'./speech','speech_python':'./custom-python'})
        os.environ['ANIMATION_CONFIG']=str(profile)
        spec=self.write('spec.json',{'segments':[{'id':'hello','text':'Hello.'}]})
        calls=[]
        def execute(argv,log,**kwargs):
            calls.append(argv)
            if '--output' in argv:
                target=Path(argv[argv.index('--output')+1]);rate=24000;channels=1
            else:target=Path(argv[-1]);rate=48000;channels=2
            with wave.open(str(target),'wb') as output:
                output.setnchannels(channels);output.setsampwidth(2);output.setframerate(rate)
                output.writeframes(b'\0'*(rate*channels*2//10))
            Path(log).write_text('test adapter executed')
        with patch.object(narration,'execute',execute), patch.object(narration,'kokoro_runtime',return_value={'test':'runtime'}):
            narration.prepare(spec,self.root/'audio',self.root/'cache')
        self.assertEqual(calls[0][0],self.root/'custom-python')
        self.assertEqual(calls[0][2],speech/'synthesize.py')
        self.assertTrue((self.root/'audio/receipt.json').is_file())

    def test_kokoro_dependency_version_change_invalidates_cached_take(self):
        speech=self.root/'speech';(speech/'models').mkdir(parents=True)
        for name in ('synthesize.py','models/kokoro-v1.0.onnx','models/voices-v1.0.bin'):
            (speech/name).write_bytes(b'test runtime fingerprint')
        profile=self.write('runtime.json',{'speech_root':'./speech','speech_python':sys.executable})
        os.environ['ANIMATION_CONFIG']=str(profile)
        spec=self.write('spec.json',{'segments':[{'id':'one','text':'A sentence.'}]})
        version=['1'];synthesis=[]
        def inspect(argv,**kwargs):
            self.assertEqual(argv[0],sys.executable)
            self.assertEqual(argv[1:3],['-I','-c'])
            packages={name:version[0] for name in ('kokoro-onnx','numpy','onnxruntime','soundfile','espeakng-loader','phonemizer')}
            return SimpleNamespace(stdout=json.dumps({'python':'3.14.0','packages':packages}))
        def execute(argv,log,**kwargs):
            target=Path(argv[argv.index('--output')+1]) if '--output' in argv else Path(argv[-1])
            if '--output' in argv:synthesis.append(target)
            with wave.open(str(target),'wb') as output:
                output.setnchannels(2);output.setsampwidth(2);output.setframerate(48000);output.writeframes(b'\0'*19200)
        with patch.object(narration.subprocess,'run',inspect),patch.object(narration,'execute',execute):
            first=narration.prepare(spec,self.root/'first',self.root/'cache')
            reused=narration.prepare(spec,self.root/'reused',self.root/'cache')
            version[0]='2'
            changed=narration.prepare(spec,self.root/'changed',self.root/'cache')
        self.assertFalse(first[0]['cache_hit']);self.assertTrue(reused[0]['cache_hit']);self.assertFalse(changed[0]['cache_hit'])
        self.assertEqual(first[0]['cache_key'],reused[0]['cache_key'])
        self.assertNotEqual(first[0]['cache_key'],changed[0]['cache_key']);self.assertEqual(len(synthesis),2)

    def test_process_runner_uses_custom_configured_media_directories(self):
        binaries=[]
        for name in ('ffmpeg','ffprobe'):
            folder=self.root/name;folder.mkdir();binary=folder/name
            binary.write_text('#!/bin/sh\nexit 0\n');binary.chmod(0o755);binaries.append(binary)
        profile=self.write('custom.json',dict(zip(('ffmpeg','ffprobe'),map(str,binaries))))
        os.environ['ANIMATION_CONFIG']=str(profile)
        result=processes.run([sys.executable,'-c','import os;print(os.environ["PATH"])'],self.root/'child.log',timeout=5)
        self.assertEqual(result.strip().split(os.pathsep)[:2],[str(p.parent) for p in binaries])

    def test_voice_review_uses_configured_paths_and_retains_legacy_support(self):
        legacy=self.root/'legacy';(legacy/'bin').mkdir(parents=True)
        (legacy/'bin/whisper-cli').write_text('legacy')
        with patch.object(voice_review,'LEGACY_WHISPER_ROOT',legacy):
            self.assertEqual(voice_review.whisper_path({},'whisper_cli','bin/whisper-cli'),legacy/'bin/whisper-cli')
            with self.assertRaisesRegex(ValueError,'Configure whisper_cli'):
                voice_review.whisper_path({'whisper_cli':None},'whisper_cli','bin/whisper-cli')
            profile=self.write('whisper.json',{'whisper_cli':'./custom/whisper-cli'})
            self.assertEqual(voice_review.whisper_path(config.settings(profile),'whisper_cli','bin/whisper-cli'),self.root/'custom/whisper-cli')

    def test_narration_import_has_no_runtime_configuration_dependency(self):
        # Importing validation helpers remains possible before optional voice setup.
        with patch('config.settings',side_effect=AssertionError('should be lazy')):
            importlib.reload(narration)
        importlib.reload(narration)
        self.assertEqual(narration.validate_spec({'segments':[{'id':'one','text':'A sentence.'} ]})[0],'kokoro')


if __name__=='__main__':unittest.main()
