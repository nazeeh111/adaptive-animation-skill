#!/usr/bin/env python3
"""Inspect aligned opaque 8-bit SDR review copies with local FFmpeg and stdlib.

Select changed pictures, never approve quality. Existing timing is not realigned.
Bounds are deliberately for short review clips; larger jobs use direct review.
"""
import argparse
from fractions import Fraction
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

BOUNDS = {'seconds':60, 'duration_seconds':120, 'frames':7200,
          'pixels_per_frame':1920*1080, 'pixel_frames_each':5_000_000_000,
          'input_bytes_each':1024**3, 'output_bytes':64*1024**2,
          'pair_images':24, 'pair_image_pixels_total':16_000_000}
PIXEL_FORMATS = {'yuv420p','yuvj420p','yuv422p','yuvj422p','yuv444p','yuvj444p',
                'rgb24','bgr24','gbrp','gray'}


class BudgetExhausted(RuntimeError):
    pass


class Job:
    """One deadline and bounded temporary capture for native commands only."""
    def __init__(self, seconds):
        self.started = time.monotonic()
        self.deadline = self.started+seconds
        self.commands = []
        self.output = None
        self.next_size_check = self.started

    def check(self):
        now = time.monotonic()
        if now>=self.deadline:
            raise BudgetExhausted('Total job deadline exhausted')
        if self.output and now>=self.next_size_check:
            self.next_size_check = now+.1
            if sum(p.stat().st_size for p in self.output.iterdir() if p.is_file())>BOUNDS['output_bytes']:
                raise BudgetExhausted('Output byte budget exhausted')

    def run(self, stage, argv, cwd=None):
        self.check()
        entry = {'stage':stage,'argv':[str(x) for x in argv]}
        self.commands.append(entry)
        start = time.monotonic()
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(entry['argv'],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,cwd=cwd)
            try:
                while process.poll() is None:
                    self.check()
                    if stdout.tell()>1024**2 or stderr.tell()>1024**2:
                        raise BudgetExhausted('Native command capture exceeded 1 MiB: '+stage)
                    time.sleep(min(.02,max(0,self.deadline-time.monotonic())))
                self.check()
                if stdout.tell()>1024**2 or stderr.tell()>1024**2:
                    raise BudgetExhausted('Native command capture exceeded 1 MiB: '+stage)
                stdout.seek(0); stderr.seek(0)
                result,error = stdout.read().decode(errors='replace'),stderr.read().decode(errors='replace')
                if process.returncode:
                    raise RuntimeError(stage+': '+error[-6000:])
                return result
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                entry['elapsed_seconds'] = round(time.monotonic()-start,4)
                entry['returncode'] = process.returncode


def identity(path, job):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda:source.read(1024**2),b''):
            job.check()
            digest.update(chunk)
    return {'path':str(path),'bytes':path.stat().st_size,'sha256':digest.hexdigest()}


def probe(tool, path, job):
    if not path.is_file():
        raise ValueError('Input file missing')
    if path.stat().st_size>BOUNDS['input_bytes_each']:
        raise BudgetExhausted('Input exceeds the 1 GiB review-copy limit')
    data = json.loads(job.run('stream preflight',[tool,'-v','error','-show_entries',
        'stream=codec_type,width,height,pix_fmt,color_transfer,time_base,duration_ts,avg_frame_rate:format=duration',
        '-of','json',path]))
    streams = [s for s in data.get('streams',[]) if s.get('codec_type')=='video']
    if len(streams)!=1:
        raise ValueError('Exactly one video stream is required')
    stream = streams[0]
    if stream.get('pix_fmt') not in PIXEL_FORMATS or stream.get('color_transfer') in {'smpte2084','arib-std-b67'}:
        raise ValueError('Use an opaque 8-bit SDR review copy; alpha, high bit depth and HDR are unsupported')
    pixels = stream['width']*stream['height']
    rate = Fraction(stream['avg_frame_rate'])
    duration = float(data.get('format',{}).get('duration',0))
    if not 0<duration<=BOUNDS['duration_seconds'] or not 0<rate<=120:
        raise BudgetExhausted('Review copy needs a known positive duration <=120s and rate <=120fps')
    if pixels>BOUNDS['pixels_per_frame'] or duration*rate>BOUNDS['frames'] or pixels*duration*rate>BOUNDS['pixel_frames_each']:
        raise BudgetExhausted('Review copy exceeds frame/pixel budget')
    return stream


def timing(tool, path, stream, job):
    text = job.run('frame timing',[tool,'-v','error','-select_streams','v:0','-show_frames',
        '-show_entries','frame=best_effort_timestamp,duration','-of','csv=p=0',path])
    scale = Fraction(stream['time_base'])
    frames = []
    for line in text.splitlines():
        job.check()
        if not line.strip():
            continue
        fields = line.split(',')
        if len(fields)<2 or not fields[0].lstrip('-').isdigit() or not fields[1].isdigit():
            raise ValueError('Exact integer frame PTS and duration are required')
        frames.append((int(fields[0])*scale,int(fields[1])*scale))
        if len(frames)>BOUNDS['frames'] or len(frames)*stream['width']*stream['height']>BOUNDS['pixel_frames_each']:
            raise BudgetExhausted('Decoded frame/pixel budget exhausted')
    if not frames or any(b[0]<=a[0] for a,b in zip(frames,frames[1:])) or frames[-1][1]<=0:
        raise ValueError('Missing, non-increasing or incomplete frame timing')
    return frames


def measurements(path, count, pixels, job):
    frames = []
    with path.open() as source:
        for line in source:
            job.check()
            if line.startswith('frame:'):
                frames.append({'frame':int(re.match(r'frame:(\d+)',line)[1])})
                if len(frames)>count:
                    raise ValueError('Unexpected extra comparison frame')
            elif line.startswith('lavfi.bbox.') or line.startswith('lavfi.signalstats.YAVG='):
                key,value = line.strip().split('=',1)
                frames[-1][key] = float(value)
    if len(frames)!=count:
        raise ValueError('Comparison did not measure every decoded frame')
    for frame in frames:
        frame['changed_pixels_approx'] = round(frame['lavfi.signalstats.YAVG']/255*pixels)
    return frames


def write_report(out, report):
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    message = ('No picture differences exceeded the thresholds; this does not establish identity or approval.'
               if report['status']=='no_thresholded_changes' else 'Localized picture differences selected; no quality approval.')
    fields = ['status','fallback','changed_frames','changed_frame_fraction','requested_pair_images',
              'pair_extraction_status','exported_pair_images','bounded_selection_useful','changed_ranges','threshold','limits']
    cards = ''.join(f'<figure><figcaption>Frame {i["frame"]}, {i["seconds"]:.6f}s: baseline left, revision right</figcaption>'
                    f'<img src="{i["image"]}" style="max-width:100%;height:auto"></figure>' for i in report['selected_frames'])
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Changed render frames</title>'
        '<style>body{background:#111;color:#ddd;font:16px system-ui;margin:32px}pre{white-space:pre-wrap}figure{margin:24px 0}</style>'
        '<h1>Changed render frames</h1><p>'+html.escape(report['fallback'] or message)+'</p>'
        '<pre>'+html.escape(json.dumps({k:report.get(k) for k in fields},indent=2))+'</pre>'+cards)


def compare(base, candidate, out, channel_delta, min_pixels, seconds=60):
    if not 0<=channel_delta<=254 or min_pixels<1 or not 0<seconds<=BOUNDS['seconds']:
        raise ValueError('Delta 0..254, positive minimum pixels and total seconds in (0,60] are required')
    if out.exists():
        raise FileExistsError(out)
    ffmpeg,ffprobe = shutil.which('ffmpeg'),shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise RuntimeError('ffmpeg and ffprobe must already be installed')
    job = Job(seconds)
    report = {'schema':2,'purpose':'Select changed pictures for inspection; no quality approval',
        'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'baseline':{'path':str(base)},'candidate':{'path':str(candidate)},'status':'analysis_incomplete',
        'fallback':'','bounds':dict(BOUNDS,total_job_seconds=seconds),'commands':job.commands,
        'threshold':{'rgb_channel_delta_above':channel_delta,'minimum_changed_pixels':min_pixels},
        'selected_frames':[],'requested_pair_images':0,'exported_pair_images':0,
        'pair_extraction_status':'not_started','bounded_selection_useful':False,
        'audio':'Not compared; audio review remains separate',
        'limits':['Comparison domain is opaque 8-bit RGB SDR; not alpha/HDR validation',
                  'Below-threshold edits can be missed; zero differences is not identity or approval',
                  'A baseline can already contain faults','No realignment; integer PTS/time-base and frame durations must match',
                  'Changed pixels do not establish correctness, comprehension, motion or listening quality']}
    try:
        first,second = probe(ffprobe,base,job),probe(ffprobe,candidate,job)
        if (first['width'],first['height'])!=(second['width'],second['height']):
            raise ValueError('Different dimensions: inspect the changed composition directly')
        stamps = timing(ffprobe,base,first,job)
        if stamps!=timing(ffprobe,candidate,second,job):
            raise ValueError('Different frame timestamps/durations/count: inspect the changed edit directly')
        report.update(baseline=identity(base,job),candidate=identity(candidate,job),
            width=first['width'],height=first['height'],decoded_frames_each=len(stamps))
        out.mkdir(parents=True,exist_ok=False)
        job.output = out
        threshold = f'if(gt(val,{channel_delta}),255,0)'
        graph = ("[0:v]format=gbrp[a];[1:v]format=gbrp[b];[a][b]blend=all_mode=difference:shortest=1:repeatlast=0,"
                 f"lutrgb=r='{threshold}':g='{threshold}':b='{threshold}',format=gray,lut=y='if(gt(val,1),255,0)',"
                 "bbox=min_val=1,signalstats,metadata=print:file=per-frame-mask.txt")
        # Fixed metadata name and explicit child cwd keep paths out of filter syntax.
        job.run('picture comparison',[ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-i',base,'-i',candidate,
                                      '-filter_complex',graph,'-an','-f','null','-'],cwd=out)
        measured = measurements(out/'per-frame-mask.txt',len(stamps),first['width']*first['height'],job)
        changed = [f for f in measured if f['changed_pixels_approx']>=min_pixels]
        runs = []
        for frame in changed:
            if not runs or frame['frame']>runs[-1][-1]['frame']+1:
                runs.append([])
            runs[-1].append(frame)
        selected,spans = set(),[]
        for run in runs:
            job.check()
            peak = max(run,key=lambda x:x['changed_pixels_approx'])
            selected.update([run[0]['frame'],peak['frame'],run[-1]['frame'],max(0,run[0]['frame']-1),min(len(stamps)-1,run[-1]['frame']+1)])
            coordinates = [f for f in run if 'lavfi.bbox.x1' in f]
            box = None if not coordinates else {key:int(fn(f['lavfi.bbox.'+key] for f in coordinates))
                for key,fn in [('x1',min),('y1',min),('x2',max),('y2',max)]}
            spans.append({'first_frame':run[0]['frame'],'last_frame':run[-1]['frame'],
                'first_seconds':float(stamps[run[0]['frame']][0]),'last_seconds':float(stamps[run[-1]['frame']][0]),
                'peak_frame':peak['frame'],'peak_changed_pixels_approx':peak['changed_pixels_approx'],'union_bbox_inclusive':box})
        fraction = len(changed)/len(stamps)
        report.update(changed_frames=len(changed),changed_frame_fraction=fraction,changed_ranges=spans,
            maximum_pixels_above_threshold=max(f['changed_pixels_approx'] for f in measured),requested_pair_images=len(selected))
        if fraction>=.5:
            report.update(status='broad_change_no_reduction',pair_extraction_status='skipped_broad_change',
                fallback='Most or all frames changed; no useful time-range reduction. Inspect the original clips directly.')
        elif len(selected)>BOUNDS['pair_images'] or len(selected)*2*first['width']*first['height']>BOUNDS['pair_image_pixels_total']:
            report.update(status='selection_budget_exceeded',pair_extraction_status='skipped_selection_budget',
                fallback='Paired extraction skipped: selection count/pixel budget exceeded. Inspect the original clips directly.')
        elif selected:
            indices = sorted(selected)
            expression = '+'.join(f'eq(n\\,{i})' for i in indices)
            # One decoder per input, one hstack, one image-sequence output.
            job.run('paired extraction',[ffmpeg,'-nostdin','-hide_banner','-loglevel','error','-n','-i',base,'-i',candidate,
                '-filter_complex',f'[0:v]select={expression}[a];[1:v]select={expression}[b];[a][b]hstack,format=rgb24',
                '-frames:v',len(indices),'-fps_mode','passthrough','-start_number','0',out/'pair-%03d.png'])
            images = [{'frame':frame,'seconds':float(stamps[frame][0]),'image':f'pair-{n:03d}.png'} for n,frame in enumerate(indices)]
            if not all((out/i['image']).is_file() for i in images):
                raise ValueError('Incomplete paired extraction')
            report.update(status='localized_changes',selected_frames=images,exported_pair_images=len(images),
                          pair_extraction_status='completed_one_pass',bounded_selection_useful=True)
        else:
            report.update(status='no_thresholded_changes',pair_extraction_status='not_needed',bounded_selection_useful=True)
        job.check()
    except BudgetExhausted as error:
        if not out.exists():
            out.mkdir(parents=True,exist_ok=False)
        report.update(status='budget_exhausted',pair_extraction_status='skipped_or_incomplete_budget',
            bounded_selection_useful=False,selected_frames=[],exported_pair_images=0,
            fallback=str(error)+'. Analysis or extraction is incomplete; inspect the original clips directly. Partial files are not approved pairs.')
    report['elapsed_seconds'] = round(time.monotonic()-job.started,4)
    write_report(out,report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline',type=Path)
    parser.add_argument('candidate',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--channel-delta',type=int,default=12)
    parser.add_argument('--min-pixels',type=int,default=32)
    parser.add_argument('--seconds',type=float,default=60,help='One total deadline, at most 60 seconds')
    args=parser.parse_args()
    report=compare(args.baseline.resolve(strict=True),args.candidate.resolve(strict=True),args.out.absolute(),
                   args.channel_delta,args.min_pixels,args.seconds)
    print(json.dumps({k:report.get(k) for k in ['status','fallback','decoded_frames_each','changed_frames','changed_ranges',
        'requested_pair_images','exported_pair_images','elapsed_seconds']},indent=2))
