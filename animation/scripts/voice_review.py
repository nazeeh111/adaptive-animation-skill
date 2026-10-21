#!/usr/bin/env python3
"""Review short generated English phrases for wording coverage, not performance quality.

Uses installed whisper.cpp base.en on CPU. The primary pass never uses VAD or trims
quiet openings. Optional VAD output is a separate diagnostic, not a replacement.
"""
import argparse
from array import array
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
import wave
from processes import run
from studio import absolute, configured, fresh, require_file, settings

# Preserve an existing legacy installation when a private config predates these
# optional settings. Public users configure explicit executable and model paths.
LEGACY_WHISPER_ROOT=Path.home()/'.local/share/codex-tools/whisper-cpp-b4938'


def whisper_path(config,key,relative):
    if config.get(key):
        return configured(config,key)
    legacy=LEGACY_WHISPER_ROOT/relative
    if legacy.is_file() and key not in config:
        return legacy
    raise ValueError('Configure '+key+' in ANIMATION_CONFIG or scripts/local.json')


def sha(path):
    import hashlib
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def words(text):
    normalized=unicodedata.normalize('NFKC',text).casefold().replace('\u2019',"'")
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*",normalized,flags=re.UNICODE)


def align(expected,recognized):
    """Minimum word edits; ties prefer substitution, then deletion, then insertion."""
    a,b=words(expected),words(recognized);rows=len(a)+1;cols=len(b)+1
    dp=[[0]*cols for _ in range(rows)]
    for i in range(rows):dp[i][0]=i
    for j in range(cols):dp[0][j]=j
    for i in range(1,rows):
        for j in range(1,cols):dp[i][j]=min(dp[i-1][j-1]+(a[i-1]!=b[j-1]),dp[i-1][j]+1,dp[i][j-1]+1)
    i,j=len(a),len(b);edits=[]
    while i or j:
        if i and j and dp[i][j]==dp[i-1][j-1]+(a[i-1]!=b[j-1]):
            edits.append({'operation':'equal' if a[i-1]==b[j-1] else 'substitute','expected_index':i-1,'recognized_index':j-1,'expected':a[i-1],'recognized':b[j-1]});i-=1;j-=1
        elif i and dp[i][j]==dp[i-1][j]+1:
            edits.append({'operation':'delete','expected_index':i-1,'recognized_index':None,'expected':a[i-1],'recognized':None});i-=1
        else:
            edits.append({'operation':'insert','expected_index':None,'recognized_index':j-1,'expected':None,'recognized':b[j-1]});j-=1
    edits.reverse();counts={kind:sum(e['operation']==kind for e in edits) for kind in ('equal','substitute','delete','insert')}
    return {'normalization':'Unicode NFKC, casefold, curly apostrophe normalization; punctuation/whitespace separate words; numbers and contractions are not expanded',
            'expected_words':a,'recognized_words':b,'word_edit_distance':dp[-1][-1],
            'word_error_rate':dp[-1][-1]/len(a) if a else None,'counts':counts,'alignment':edits,
            'likely_omitted_words':[e['expected'] for e in edits if e['operation']=='delete'],
            'extra_recognized_words':[e['recognized'] for e in edits if e['operation']=='insert']}


def expected_phrase(expected_file=None,spec_path=None,segment_id=None):
    if expected_file:
        text=Path(expected_file).read_text(encoding='utf-8')
        return {'written_text':None,'spoken_text':text,'source':str(absolute(expected_file)),'pronunciation_substitutions':[]}
    spec=json.loads(Path(spec_path).read_text(encoding='utf-8'))
    if not isinstance(spec,dict) or not isinstance(spec.get('segments'),list):raise ValueError('Narration spec requires a segment list')
    found=[s for s in spec['segments'] if isinstance(s,dict) and s.get('id')==segment_id]
    if len(found)!=1:raise ValueError('Choose exactly one existing narration segment with --segment')
    segment=found[0];written=segment.get('text');spoken=segment.get('spoken',written)
    language=segment.get('language',spec.get('language','English' if spec.get('engine')=='qwen' else 'en-gb'))
    if not isinstance(language,str) or language.casefold() not in ('en','english','en-us','en-gb'):
        raise ValueError('The installed base.en review supports explicitly English phrases only')
    if not isinstance(written,str) or not written.strip() or not isinstance(spoken,str) or not spoken.strip():raise ValueError('Expected written/spoken text must be nonblank')
    substitutions=spec.get('pronunciations',{});changes=[]
    if not isinstance(substitutions,dict):raise ValueError('Pronunciations must be a text mapping')
    for original,replacement in substitutions.items():
        if not isinstance(original,str) or not original or not isinstance(replacement,str):raise ValueError('Invalid pronunciation mapping')
        spoken,count=re.subn(r'(?<!\w)'+re.escape(original)+r'(?!\w)',lambda _:replacement,spoken)
        if count:changes.append({'from':original,'to':replacement,'count':count})
    return {'written_text':written,'spoken_text':spoken,'source':str(absolute(spec_path)),'segment':segment_id,'pronunciation_substitutions':changes}


def energy(path):
    with wave.open(str(path)) as sound:
        if (sound.getframerate(),sound.getnchannels(),sound.getsampwidth())!=(16000,1,2) or sound.getnframes()<=0:
            raise ValueError('Analysis WAV must be nonempty mono16kHz16bit PCM')
        samples=array('h',sound.readframes(sound.getnframes()))
    if sys.byteorder!='little':samples.byteswap()
    rms=math.sqrt(sum(v*v for v in samples)/len(samples))/32768;peak=max(abs(v) for v in samples)/32768
    # Conservative guard against silence/near-silence, not a speech detector or trim.
    sufficient=rms>=.0001 and peak>=.001
    return {'samples':len(samples),'seconds':len(samples)/16000,'rms':rms,'peak':peak,
            'rms_dbfs':20*math.log10(rms) if rms else None,'peak_dbfs':20*math.log10(peak) if peak else None,
            'nonzero_samples':sum(v!=0 for v in samples),'minimum_rms':.0001,'minimum_peak':.001,
            'sufficient_signal':sufficient,'meaning':'Silence/near-silence guard only; energy does not prove speech or transcript correctness'}


def transcribe(input_wav,directory,cli,model,vad_model=None):
    directory.mkdir()
    prefix=directory/'transcript'
    command=[cli,'-m',model,'-f',input_wav,'-l','en','-ng','-t','4','-p','1','-otxt','-ojf','-of',prefix]
    if vad_model is not None:command+=['--vad','--vad-model',vad_model]
    run(command,directory/'whisper.log',timeout=180)
    for suffix in ('.json','.txt'):
        if not Path(str(prefix)+suffix).is_file():raise ValueError('Whisper did not produce its requested actual outputs')
    diagnostic=(directory/'whisper.log').read_text(errors='replace')
    if re.search(r'(?mi)^(?:error:|(?:whisper_[^:\n]+|read_audio_data):[^\n]*(?:failed|error))',diagnostic):raise ValueError('Whisper reported a decoding/model error; inspect whisper.log')
    data=json.loads(Path(str(prefix)+'.json').read_text());segments=data.get('transcription')
    if not isinstance(segments,list) or any(not isinstance(s,dict) or not isinstance(s.get('text'),str) for s in segments):
        raise ValueError('Whisper returned malformed transcription data')
    raw=''.join(s['text'] for s in segments)
    return {'raw_recognized_text':raw,'raw_text_file':Path(str(prefix)+'.txt').read_text(),
            'segments':segments,'command':[str(v) for v in command],'vad_enabled':vad_model is not None,
            'cpu_only':True,'expected_text_prompt_used':False}


def review(audio,out,expected,vad_diagnostic=False):
    audio=require_file(absolute(audio));out=fresh(out)
    spoken=expected['spoken_text']
    if not isinstance(spoken,str) or not words(spoken) or len(words(spoken))>80 or len(spoken)>1000:
        raise ValueError('Review requires a nonblank short English phrase of at most80words/1000characters')
    config=settings();ffmpeg=require_file(configured(config,'ffmpeg'),True);ffprobe=require_file(configured(config,'ffprobe'),True)
    cli=require_file(whisper_path(config,'whisper_cli','bin/whisper-cli'),True);model=require_file(whisper_path(config,'whisper_model','models/ggml-base.en.bin'))
    vad=require_file(whisper_path(config,'whisper_vad_model','models/ggml-silero-v6.2.0.bin')) if vad_diagnostic else None
    original_hash=sha(audio);out.mkdir(parents=True)
    try:
        probe=json.loads(run([ffprobe,'-v','error','-show_format','-show_streams','-of','json',audio],out/'probe.json',timeout=30))
        if not any(s.get('codec_type')=='audio' for s in probe.get('streams',[])):raise ValueError('Input has no actual audio stream')
        duration=float(probe['format']['duration'])
        if not math.isfinite(duration) or not 0<duration<=60:raise ValueError('Short-phrase review requires audio of at most60seconds')
        conversion=[ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-n','-i',audio,'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le',out/'input.wav']
        run(conversion,out/'conversion.log',timeout=60)
        signal=energy(out/'input.wav');primary=transcribe(out/'input.wav',out/'no-vad',cli,model)
        comparison=align(spoken,primary['raw_recognized_text'])
        status='insufficient_signal' if not signal['sufficient_signal'] else ('differences_flagged' if comparison['word_edit_distance'] else 'wording_match')
        result={'schema':1,'review_status':status,'requires_review':status!='wording_match','performance_quality_assessed':False,
                'expected':expected,'primary':primary,'comparison':comparison,'energy':signal,
                'audio':{'source':str(audio),'sha256':original_hash,'analysis_wav_sha256':sha(out/'input.wav'),'source_unchanged':sha(audio)==original_hash},
                'runtime':{'cli':str(cli),'cli_sha256':sha(cli),'model':str(model),'model_sha256':sha(model),'cpu_only':True},
                'analysis_conversion':{'command':[str(v) for v in conversion],'trimmed':False,'sample_rate':16000,'channels':1},
                'quiet_openings':'Entire input converted; no trim, VAD or expected-text prompt in primary pass',
                'limits':['Whisper recognition is fallible. Differences flag likely wording issues for review, not proven generation errors.',
                          'Wording match does not establish pronunciation, emotional compliance, naturalness, speaker identity or a quality winner.',
                          'Energy guard prevents silence/near-silence from matching automatically; it does not detect all nonspeech or hallucination.']}
        if not result['audio']['source_unchanged']:raise ValueError('Source changed during review')
        if vad is not None:
            try:
                diagnostic=transcribe(out/'input.wav',out/'vad-diagnostic',cli,model,vad)
                diagnostic.update(diagnostic_only=True,used_for_primary_status=False,comparison=align(spoken,diagnostic['raw_recognized_text']))
            except Exception as error:
                diagnostic={'diagnostic_only':True,'used_for_primary_status':False,'error':str(error)}
            result['vad_diagnostic']=diagnostic
        with (out/'review.json').open('x') as stream:json.dump(result,stream,indent=2)
        return result
    except Exception as error:
        with (out/'failure.json').open('x') as stream:json.dump({'error':str(error),'source':str(audio),'source_sha256':original_hash},stream,indent=2)
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio',type=Path);parser.add_argument('--out',type=Path,required=True)
    expected=parser.add_mutually_exclusive_group(required=True)
    expected.add_argument('--expected-file',type=Path);expected.add_argument('--spec',type=Path)
    parser.add_argument('--segment');parser.add_argument('--vad-diagnostic',action='store_true')
    args=parser.parse_args(argv)
    if bool(args.spec)!=bool(args.segment):parser.error('--spec and --segment must be supplied together')
    try:
        phrase=expected_phrase(args.expected_file,args.spec,args.segment)
        result=review(args.audio,args.out,phrase,args.vad_diagnostic)
        print(json.dumps({'review_status':result['review_status'],'word_edit_distance':result['comparison']['word_edit_distance'],
                          'sufficient_signal':result['energy']['sufficient_signal'],'report':str(absolute(args.out)/'review.json')},indent=2));return 0
    except (OSError,ValueError,KeyError) as error:
        print('voice-review: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
