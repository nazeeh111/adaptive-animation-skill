#!/usr/bin/env python3
"""Compose the two original four-second examples into a small README GIF."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path,help='New GIF path; parent must exist')
    parser.add_argument('--ffmpeg',default='ffmpeg',help='Existing FFmpeg executable or PATH name')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    output=args.output.expanduser().absolute()
    if os.path.lexists(output) or not output.parent.is_dir():
        parser.error('Choose a new output path with an existing parent')
    executable=shutil.which(args.ffmpeg)
    if not executable:
        parser.error('FFmpeg is required; no tool is installed automatically')
    inputs=[root/'examples/ink-study/ink-study.mp4',root/'examples/power-cell/power-cell.mp4']
    if not all(p.is_file() for p in inputs):
        parser.error('Run from a checkout containing both selected example movies')
    filters=(
        '[0:v]fps=12,scale=360:450:flags=lanczos,'
        'pad=1040:520:12:35:color=0x0c151b[base];'
        '[1:v]fps=12,scale=640:360:flags=neighbor[pixel];'
        '[base][pixel]overlay=388:80:shortest=1,split[a][b];'
        '[a]palettegen=max_colors=128:stats_mode=diff[p];'
        '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle'
    )
    command=[executable,'-n','-v','error','-i',str(inputs[0]),'-i',str(inputs[1]),
             '-filter_complex',filters,'-t','4','-loop','0',str(output)]
    subprocess.run(command,check=True,timeout=120)
    print('Created '+str(output))


if __name__=='__main__':
    main()
