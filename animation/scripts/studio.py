#!/usr/bin/env python3
"""Small local studio entry point. Python 3.9+, standard library only."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys

from config import configured, settings

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
ROUTES = ('math', 'motion', '3d', 'voice', 'edit')


def absolute(value):
    return Path(os.path.abspath(os.path.expanduser(str(value))))


def exists(path):
    return os.path.lexists(str(path))


def guard_ancestors(path):
    """Refuse paths that traverse symlinks, including dangling links."""
    path = absolute(path)
    for candidate in (path,) + tuple(path.parents):
        if candidate.is_symlink():
            raise ValueError('Symlink paths are not supported: ' + str(candidate))
    return path


def fresh(path):
    path = guard_ancestors(path)
    if exists(path):
        raise FileExistsError('Choose a new path: ' + str(path))
    return path



def require_file(path, executable=False):
    if not path.is_file() or (executable and not os.access(str(path), os.X_OK)):
        raise ValueError(('Executable' if executable else 'File') + ' missing: ' + str(path))
    return path


def size(value):
    try:
        width, height = (int(x) for x in value.lower().split('x'))
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Use WIDTHxHEIGHT, for example 1920x1080')
    if min(width, height) < 2 or max(width, height) > 8192 or width % 2 or height % 2:
        raise argparse.ArgumentTypeError('Dimensions must be even and between 2 and 8192')
    return width, height


def layer_size(value):
    """Transparent stills/layers can have odd dimensions, unlike H.264 delivery."""
    try:
        width, height = (int(x) for x in value.lower().split('x'))
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Use WIDTHxHEIGHT, for example 1920x1080')
    if min(width, height) < 1 or max(width, height) > 8192:
        raise argparse.ArgumentTypeError('Layer dimensions must be between 1 and 8192')
    return width, height


def fps(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('FPS must be an integer from 1 to 240')
    if not 1 <= number <= 240:
        raise argparse.ArgumentTypeError('FPS must be an integer from 1 to 240')
    return number


def duration(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Duration must be a positive finite number of seconds')
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('Duration must be a positive finite number of seconds')
    return number


def verification_rate(value):
    """Exact output rate; offline capture/init retain their integer contract."""
    try:
        if len(value) > 64:
            raise ValueError('Rate is too long')
        number = Fraction(value)
        if not 1 <= number <= 240:
            raise ValueError('Out of range')
    except (ValueError, ZeroDivisionError, OverflowError):
        raise argparse.ArgumentTypeError('FPS must be a rate from 1 to 240, such as 24 or 30000/1001')
    return number


def frame_count(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Frame count must be a positive integer')
    if number <= 0:
        raise argparse.ArgumentTypeError('Frame count must be a positive integer')
    return number


def files_in(directory, ignore_runtime_artifacts=False):
    """Preflight a complete owned source tree before copying any bytes."""
    directory = guard_ancestors(directory)
    if not directory.is_dir():
        raise ValueError('Source directory missing: ' + str(directory))
    result = []
    for parent, dirs, names in os.walk(str(directory), followlinks=False):
        # Newer HyperFrames stores generated reports/caches here after check.
        # Exclude only this root directory; never follow a link or skip .env.
        if ignore_runtime_artifacts and Path(parent)==directory and '.hyperframes' in dirs:
            cache=directory/'.hyperframes'
            if cache.is_symlink():
                raise ValueError('Symlinks are not allowed in source: .hyperframes')
            dirs.remove('.hyperframes')
        for name in sorted(dirs + names):
            path = Path(parent) / name
            relative = path.relative_to(directory)
            if name.startswith('.') or name == 'node_modules':
                raise ValueError('Hidden files and node_modules are excluded from production snapshots: ' + str(relative))
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError('Symlinks are not allowed in source: ' + str(relative))
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError('Only regular files and directories are supported: ' + str(relative))
            if stat.S_ISREG(mode):
                result.append((path, relative))
    return sorted(result, key=lambda pair: pair[1].as_posix())


def copy_file(source, destination, replacements=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if replacements and source.suffix.lower() in ('.html', '.css', '.js', '.json', '.txt', '.md', '.svg'):
        text = data.decode('utf-8')
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        data = text.encode('utf-8')
    with destination.open('xb') as target:
        target.write(data)


def write_json(path, value):
    with path.open('x', encoding='utf-8') as output:
        json.dump(value, output, indent=2)
        output.write('\n')


def doctor(route):
    try:
        config = settings()
        config_error = None
    except (OSError, ValueError) as error:
        config = {}
        config_error = str(error)
    keys = {'math': ('manim_launcher', 'ffmpeg', 'ffprobe'),
            'motion': ('hyperframes_runner', 'node', 'chrome', 'ffmpeg', 'ffprobe'),
            '3d': ('blender', 'ffmpeg', 'ffprobe'),
            'voice': ('speech_python', 'ffmpeg', 'ffprobe'), 'edit': ()}
    results = {}
    for selected in (ROUTES if route == 'all' else (route,)):
        checks = []
        for key in keys[selected]:
            try:
                path = configured(config, key)
                binary = key in ('blender', 'speech_python', 'node', 'chrome', 'ffmpeg', 'ffprobe')
                ok = path.is_file() and (not binary or os.access(str(path), os.X_OK))
                checks.append({'name': key, 'path': str(path), 'present': ok})
            except ValueError as error:
                checks.append({'name': key, 'present': False, 'error': str(error)})
        if selected in ('motion', 'voice'):
            helper = SCRIPTS / ('hf_screenshot.py' if selected == 'motion' else 'narration.py')
            checks.append({'name': 'bundled_adapter', 'path': str(helper), 'present': helper.is_file()})
        if selected == 'voice':
            try:
                speech_root = configured(config, 'speech_root')
                checks.append({'name': 'speech_root', 'path': str(speech_root), 'present': speech_root.is_dir()})
                for name, relative in (('speech_script', 'synthesize.py'),
                                       ('speech_model', 'models/kokoro-v1.0.onnx'),
                                       ('speech_voices', 'models/voices-v1.0.bin')):
                    asset = speech_root / relative
                    checks.append({'name': name, 'path': str(asset), 'present': asset.is_file()})
            except ValueError as error:
                checks.append({'name': 'speech_root', 'present': False, 'error': str(error)})
        if selected == 'edit':
            codex_home = absolute(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
            skill = codex_home / 'skills/resolve-free-codex/SKILL.md'
            checks.append({'name': 'resolve_skill', 'path': str(skill), 'present': skill.is_file()})
        results[selected] = {'checks': checks, 'presence_checks_passed': all(c['present'] for c in checks),
                             'runtime_proof': False}
        if selected == 'voice':
            optional = []
            for key in ('qwen_python', 'qwen_model', 'qwen_model_manifest'):
                try:
                    path = configured(config, key)
                    ok = path.is_dir() if key == 'qwen_model' else path.is_file()
                    if key == 'qwen_python':
                        ok = ok and os.access(str(path), os.X_OK)
                    optional.append({'name': key, 'path': str(path), 'present': ok})
                except ValueError as error:
                    optional.append({'name': key, 'present': False, 'error': str(error)})
            worker = SCRIPTS / 'qwen_worker.py'
            optional.append({'name': 'qwen_worker', 'path': str(worker), 'present': worker.is_file()})
            results[selected]['optional_engines'] = {'qwen': {
                'checks': optional, 'presence_checks_passed': all(c['present'] for c in optional),
                'runtime_proof': False,
                'note': 'Optional explicit engine; no model load, hashing, GPU synthesis or download performed.'}}
        if selected == 'edit':
            results[selected]['note'] = 'Skill presence only. Live Resolve UI, import/export and Free-edition scripting are not tested.'
    report = {'routes': results, 'note': 'Presence/configuration checks only; no renderer, editor, synthesis or installation was run.'}
    if config_error and route != 'edit':
        report['configuration_error'] = config_error
    print(json.dumps(report, indent=2))
    return 0 if all(r['presence_checks_passed'] for r in results.values()) else 1


def initialize(args):
    project = fresh(args.project)
    brief = args.brief.strip()
    if not brief:
        raise ValueError('Brief must contain text')
    width, height = args.size
    if args.example and args.template != 'motion':
        raise ValueError('--example requires --template motion')
    if args.example and args.duration != 6:
        raise ValueError('The orbit-title example is six seconds; omit --example to author another duration')
    template_files = []
    fonts = []
    if args.template == 'motion':
        template_root = ROOT / ('assets/examples/orbit-title' if args.example else 'assets/motion')
        template_files = files_in(template_root)
        if not any(relative.as_posix() == 'index.html' for _, relative in template_files):
            raise ValueError('Bundled motion template needs index.html')
        if args.example:
            fonts = files_in(ROOT / 'assets/fonts')
        require_file(guard_ancestors(ROOT / 'assets/gsap.min.js'))
    guard_ancestors(project.parent)
    project.mkdir(parents=True, exist_ok=False)
    for folder in ('assets', 'audio', 'renders', 'delivery', 'source'):
        (project / folder).mkdir()
    write_json(project / 'studio.json', {'schema': 1, 'brief': brief, 'width': width,
                                        'height': height, 'fps': args.fps, 'template': args.template,
                                        'duration': args.duration, 'example': args.example})
    with (project / 'PROJECT.md').open('x', encoding='utf-8') as output:
        output.write('# Video project\n\n' + brief + '\n\n'
                     + 'Delivery: {}x{}, {} fps. Planned duration: {} seconds. Template: {}. Example: {}.\n\n'.format(width, height, args.fps, args.duration, args.template, args.example or 'none')
                     + 'Keep editable work in source/, source assets in assets/, narration in audio/, '
                     + 'working exports in renders/, and approved exports in delivery/. Preserve earlier versions.\n')
    if args.template == 'motion':
        composition = project / 'source/motion'
        composition.mkdir()
        replacements = {'@WIDTH@': str(width), '@HEIGHT@': str(height), '@DURATION@': str(args.duration)}
        for source, relative in template_files:
            copy_file(source, composition / relative, replacements)
        for source, relative in fonts:
            copy_file(source, composition / 'assets' / relative)
        copy_file(ROOT / 'assets/gsap.min.js', composition / 'assets/gsap.min.js')
    print(json.dumps({'project': str(project), 'template': args.template, 'example': args.example, 'duration': args.duration, 'created': True}, indent=2))
    return 0


def execute(script, arguments):
    require_file(script)
    os.execve(sys.executable, [sys.executable, str(script)] + [str(a) for a in arguments], dict(os.environ))


def render_motion(args):
    project = guard_ancestors(args.project)
    source = project / 'source/motion'
    source_files = files_in(source, ignore_runtime_artifacts=True)
    require_file(source / 'index.html')
    config = json.loads((project / 'studio.json').read_text(encoding='utf-8'))
    frame_rate = fps(str(config['fps']))
    adapter = require_file(SCRIPTS / 'hf_screenshot.py')
    output = fresh(args.output)
    if not output.parent.is_dir():
        raise ValueError('Output parent must already exist: ' + str(output.parent))
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError('Render output cannot be inside source/motion')
    renders = guard_ancestors(project / 'renders')
    if not renders.is_dir():
        raise ValueError('Project renders directory missing: ' + str(renders))
    snapshot = fresh(renders / (output.stem + '.source'))
    manifest = fresh(renders / (output.stem + '.source-manifest.json'))
    snapshot.mkdir(exist_ok=False)
    entries = []
    for original, relative in source_files:
        copied = snapshot / relative
        copy_file(original, copied)
        data = copied.read_bytes()
        entries.append({'path': relative.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    write_json(manifest, {'schema': 1, 'source': str(source), 'snapshot': str(snapshot),
                          'output': str(output), 'fps': frame_rate, 'quality': args.quality,
                          'excluded_runtime_artifacts': ['.hyperframes/'] if (source/'.hyperframes').is_dir() else [],
                          'files': entries})
    print(json.dumps({'snapshot': str(snapshot), 'manifest': str(manifest), 'output': str(output)}, indent=2), flush=True)
    execute(adapter, ['render', snapshot, '--output', output, '--fps', frame_rate,
                      '--quality', args.quality, '--workers', '1'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('doctor', help='Selected path/config checks; never renders or installs')
    check.add_argument('--route', choices=ROUTES + ('all',), default='all')
    init = commands.add_parser('init', help='Create a new editable project')
    init.add_argument('project', type=Path)
    init.add_argument('--brief', required=True)
    init.add_argument('--size', type=size, default=(1920, 1080))
    init.add_argument('--fps', type=fps, default=30)
    init.add_argument('--template', choices=('motion', 'empty'), default='empty',
                      help='Empty workspace (default), or unstyled browser capture scaffold')
    init.add_argument('--duration', type=duration, default=6,
                      help='Planned motion duration in seconds; author scene timing for the brief')
    init.add_argument('--example', choices=('orbit-title',),
                      help='Explicitly copy an authored study; requires --template motion')
    motion = commands.add_parser('render-motion', help='Snapshot only motion source and invoke its local renderer')
    motion.add_argument('project', type=Path)
    motion.add_argument('--output', type=Path, required=True)
    motion.add_argument('--quality', choices=('standard', 'high', 'draft'), default='standard')
    verify = commands.add_parser('verify', help='Probe and fully decode H.264 media with configured FFmpeg')
    verify.add_argument('file', type=Path)
    verify.add_argument('--resolution', type=size)
    verify.add_argument('--fps', type=verification_rate)
    verify.add_argument('--audio', action='store_true')
    verify.add_argument('--duration', type=duration, help='Expected video duration in seconds; tolerance 0.000001 s')
    verify.add_argument('--frames', type=frame_count, help='Expected decoded video frame count; adds a CPU frame-count pass')
    layer = commands.add_parser('verify-layer', help='Decode one transparent still/movie and check its alpha plane')
    layer.add_argument('file', type=Path)
    layer.add_argument('--resolution', type=layer_size)
    layer.add_argument('--codec')
    layer.add_argument('--fps', type=verification_rate)
    layer.add_argument('--duration', type=duration)
    layer.add_argument('--frames', type=frame_count)
    layer.add_argument('--alpha-content', choices=('present', 'nontrivial'), default='nontrivial')
    layer.add_argument('--alpha-mode', choices=('straight', 'premultiplied', 'unspecified'), default='unspecified')
    layer.add_argument('--max-bytes', type=frame_count, default=4*1024**3)
    pack = commands.add_parser('pack-sources', help='Bundle explicitly selected native sources without overwriting')
    pack.add_argument('manifest', type=Path)
    pack.add_argument('--output', type=Path, required=True)
    pack.add_argument('--max-bytes', type=frame_count)
    recover = commands.add_parser('recover-sources', help='Validate a source bundle and recover to a fresh directory')
    recover.add_argument('archive', type=Path)
    recover.add_argument('--out', type=Path, required=True)
    recover.add_argument('--max-bytes', type=frame_count)
    narration = commands.add_parser('narrate', help='Prepare measured cached local sentence takes')
    narration.add_argument('spec', type=Path)
    narration.add_argument('--out', type=Path, required=True)
    narration.add_argument('--cache', type=Path, required=True)
    voice_review = commands.add_parser('review-voice', help='Review short English spoken-word coverage on CPU; no quality ranking')
    voice_review.add_argument('audio', type=Path)
    voice_review.add_argument('--out', type=Path, required=True)
    expected = voice_review.add_mutually_exclusive_group(required=True)
    expected.add_argument('--expected-file', type=Path)
    expected.add_argument('--spec', type=Path)
    voice_review.add_argument('--segment')
    voice_review.add_argument('--vad-diagnostic', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'doctor':
            return doctor(args.route)
        if args.command == 'init':
            return initialize(args)
        if args.command == 'render-motion':
            render_motion(args)
        elif args.command == 'verify':
            arguments = [require_file(absolute(args.file))]
            if args.resolution:
                arguments += ['--resolution', '{}x{}'.format(*args.resolution)]
            if args.fps is not None:
                arguments += ['--fps', str(args.fps)]
            if args.audio:
                arguments += ['--audio']
            if args.duration is not None:
                arguments += ['--duration', args.duration]
            if args.frames is not None:
                arguments += ['--frames', args.frames]
            execute(SCRIPTS / 'media_verify.py', arguments)
        elif args.command == 'verify-layer':
            arguments = [args.file, '--alpha-content', args.alpha_content,
                         '--alpha-mode', args.alpha_mode, '--max-bytes', args.max_bytes]
            if args.resolution:
                arguments += ['--resolution', '{}x{}'.format(*args.resolution)]
            for option in ('codec', 'fps', 'duration', 'frames'):
                value = getattr(args, option)
                if value is not None:
                    arguments += ['--' + option, value]
            execute(SCRIPTS / 'layers.py', arguments)
        elif args.command in ('pack-sources', 'recover-sources'):
            if args.command == 'pack-sources':
                arguments = ['pack', args.manifest, '--output', args.output]
            else:
                arguments = ['recover', args.archive, '--out', args.out]
            if args.max_bytes is not None:
                arguments += ['--max-bytes', args.max_bytes]
            execute(SCRIPTS / 'sources.py', arguments)
        elif args.command == 'review-voice':
            if bool(args.spec) != bool(args.segment):
                raise ValueError('--spec and --segment must be supplied together')
            arguments = [require_file(absolute(args.audio)), '--out', fresh(args.out)]
            if args.expected_file:
                arguments += ['--expected-file', require_file(absolute(args.expected_file))]
            else:
                arguments += ['--spec', require_file(absolute(args.spec)), '--segment', args.segment]
            if args.vad_diagnostic:
                arguments += ['--vad-diagnostic']
            execute(SCRIPTS / 'voice_review.py', arguments)
        elif args.command == 'narrate':
            execute(SCRIPTS / 'narration.py', [require_file(absolute(args.spec)), '--out',
                                             fresh(args.out), '--cache', guard_ancestors(args.cache)])
        return 0
    except (OSError, ValueError, KeyError) as error:
        print('studio: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
