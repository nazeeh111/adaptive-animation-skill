"""Bounded owned process groups for local production commands, with durable logs."""
import os
from pathlib import Path
import signal
import subprocess
import time

from config import configured, settings


def run(argv,log,timeout=900,env=None):
    argv=[str(a) for a in argv];log=Path(log)
    # Codex's initialized PATH can differ after a turn resumes. Scope the known
    # local media binary directory to this child, preserving all other settings.
    child_environment=dict(os.environ if env is None else env)
    config=settings()
    media_paths=[]
    for key in ('ffmpeg','ffprobe'):
        if config.get(key):
            binary=configured(config,key)
            if binary.is_file() and os.access(str(binary),os.X_OK) and str(binary.parent) not in media_paths:
                media_paths.append(str(binary.parent))
    if media_paths:
        child_environment['PATH']=os.pathsep.join(media_paths+[child_environment.get('PATH',os.defpath)])
    interrupted=[];process=None
    previous={s:signal.getsignal(s) for s in (signal.SIGINT,signal.SIGTERM)}
    def handle(signum,frame):
        interrupted.append(signum)
    def send(signum):
        if process is not None:
            try:
                os.killpg(process.pid,signum)
                return True
            except ProcessLookupError:return False
        return False
    def cleanup():
        if not send(signal.SIGTERM):return
        deadline=time.monotonic()+2
        try:process.wait(timeout=2)
        except subprocess.TimeoutExpired:pass
        # The leader may exit before descendants finish; retain their grace period.
        remaining=deadline-time.monotonic()
        if remaining>0:time.sleep(remaining)
        send(signal.SIGKILL)
        if process.poll() is None:process.wait()
    started=time.monotonic()
    try:
        for s in previous:signal.signal(s,handle)
        with log.open('wb') as output:
            process=subprocess.Popen(argv,stdout=output,stderr=subprocess.STDOUT,
                                     env=child_environment,start_new_session=True)
            while process.poll() is None:
                if interrupted or time.monotonic()-started>timeout:
                    cleanup()
                    if interrupted:
                        output.write(f'\nCancelled by signal{interrupted[0]}.\n'.encode());output.flush()
                        raise InterruptedError(f'Cancelled; logs retained at {log}')
                    output.write(f'\nTimed out after{timeout} seconds.\n'.encode());output.flush()
                    raise subprocess.TimeoutExpired(argv,timeout)
                time.sleep(.05)
            code=process.wait()
            # Render/synthesis commands should not leave workers after leader exit.
            cleanup()
        if code:raise RuntimeError(f'Command failed({code}); see {log}')
        return log.read_text(errors='replace')
    finally:
        if process is not None and process.poll() is None:cleanup()
        for s,handler in previous.items():signal.signal(s,handler)
