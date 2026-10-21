#!/usr/bin/env python3
"""Probe and fully decode one H.264 delivery with configured FFmpeg, no Manim required.

Preserves the original local Manim verifier's codec, streams, duration/rate,
resolution, audio timeline and full-decode checks. Optional duration/frame
contracts use the animation CLI's existing exact-rate and duration semantics.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from config import configured, settings
from processes import run
from studio import absolute, duration, frame_count, require_file, size, verification_rate


def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def inspect_video(path,resolution=None,fps=None,audio=False,expected_duration=None,expected_frames=None):
    path=require_file(absolute(path))
    if path.stat().st_size==0:raise ValueError('Missing/empty video: '+str(path))
    before=digest(path);config=settings()
    probe=require_file(configured(config,'ffprobe'),True)
    ffmpeg=require_file(configured(config,'ffmpeg'),True)
    with tempfile.TemporaryDirectory(prefix='animation-media-verify-') as temporary:
        log=Path(temporary)/'probe.log'
        try:
            info=json.loads(run([probe,'-v','error','-show_streams','-show_format','-of','json',path],log,timeout=60))
            videos=[s for s in info['streams'] if s['codec_type']=='video']
            sounds=[s for s in info['streams'] if s['codec_type']=='audio']
            if len(videos)!=1:raise ValueError('Expected exactly one video stream')
            video=videos[0];seconds=float(video.get('duration',0));rate=Fraction(video['avg_frame_rate'])
            if not math.isfinite(seconds) or seconds<=0 or rate<=0:raise ValueError('Invalid duration or frame rate')
            actual='{}x{}'.format(video['width'],video['height'])
            if resolution and tuple(resolution)!=(video['width'],video['height']):
                raise ValueError('Resolution mismatch: {}, expected {}x{}'.format(actual,*resolution))
            if fps is not None and rate!=fps:raise ValueError('Frame rate mismatch: {}, expected {}'.format(rate,fps))
            if video['codec_name']!='h264':raise ValueError('Unexpected codec: '+video['codec_name'])
            if audio and not sounds:raise ValueError('Expected audio but no audio stream exists')
            video_start=float(video.get('start_time',0))
            if not math.isfinite(video_start):raise ValueError('Invalid video start time')
            for sound in sounds:
                audio_duration=float(sound.get('duration',0));audio_start=float(sound.get('start_time',0))
                if (not math.isfinite(audio_duration) or audio_duration<=0 or not math.isfinite(audio_start)
                        or abs(audio_start-video_start)>.25
                        or abs(audio_start+audio_duration-video_start-seconds)>.25):
                    raise ValueError('Audio/video timeline mismatch: audio={}+{}, video={}+{}'.format(audio_start,audio_duration,video_start,seconds))
            log=Path(temporary)/'decode.log'
            run([ffmpeg,'-nostdin','-v','error','-xerror','-i',path,'-map','0:v:0','-map','0:a?','-f','null','-'],log,timeout=900)
            result={'file':str(path),'bytes':path.stat().st_size,'sha256':before,'resolution':actual,
                    'fps':str(rate),'nominal_fps':video.get('r_frame_rate'),'duration_seconds':seconds,
                    'codec':video['codec_name'],'pixel_format':video.get('pix_fmt'),'audio_streams':len(sounds),
                    'full_decode':'passed','visual_review':'not established by this check',
                    'listening_review':'not established by this check'}
            expected={}
            if fps is not None:
                expected['fps']=str(fps)
                result['frame_rate_check']='Exact average stream rate; not an assertion of constant per-frame timestamps'
            if expected_duration is not None:
                tolerance=.000001
                if abs(seconds-expected_duration)>tolerance:
                    raise ValueError('Duration mismatch: {} seconds, expected {} (tolerance {} seconds)'.format(seconds,expected_duration,tolerance))
                expected['duration_seconds']=expected_duration;result['duration_tolerance_seconds']=tolerance
            if expected_frames is not None:
                log=Path(temporary)/'frames.log'
                counted=json.loads(run([probe,'-v','error','-select_streams','v:0','-count_frames',
                    '-show_entries','stream=nb_read_frames','-of','json',path],log,timeout=900))
                streams=counted.get('streams',[])
                if len(streams)!=1:raise ValueError('Expected exactly one counted video stream')
                try:actual_frames=int(streams[0]['nb_read_frames'])
                except (KeyError,TypeError,ValueError):raise ValueError('FFprobe did not return an actual decoded frame count')
                if actual_frames!=expected_frames:raise ValueError('Frame count mismatch: {}, expected {}'.format(actual_frames,expected_frames))
                expected['video_frames']=expected_frames;result['video_frames']=actual_frames
            if expected:result.update(expected_contract=expected,contract_verification='passed')
        except (RuntimeError,subprocess.TimeoutExpired) as error:
            detail=log.read_text(errors='replace')[-4000:] if log.is_file() else str(error)
            raise ValueError('Media verification command failed:\n'+detail) from error
    if digest(path)!=before:raise ValueError('Source changed during media verification')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path);parser.add_argument('--resolution',type=size)
    parser.add_argument('--fps',type=verification_rate);parser.add_argument('--audio',action='store_true')
    parser.add_argument('--duration',type=duration);parser.add_argument('--frames',type=frame_count)
    args=parser.parse_args(argv)
    try:
        print(json.dumps(inspect_video(args.file,args.resolution,args.fps,args.audio,args.duration,args.frames),indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError,ZeroDivisionError) as error:
        print('animation-media: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
