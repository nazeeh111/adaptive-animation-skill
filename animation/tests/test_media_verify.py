"""Actual FFmpeg fixtures preserve delivery checks without any Manim runtime."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from media_verify import inspect_video


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required for media integration checks')
class MediaVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory(prefix='animation-media-tests-')
        cls.root=Path(cls.temporary.name).resolve()
        cls.config=cls.root/'config.json'
        cls.config.write_text(json.dumps({key:shutil.which(key) for key in ('ffmpeg','ffprobe')}))
        base=[shutil.which('ffmpeg'),'-v','error','-nostdin','-n','-f','lavfi','-i','color=c=blue:s=64x64:r=10:d=1']
        def render(name,extra):
            output=cls.root/name
            subprocess.run(base+extra+[str(output)],check=True,capture_output=True,timeout=20)
            return output
        cls.good=render('good.mp4',['-c:v','libx264','-pix_fmt','yuv420p'])
        cls.other_codec=render('other.mp4',['-c:v','mpeg4'])
        cls.good_audio=render('good-audio.mp4',['-f','lavfi','-i','sine=frequency=440:duration=1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac'])
        cls.short_audio=render('short-audio.mp4',['-f','lavfi','-i','sine=frequency=440:duration=0.4','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac'])
        cls.two_videos=render('two-videos.mp4',['-map','0:v','-map','0:v','-c:v','libx264','-pix_fmt','yuv420p'])

    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()

    def setUp(self):
        self.environment=patch.dict(os.environ,{'ANIMATION_CONFIG':str(self.config)})
        self.environment.start()

    def tearDown(self):self.environment.stop()

    def test_full_decode_and_all_exact_contracts(self):
        result=inspect_video(self.good,(64,64),Fraction(10),False,1,10)
        self.assertEqual(result['full_decode'],'passed')
        self.assertEqual(result['contract_verification'],'passed')
        self.assertEqual(result['video_frames'],10)
        self.assertEqual(result['audio_streams'],0)
        self.assertEqual(len(result['sha256']),64)

    def test_audio_delivery_decodes_and_aligns(self):
        result=inspect_video(self.good_audio,audio=True)
        self.assertEqual(result['audio_streams'],1);self.assertEqual(result['full_decode'],'passed')

    def test_fractional_frame_rate_contract(self):
        output=self.root/'fractional.mp4'
        subprocess.run([shutil.which('ffmpeg'),'-v','error','-nostdin','-n','-f','lavfi','-i',
                        'color=c=blue:s=64x64:r=24000/1001','-frames:v','24','-c:v','libx264','-pix_fmt','yuv420p',str(output)],
                       check=True,capture_output=True,timeout=20)
        result=inspect_video(output,fps=Fraction(24000,1001),expected_duration=1.001,expected_frames=24)
        self.assertEqual(result['fps'],'24000/1001');self.assertEqual(result['contract_verification'],'passed')

    def test_required_audio_is_checked(self):
        with self.assertRaisesRegex(ValueError,'Expected audio'):inspect_video(self.good,audio=True)

    def test_audio_end_alignment_is_preserved_even_without_audio_flag(self):
        with self.assertRaisesRegex(ValueError,'Audio/video timeline mismatch'):inspect_video(self.short_audio)

    def test_h264_delivery_codec_is_preserved(self):
        with self.assertRaisesRegex(ValueError,'Unexpected codec'):inspect_video(self.other_codec)

    def test_exactly_one_video_stream_is_required(self):
        with self.assertRaisesRegex(ValueError,'exactly one video'):inspect_video(self.two_videos)

    def test_wrong_resolution_rate_duration_and_frames_fail(self):
        for options,error in [({'resolution':(128,64)},'Resolution mismatch'),({'fps':Fraction(11)},'Frame rate mismatch'),
                              ({'expected_duration':.9},'Duration mismatch'),({'expected_frames':9},'Frame count mismatch')]:
            with self.subTest(options=options),self.assertRaisesRegex(ValueError,error):inspect_video(self.good,**options)

    def test_studio_dispatch_works_without_manim_configuration(self):
        result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'studio.py'),'verify',str(self.good),'--fps','10','--frames','10'],
                              check=True,capture_output=True,text=True,timeout=20)
        self.assertEqual(json.loads(result.stdout)['video_frames'],10)

    def test_empty_and_corrupt_inputs_fail(self):
        empty=self.root/'empty.mp4';empty.write_bytes(b'')
        corrupt=self.root/'corrupt.mp4';corrupt.write_bytes(b'not a video')
        with self.assertRaisesRegex(ValueError,'empty video'):inspect_video(empty)
        with self.assertRaisesRegex(ValueError,'verification command failed'):inspect_video(corrupt)


if __name__=='__main__':unittest.main()
