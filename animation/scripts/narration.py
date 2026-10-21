#!/usr/bin/env python3
"""Measured, cached offline sentence takes. Kokoro default; explicit optional offline Qwen preset engine."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import wave
from processes import run as execute
from config import configured, settings

QWEN_WORKER=Path(__file__).parent/'qwen_worker.py'
QWEN_VOICES={'serena','vivian','uncle_fu','ryan','aiden','ono_anna','sohee','eric','dylan'}
QWEN_LANGUAGES={'auto','chinese','english','german','italian','portuguese','spanish','japanese','korean','french','russian'}


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def stamp(frame,fps):
    ms=round(frame*1000/fps)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def caption_payload(text):
    """Keep intentional lines without letting paragraph gaps delimit SRT cues."""
    lines=text.replace('\r\n','\n').replace('\r','\n').split('\n')
    return '\n'.join(line.strip() for line in lines if line.strip())


def number(value, name, lower, upper):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lower<=value<=upper:
        raise ValueError(name+' must be finite and between '+str(lower)+' and '+str(upper))
    return value


def qwen_controls(spec, segment, spoken):
    def pick(name, default):return segment.get(name,spec.get(name,default))
    if 'speed' in spec or 'speed' in segment:
        raise ValueError('Qwen speed is unsupported; expression uses instruct, not speed changes')
    voice=pick('voice','Ryan');language=pick('language','English');instruct=pick('instruct','')
    if not isinstance(voice,str) or voice.lower() not in QWEN_VOICES:raise ValueError('Unsupported Qwen preset voice')
    if not isinstance(language,str) or language.lower() not in QWEN_LANGUAGES:raise ValueError('Unsupported Qwen language')
    if not isinstance(instruct,str) or len(instruct)>500 or any(ord(ch)<32 and ch not in '\n\t' for ch in instruct):
        raise ValueError('Qwen instruct must be text of at most500characters without control characters')
    if not isinstance(spoken,str) or not spoken.strip() or len(spoken)>300 or len(spoken.split())>35:
        raise ValueError('Qwen spoken segments must be short: at most35words and300characters; split longer passages')
    if any(ord(ch)<32 and ch not in '\n\t' for ch in spoken):raise ValueError('Unsupported control character in Qwen spoken text')
    seed=pick('seed',0);tokens=pick('max_tokens',700)
    if type(seed) is not int or not 0<=seed<=4294967295:raise ValueError('Qwen seed must be an integer from0 to4294967295')
    if type(tokens) is not int or not 64<=tokens<=900:raise ValueError('Qwen max_tokens must be an integer from64 to900')
    temperature=float(number(pick('temperature',.7),'Qwen temperature',.1,1.5))
    return {'voice':voice.lower(),'language':language.lower(),'instruct':instruct.strip(),
            'seed':seed,'temperature':temperature,'max_tokens':tokens}


def validate_spec(spec):
    if not isinstance(spec,dict):raise ValueError('Narration spec must be an object')
    engine=spec.get('engine','kokoro')
    if engine not in ('kokoro','qwen'):raise ValueError('Unsupported narration engine')
    raw_fps=spec.get('fps',30)
    try:fps=int(raw_fps)
    except (ValueError,TypeError,OverflowError):raise ValueError('FPS must divide48000 exactly')
    if isinstance(raw_fps,bool) or (isinstance(raw_fps,float) and raw_fps!=fps) or fps<=0 or 48000%fps:
        raise ValueError('FPS must divide48000 exactly for this PCM mixer')
    segments=spec.get('segments')
    if not isinstance(segments,list) or not segments:raise ValueError('At least one narration segment is required')
    shared={'engine','fps','voice','language','speed','pronunciations','segments'}
    fields={'id','text','spoken','voice','language','speed','take','pause_after','minimum_seconds'}
    extra={'instruct','seed','temperature','max_tokens'} if engine=='qwen' else set()
    if engine=='qwen':qwen_controls(spec,{},'validation')
    if engine=='kokoro' and set(spec)&{'instruct','seed','temperature','max_tokens'}:
        raise ValueError('Qwen controls require explicit engine=qwen; Kokoro does not provide expression instructions')
    if set(spec)-(shared|extra):raise ValueError('Unsupported '+engine.title()+' spec controls: '+', '.join(sorted(set(spec)-(shared|extra))))
    substitutions=spec.get('pronunciations',{})
    if not isinstance(substitutions,dict) or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v.strip() for k,v in substitutions.items()):
        raise ValueError('Pronunciations must map nonblank text to nonblank spoken text')
    ids=[];validated=[]
    for segment in segments:
        if not isinstance(segment,dict) or not isinstance(segment.get('text'),str) or not segment['text'].strip():
            raise ValueError('Each segment requires nonblank caption text')
        sid=segment.get('id')
        if not isinstance(sid,str) or not re.fullmatch(r'[a-zA-Z0-9_-]+',sid) or sid in ids:
            raise ValueError('Segment IDs must be unique simple names')
        ids.append(sid)
        if engine=='kokoro' and set(segment)&{'instruct','seed','temperature','max_tokens'}:
            raise ValueError('Qwen controls require explicit engine=qwen')
        if set(segment)-(fields|extra):raise ValueError('Unsupported '+engine.title()+' segment controls: '+', '.join(sorted(set(segment)-(fields|extra))))
        spoken=segment.get('spoken',segment['text']);changes=[]
        if not isinstance(spoken,str) or not spoken.strip():raise ValueError('Each segment requires nonblank spoken text')
        for original,replacement in substitutions.items():
            pattern=r'(?<!\w)'+re.escape(original)+r'(?!\w)'
            spoken,count=re.subn(pattern,lambda _:replacement,spoken)
            if count:changes.append({'from':original,'to':replacement,'count':count})
        take=segment.get('take','v1')
        if not isinstance(take,str) or not take.strip():raise ValueError('Take must be nonblank text')
        try:pause=float(segment.get('pause_after',.4));minimum=float(segment.get('minimum_seconds',0))
        except (ValueError,TypeError,OverflowError):raise ValueError('Invalid timing')
        if not math.isfinite(pause+minimum) or min(pause,minimum)<0:raise ValueError('Invalid timing')
        if engine=='qwen':controls=qwen_controls(spec,segment,spoken)
        else:
            try:speed=float(segment.get('speed',spec.get('speed',1)))
            except (ValueError,TypeError,OverflowError):raise ValueError('Speech speed must be finite and positive')
            if not math.isfinite(speed) or speed<=0:raise ValueError('Speech speed must be finite and positive')
            controls={'voice':segment.get('voice',spec.get('voice','bm_george')),
                      'language':segment.get('language',spec.get('language','en-gb')),'speed':speed}
            if any(not isinstance(controls[k],str) or not controls[k].strip() for k in ('voice','language')):
                raise ValueError('Voice and language must be nonblank text')
        validated.append({'segment':segment,'spoken':spoken,'substitutions':changes,'controls':controls,
                          'take':take,'pause':pause,'minimum':minimum})
    return engine,fps,validated


def offline_environment(state):
    env={k:os.environ[k] for k in ('PATH','HOME','LANG','TMPDIR') if k in os.environ}
    env.update({'HF_HOME':str(state/'hf'),'HF_HUB_CACHE':str(state/'hf/hub'),
                'XDG_CACHE_HOME':str(state),'TORCH_HOME':str(state/'torch'),
                'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1',
                'DO_NOT_TRACK':'1','TOKENIZERS_PARALLELISM':'false'})
    return env


def verify_qwen_model(model, manifest):
    model=Path(model).resolve();manifest=Path(manifest)
    records=json.loads(manifest.read_text());files=[];seen=set()
    if not isinstance(records,list) or not records:raise ValueError('Qwen model manifest must list exact local files')
    for record in records:
        name=record['file'];relative=Path(name)
        if not isinstance(name,str) or relative.is_absolute() or '..' in relative.parts or name in seen:
            raise ValueError('Unsafe or duplicate Qwen model manifest entry')
        seen.add(name);file=model/relative
        if file.is_symlink() or not file.is_file() or file.resolve().is_relative_to(model) is False:
            raise ValueError('Qwen model file missing or unsafe: '+name)
        if file.stat().st_size!=record['bytes'] or sha(file)!=record['sha256']:
            raise ValueError('Qwen model file hash mismatch: '+name)
        files.append({'file':name,'bytes':record['bytes'],'sha256':record['sha256']})
    actual={f.relative_to(model).as_posix() for f in model.rglob('*') if f.is_file()}
    if actual!=seen:raise ValueError('Qwen model tree differs from its exact manifest')
    required={'config.json','model.safetensors','tokenizer_config.json','vocab.json','merges.txt','speech_tokenizer/model.safetensors','speech_tokenizer/config.json'}
    if not required<=seen:raise ValueError('Qwen model manifest lacks required local dependencies')
    config=json.loads((model/'config.json').read_text())
    if config.get('tts_model_type')!='custom_voice':raise ValueError('Qwen requires the retained CustomVoice model')
    return {'manifest_sha256':sha(manifest),'files':sorted(files,key=lambda f:f['file'])}


def kokoro_runtime(config):
    """Fingerprint the actual isolated interpreter without importing speech/ML code."""
    speech=configured(config,'speech_root');python=configured(config,'speech_python')
    packages=('kokoro-onnx','numpy','onnxruntime','soundfile','espeakng-loader','phonemizer')
    inspection=('import importlib.metadata,json,sys;'
                'print(json.dumps({"python":sys.version.split()[0],"packages":'
                '{name:importlib.metadata.version(name) for name in '+repr(packages)+'}},sort_keys=True))')
    try:
        result=subprocess.run([str(python),'-I','-c',inspection],check=True,capture_output=True,
                              text=True,timeout=30)
        versions=json.loads(result.stdout)
        if (not isinstance(versions,dict) or not isinstance(versions.get('python'),str)
                or not isinstance(versions.get('packages'),dict)
                or set(versions['packages'])!=set(packages)
                or any(not isinstance(v,str) or not v for v in versions['packages'].values())):
            raise ValueError('Unexpected Kokoro runtime metadata')
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
        detail=getattr(error,'stderr','') or str(error)
        raise ValueError('Cannot inspect configured Kokoro interpreter: '+str(detail)[-2000:]) from error
    return {'engine':'kokoro','script':sha(speech/'synthesize.py'),
            'model':sha(speech/'models/kokoro-v1.0.onnx'),'voices':sha(speech/'models/voices-v1.0.bin'),
            'python_executable':str(python),'python_sha256':sha(python.resolve()),'versions':versions}


def qwen_runtime(config, cache):
    python=configured(config,'qwen_python');model=configured(config,'qwen_model');manifest=configured(config,'qwen_model_manifest')
    if not python.is_file() or not os.access(str(python),os.X_OK):raise ValueError('Existing Qwen Python unavailable; no automatic installation')
    if not QWEN_WORKER.is_file():raise ValueError('Qwen worker missing')
    fingerprint=verify_qwen_model(model,manifest)
    result=subprocess.run([str(python),'-I',str(QWEN_WORKER),'--inspect-runtime'],check=True,capture_output=True,text=True,
                          timeout=30,env=offline_environment(cache/'qwen-runtime-state'))
    versions=json.loads(result.stdout)
    return {'engine':'qwen','adapter_sha256':sha(Path(__file__)),'worker_sha256':sha(QWEN_WORKER),
            'python_sha256':sha(python.resolve()),'model':fingerprint,'versions':versions}


def cached_take(take, identity):
    if not take.exists():return False
    if not (take/'receipt.json').is_file():
        failures=take.parent/'failed-attempts';failures.mkdir(exist_ok=True)
        take.rename(failures/(take.name+'-'+str(time.time_ns())))
        return False
    record=json.loads((take/'receipt.json').read_text())
    if record.get('identity')!=identity or record.get('sha256')!=sha(take/'dry.wav'):
        raise ValueError('Corrupt cached take: '+str(take))
    with wave.open(str(take/'dry.wav')) as sound:
        if sound.getsampwidth()!=2 or sound.getnframes()<=0:raise ValueError('Invalid cached PCM take')
    return True


def prepare(spec_path, output, cache):
    spec=json.loads(spec_path.read_text())
    engine,fps,validated=validate_spec(spec)
    if output.exists():raise FileExistsError(output)
    config=settings()
    speech=configured(config,'speech_root') if engine=='kokoro' else None
    if engine=='qwen':runtime=qwen_runtime(config,cache)
    else:runtime=kokoro_runtime(config)
    output.mkdir(parents=True)
    cache.mkdir(parents=True,exist_ok=True)
    cursor=0; cues=[]; blocks=[]; subtitles=[]
    try:
        plans=[]
        for item in validated:
            identity={'spoken':item['spoken'],**item['controls'],'take':item['take'],'runtime':runtime}
            if engine=='qwen':identity['engine']='qwen'
            key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
            take=cache/key
            plans.append({**item,'identity':identity,'key':key,'directory':take,'hit':cached_take(take,identity)})
        missing=list({item['key']:item for item in plans if not item['hit']}.values())
        if engine=='qwen' and missing:
            for item in missing:
                item['directory'].mkdir()
                (item['directory']/'script.txt').write_text(item['spoken'])
            request={'schema':1,'model':str(configured(config,'qwen_model').resolve()),
                     'model_manifest':str(configured(config,'qwen_model_manifest').resolve()),'runtime':runtime,
                     'jobs':[{'directory':str(item['directory'].resolve()),'identity':item['identity']} for item in missing]}
            request_path=output/'qwen-request.json';request_path.write_text(json.dumps(request,indent=2))
            execute([configured(config,'qwen_python'),'-I',QWEN_WORKER,'--request',request_path],output/'qwen-worker.log',timeout=600,
                    env=offline_environment(cache/'qwen-runtime-state'))
            for item in missing:
                if not cached_take(item['directory'],item['identity']):raise ValueError('Qwen worker returned without a complete take')
        for number,item in enumerate(plans,1):
            s=item['segment'];spoken=item['spoken'];substitutions=item['substitutions'];identity=item['identity']
            key=item['key'];take=item['directory'];hit=item['hit']
            if engine=='kokoro' and not hit:hit=cached_take(take,identity)
            if engine=='kokoro' and not hit:
                take.mkdir();(take/'script.txt').write_text(spoken);started=time.perf_counter()
                execute([configured(config,'speech_python'),'-I',speech/'synthesize.py','--text-file',take/'script.txt',
                         '--output',take/'dry.wav','--voice',identity['voice'],'--language',identity['language'],
                         '--speed',identity['speed']],take/'synthesis.log',timeout=180)
                with wave.open(str(take/'dry.wav')) as sound:
                    if sound.getsampwidth()!=2 or sound.getnframes()==0:raise ValueError('Invalid PCM take')
                    duration=sound.getnframes()/sound.getframerate()
                (take/'receipt.json').write_text(json.dumps({'identity':identity,'duration':duration,
                    'sha256':sha(take/'dry.wav'),'elapsed_seconds':time.perf_counter()-started},indent=2))
            dry=output/f'{s["id"]}.dry.wav'
            shutil.copy2(take/'dry.wav',dry)
            mixwav=output/f'{s["id"]}.48k.wav'
            execute(['ffmpeg','-v','error','-n','-i',dry,'-ar','48000','-ac','2','-c:a','pcm_s16le',mixwav],output/f'{s["id"]}.resample.log')
            with wave.open(str(mixwav)) as w:
                pcm=w.readframes(w.getnframes()); samples=w.getnframes(); raw_duration=samples/48000
            pause=item['pause']; minimum=item['minimum']
            if not math.isfinite(pause+minimum) or min(pause,minimum)<0:raise ValueError('Invalid timing')
            frames=max(math.ceil(minimum*fps),math.ceil((raw_duration+pause)*fps))
            target_samples=frames*48000//fps
            blocks.append(pcm+b'\0'*((target_samples-samples)*4))
            cues.append({'id':s['id'],'start_frame':cursor,'end_frame':cursor+frames,
                         'frames':frames,'seconds':frames/fps,'dry_seconds':raw_duration,'spoken':spoken,
                         'text':s['text'],'substitutions':substitutions,'cache_key':key,'cache_hit':hit,
                         'dry_sha256':sha(dry),'take':identity['take']})
            end=min(cursor+frames,cursor+math.ceil(raw_duration*fps))
            subtitles.append(f'{number}\n{stamp(cursor,fps)} --> {stamp(end,fps)}\n{caption_payload(s["text"])}\n')
            cursor+=frames
        with wave.open(str(output/'narration.wav'),'wb') as w:
            w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000)
            for block in blocks:w.writeframes(block)
        with wave.open(str(output/'narration.wav')) as finished:
            if cursor<=0 or finished.getnframes()<=0:
                raise ValueError('Narration must contain positive PCM duration')
        (output/'captions.srt').write_text('\n'.join(subtitles))
        (output/'cues.json').write_text(json.dumps({'fps':fps,'total_frames':cursor,'duration':cursor/fps,
             'alignment':'Measured sentence clips; not word-level forced alignment','segments':cues},indent=2))
        (output/'receipt.json').write_text(json.dumps({'status':'passed','spec_sha256':sha(spec_path),
            'runtime':runtime,'cached_segments':sum(c['cache_hit'] for c in cues),'total_segments':len(cues),
            'wav_sha256':sha(output/'narration.wav'),'frames':cursor,'fps':fps},indent=2))
        return cues
    except Exception as e:
        (output/'failure.json').write_text(json.dumps({'error':str(e),'completed_segments':len(cues)},indent=2))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('spec',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
    a=p.parse_args()
    result=prepare(a.spec.resolve(),a.out.absolute(),a.cache.absolute())
    print(json.dumps({'segments':len(result),'cache_hits':sum(c['cache_hit'] for c in result)},indent=2))
