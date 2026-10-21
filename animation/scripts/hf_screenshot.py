"""Use the existing safe HF runner with its documented screenshot opt-out.

No installed file is edited. The original runner still enforces output/no-download
and process ownership contracts; only its sanitized child environment is extended.
"""
import importlib.util
import sys
import os
from pathlib import Path
from config import configured, settings
config=settings()
paths=[]
for key in ('ffmpeg','ffprobe','node'):
    binary=configured(config,key)
    if not binary.is_file() or not os.access(binary,os.X_OK):
        raise SystemExit('Configured executable missing: '+str(binary))
    if str(binary.parent) not in paths: paths.append(str(binary.parent))
os.environ['PATH']=os.pathsep.join(paths+[os.environ.get('PATH',os.defpath)])
p=configured(config,'hyperframes_runner')
spec=importlib.util.spec_from_file_location('studio_existing_hf_runner',p)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.CHROME=configured(config,'chrome')
original_environment=module.environment
def environment():
    env=original_environment()
    env['PRODUCER_EXPERIMENTAL_FAST_CAPTURE']='false'
    env['PRODUCER_FORCE_SCREENSHOT']='true'
    return env
module.environment=environment
print('Matched capture profile: PRODUCER_EXPERIMENTAL_FAST_CAPTURE=false; PRODUCER_FORCE_SCREENSHOT=true',flush=True)
sys.exit(module.main())
