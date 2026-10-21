#!/usr/bin/env python3
"""One offline Qwen CustomVoice model for a validated batch of missing sentence takes.

--inspect-runtime reads distribution metadata only: it never imports MLX or loads weights.
The parent owns the600second process-group deadline through processes.run.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import sys
import time
import wave

sys.dont_write_bytecode=True
PACKAGES=('mlx-audio','mlx','mlx-metal','numpy','transformers','tokenizers','safetensors','huggingface-hub')


def runtime_versions():
    return {'python':sys.version.split()[0],
            'packages':{name:importlib.metadata.version(name) for name in PACKAGES}}


def no_network(event, args):
    if event in ('socket.connect','socket.getaddrinfo','urllib.Request','http.client.connect'):
        raise RuntimeError('Qwen worker networking is disabled; only existing local assets may be used')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--inspect-runtime',action='store_true')
    group.add_argument('--request',type=Path)
    args=parser.parse_args()
    if args.inspect_runtime:
        print(json.dumps(runtime_versions(),sort_keys=True));return
    sys.addaudithook(no_network)
    for key in ('HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_HUB_DISABLE_TELEMETRY'):
        if os.environ.get(key)!='1':raise ValueError('Offline worker environment is required')
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from narration import qwen_controls, sha, verify_qwen_model
    request=json.loads(args.request.read_text())
    if request.get('schema')!=1 or not isinstance(request.get('jobs'),list) or not request['jobs']:
        raise ValueError('Qwen request requires a nonempty validated job batch')
    runtime=request['runtime']
    if runtime['worker_sha256']!=sha(Path(__file__)) or runtime['adapter_sha256']!=sha(Path(__file__).parent/'narration.py'):
        raise ValueError('Qwen worker/adapter changed after request creation')
    if runtime['versions']!=runtime_versions():raise ValueError('Qwen runtime versions changed')
    if runtime['python_sha256']!=sha(Path(sys.executable).resolve()):raise ValueError('Qwen interpreter changed')
    if runtime['model']!=verify_qwen_model(Path(request['model']),Path(request['model_manifest'])):
        raise ValueError('Qwen local model changed after request creation')
    jobs=[];seen=set()
    for job in request['jobs']:
        identity=job['identity'];directory=Path(job['directory'])
        expected={'engine','spoken','voice','language','instruct','seed','temperature','max_tokens','take','runtime'}
        if set(identity)!=expected or identity['engine']!='qwen' or identity['runtime']!=runtime:
            raise ValueError('Unsupported Qwen job identity')
        controls=qwen_controls({},identity,identity['spoken'])
        if any(identity[name]!=value for name,value in controls.items()):raise ValueError('Noncanonical Qwen controls')
        if not isinstance(identity['take'],str) or not identity['take'].strip():raise ValueError('Invalid take')
        key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        if not directory.is_absolute() or directory.name!=key or directory.is_symlink() or not directory.is_dir() or str(directory) in seen:
            raise ValueError('Invalid or duplicate Qwen cache destination')
        if any((directory/name).exists() for name in ('dry.wav','dry.wav.partial','receipt.json')):
            raise FileExistsError('Qwen output already exists')
        seen.add(str(directory));jobs.append((directory,identity))
    # All model files, job controls and output destinations validate before any MLX import.
    import numpy as np
    import mlx.core as mx
    from mlx_audio.tts.utils import load_model
    began=time.monotonic();model=load_model(str(Path(request['model']).resolve()));mx.eval(model.parameters())
    if model.tokenizer is None or model.speech_tokenizer is None:raise RuntimeError('Required local tokenizer missing')
    load_seconds=time.monotonic()-began
    print(json.dumps({'model_loaded_once':True,'missing_takes':len(jobs),'load_seconds':load_seconds}),flush=True)
    for directory,identity in jobs:
        mx.random.seed(identity['seed']);mx.reset_peak_memory();started=time.monotonic();parts=[];tokens=0
        for result in model.generate_custom_voice(text=identity['spoken'],speaker=identity['voice'],language=identity['language'],
                instruct=identity['instruct'],temperature=identity['temperature'],max_tokens=identity['max_tokens'],
                top_k=50,top_p=1.0,repetition_penalty=1.05,verbose=False,stream=False):
            if int(result.sample_rate)!=24000:raise RuntimeError('Qwen sample rate must be24000Hz')
            audio=np.asarray(result.audio,dtype=np.float32).reshape(-1)
            if not len(audio) or not np.isfinite(audio).all():raise RuntimeError('Qwen returned invalid or empty audio')
            parts.append(audio);tokens+=int(result.token_count)
        if not parts:raise RuntimeError('Qwen returned no audio')
        audio=np.concatenate(parts);peak=float(np.max(np.abs(audio)))
        if peak<=0 or tokens<=0 or tokens>=identity['max_tokens']:raise RuntimeError('Qwen silence or token limit reached; take not accepted')
        if len(audio)>24000*45:raise RuntimeError('Qwen short take exceeds45seconds; take not accepted')
        gain=min(1.0,.999/peak);pcm=np.rint(audio*gain*32767).astype('<i2')
        partial=directory/'dry.wav.partial';target=directory/'dry.wav'
        with partial.open('xb') as raw:
            with wave.open(raw,'wb') as sound:
                sound.setnchannels(1);sound.setsampwidth(2);sound.setframerate(24000);sound.writeframes(pcm.tobytes())
        os.link(partial,target);partial.unlink()
        record={'identity':identity,'duration':len(pcm)/24000,'sha256':sha(target),
                'elapsed_seconds':time.monotonic()-started,'generation':{'token_count':tokens,'gain':gain,'raw_peak':peak,
                'pcm_peak':float(np.max(np.abs(pcm.astype(np.int32))))/32768,
                'mlx_peak_allocator_bytes':int(mx.get_peak_memory()),
                'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
        with (directory/'receipt.json').open('x') as output:json.dump(record,output,indent=2)
        print(json.dumps({'cache_key':directory.name,'seconds':record['duration'],'token_count':tokens}),flush=True)
    print(json.dumps({'complete':True,'model_loads':1,'generated_takes':len(jobs)}),flush=True)


if __name__=='__main__':main()
