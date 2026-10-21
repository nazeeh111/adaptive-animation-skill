#!/usr/bin/env python3
"""Decode and check one transparent still/movie layer. Python 3.9+, stdlib only.

This checks decoded alpha values, not a color transform, alpha association,
interchange editability or perceptual correctness. The opaque H.264 route stays
separate. Image-sequence completeness is not inferred from a single file.
"""
import argparse
import array
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from studio import (guard_ancestors, require_file, settings, configured, layer_size,
                    verification_rate, duration, frame_count)
from processes import run


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def verify(args):
    path=require_file(guard_ancestors(args.file))
    source_sha=sha(path)
    config=settings()
    probe=require_file(configured(config,'ffprobe'),True)
    ffmpeg=require_file(configured(config,'ffmpeg'),True)
    with tempfile.TemporaryDirectory(prefix='animation-layer-') as temporary:
        temporary=Path(temporary)
        log=temporary/'probe.log'
        try:
            info=json.loads(run([probe,'-v','error','-show_streams','-show_format','-of','json',path],log,timeout=60))
            videos=[s for s in info.get('streams',[]) if s.get('codec_type')=='video']
            if len(videos)!=1:raise ValueError('Expected exactly one video/image stream')
            video=videos[0];width=int(video['width']);height=int(video['height'])
            if min(width,height)<1 or max(width,height)>8192:raise ValueError('Unsupported layer dimensions')
            if args.resolution and (width,height)!=args.resolution:raise ValueError('Layer resolution mismatch')
            if args.codec and video.get('codec_name')!=args.codec:raise ValueError('Layer codec mismatch')
            raw_rate=video.get('avg_frame_rate','0/0')
            try:rate=Fraction(raw_rate)
            except (ValueError,ZeroDivisionError):rate=None
            if args.fps is not None and rate!=args.fps:raise ValueError('Layer average frame rate mismatch')
            try:seconds=float(video['duration'])
            except (ValueError,TypeError,KeyError):seconds=None
            if seconds is not None and (not math.isfinite(seconds) or seconds<=0):raise ValueError('Invalid layer duration')
            if args.duration is not None and (seconds is None or abs(seconds-args.duration)>.000001):
                raise ValueError('Layer duration mismatch')
            # Alpha extraction requires an actual decoded alpha plane. Merely
            # tagged VP9 alpha, or an opaque codec with no plane, cannot pass.
            raw=temporary/'alpha.raw';log=temporary/'decode.log'
            run([ffmpeg,'-hide_banner','-v','error','-xerror','-nostdin','-n','-i',path,
                 '-map','0:v:0','-an','-vf','alphaextract','-pix_fmt','gray16le',
                 '-fps_mode','passthrough','-f','rawvideo','-fs',args.max_bytes+2,raw],log,timeout=900)
            count=raw.stat().st_size
            if count>args.max_bytes:raise ValueError('Decoded alpha exceeds scratch byte budget')
            per_frame=width*height*2
            if count==0 or count%per_frame:raise ValueError('Incomplete decoded alpha frames')
            frames=count//per_frame
            if args.frames is not None and frames!=args.frames:raise ValueError('Layer decoded frame count mismatch')
            low=65535;high=0;zeros=opaque=total=0
            with raw.open('rb') as source:
                for block in iter(lambda:source.read(256*1024),b''):
                    samples=array.array('H');samples.frombytes(block)
                    if sys.byteorder!='little':samples.byteswap()
                    low=min(low,min(samples));high=max(high,max(samples))
                    zeros+=samples.count(0);opaque+=samples.count(65535);total+=len(samples)
            if args.alpha_content=='nontrivial' and not (low<high and low<65535 and high>0):
                raise ValueError('Expected nontrivial transparent layer content; decoded alpha is constant/empty')
        except (RuntimeError,subprocess.TimeoutExpired) as error:
            detail=log.read_text(errors='replace')[-4000:] if log.is_file() else str(error)
            raise ValueError('Layer inspection/decode failed:\n'+detail) from error
    if sha(path)!=source_sha:raise ValueError('Source changed during layer verification')
    return {'file':str(path),'sha256':source_sha,'bytes':path.stat().st_size,
            'resolution':'{}x{}'.format(width,height),'codec':video.get('codec_name'),
            'source_pixel_format':video.get('pix_fmt'),'average_fps':str(rate) if rate is not None else None,
            'duration_seconds':seconds,'decoded_frames':frames,'video_and_alpha_decode':'passed',
            'alpha':{'decoded_format':'gray16le','minimum':low,'maximum':high,
                     'transparent_samples':zeros,'opaque_samples':opaque,
                     'intermediate_samples':total-zeros-opaque,'total_samples':total,
                     'required_content':args.alpha_content},
            'declared_alpha_mode':args.alpha_mode,
            'reported_color_tags':{k:video.get(k) for k in ['color_range','color_space','color_transfer','color_primaries']},
            'expected_contract':{'resolution':list(args.resolution) if args.resolution else None,
                                 'codec':args.codec,'fps':str(args.fps) if args.fps is not None else None,
                                 'duration_seconds':args.duration,'decoded_frames':args.frames},
            'contract_verification':'passed',
            'max_decoded_alpha_bytes':args.max_bytes,
            'limits':'Decoded unsigned16 alpha-plane evidence only. Alpha mode is caller-declared; color tags are source-reported. Does not establish premultiplication/color correctness, float/HDR channel validity, constant timestamps, sequence completeness, audio, receiver fidelity, visual craft or listening.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    parser.add_argument('--resolution',type=layer_size)
    parser.add_argument('--codec')
    parser.add_argument('--fps',type=verification_rate)
    parser.add_argument('--duration',type=duration)
    parser.add_argument('--frames',type=frame_count)
    parser.add_argument('--alpha-content',choices=('present','nontrivial'),default='nontrivial')
    parser.add_argument('--alpha-mode',choices=('straight','premultiplied','unspecified'),default='unspecified')
    parser.add_argument('--max-bytes',type=frame_count,default=4*1024**3,
                        help='Decoded alpha scratch budget in bytes, default 4 GiB')
    args=parser.parse_args(argv)
    try:print(json.dumps(verify(args),indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        print('animation-layer: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
