#!/usr/bin/env python3
"""Explicit selected-source bundles and byte-verified recovery. Python 3.9+."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import unicodedata
import zipfile
import zlib

META = '.animation-bundle/manifest.json'
RESERVED = '.animation-bundle'
DEFAULT_MAX_BYTES = 4 * 1024 ** 3
MAX_METADATA_BYTES = 8 * 1024 ** 2
MAX_FILES = 100000
CHUNK = 1024 ** 2
SHA = re.compile(r'^[0-9a-f]{64}$')


def positive(value):
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValueError('Byte budget must be a positive integer')
    if isinstance(value, bool) or result <= 0 or str(result) != str(value):
        raise ValueError('Byte budget must be a positive integer')
    return result


def relative(value, metadata=False):
    if not isinstance(value, str) or not value or '\\' in value or any(ord(c) < 32 for c in value):
        raise ValueError('Expected a nonempty safe relative POSIX file path')
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or str(path) != value or '..' in path.parts or ':' in path.parts[0]:
        raise ValueError('Unsafe or noncanonical relative path: ' + value)
    if unicodedata.normalize('NFC', path.parts[0]).casefold() == RESERVED and not (metadata and value == META):
        raise ValueError('Reserved bundle metadata path: ' + value)
    return value


def validate_tree(names):
    """Reject aliases and file/parent collisions before writing on this Mac."""
    keys = {}
    for name in names:
        key = unicodedata.normalize('NFC', name).casefold()
        if key in keys:
            raise ValueError('Case/Unicode path collision: {} and {}'.format(keys[key], name))
        keys[key] = name
    for key, name in keys.items():
        if any(str(parent) in keys for parent in PurePosixPath(key).parents if str(parent) != '.'):
            raise ValueError('File/directory path collision: ' + name)


def guarded(value):
    path = Path(os.path.abspath(os.path.expanduser(str(value))))
    for part in (path,) + tuple(path.parents):
        if part.is_symlink():
            raise ValueError('Symlink path is not supported: ' + str(part))
    return path


def fresh(value):
    path = guarded(value)
    if os.path.lexists(str(path)):
        raise FileExistsError('Choose a new destination: ' + str(path))
    if not path.parent.is_dir():
        raise ValueError('Destination parent must already exist: ' + str(path.parent))
    return path


def open_regular(path):
    guarded(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Expected a regular file: ' + str(path))
    descriptor = os.open(str(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Expected a regular file: ' + str(path))
        return os.fdopen(descriptor, 'rb')
    except BaseException:
        os.close(descriptor)
        raise


def file_hash(path, max_bytes):
    digest = hashlib.sha256()
    total = 0
    with open_regular(path) as source:
        info = os.fstat(source.fileno())
        if info.st_size > max_bytes:
            raise ValueError('File exceeds remaining byte budget: ' + str(path))
        while True:
            data = source.read(CHUNK)
            if not data:
                break
            total += len(data)
            if total > max_bytes:
                raise ValueError('File exceeds remaining byte budget: ' + str(path))
            digest.update(data)
    return total, digest.hexdigest(), stat.S_IMODE(info.st_mode) & 0o777


def read_json_file(path):
    with open_regular(path) as source:
        raw = source.read(MAX_METADATA_BYTES + 1)
    if len(raw) > MAX_METADATA_BYTES:
        raise ValueError('Manifest exceeds 8 MiB metadata limit')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('Manifest must be a JSON object')
    return value


def selected_manifest(path, max_bytes):
    path = guarded(path)
    value = read_json_file(path)
    root_value = value.get('root', '.')
    if not isinstance(root_value, str) or not root_value:
        raise ValueError('Manifest root must be a path string')
    root = Path(root_value).expanduser()
    root = guarded(root if root.is_absolute() else path.parent / root)
    if not root.is_dir():
        raise ValueError('Manifest root is not a directory: ' + str(root))
    maximum = max_bytes if max_bytes is not None else positive(value.get('max_uncompressed_bytes', DEFAULT_MAX_BYTES))
    entries = value.get('files')
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_FILES:
        raise ValueError('Manifest files must be a nonempty list of at most 100000 selected files')
    external = value.get('external_dependencies', [])
    if not isinstance(external, list):
        raise ValueError('external_dependencies must be a JSON list of declarations')
    files, seen, used = [], set(), 0
    for entry in entries:
        if isinstance(entry, str):
            name, expected = relative(entry), None
        elif isinstance(entry, dict) and set(entry) <= {'path', 'sha256'}:
            name, expected = relative(entry.get('path')), entry.get('sha256')
            if expected is not None and (not isinstance(expected, str) or not SHA.fullmatch(expected)):
                raise ValueError('Expected sha256 must be 64 lowercase hexadecimal characters: ' + name)
        else:
            raise ValueError('Each selected file must be a path or {path, sha256} object')
        if name in seen:
            raise ValueError('Duplicate selected file: ' + name)
        seen.add(name)
        size, digest, mode = file_hash(root / name, maximum - used)
        used += size
        if expected is not None and expected != digest:
            raise ValueError('Selected source SHA256 mismatch: ' + name)
        files.append({'path': name, 'bytes': size, 'sha256': digest, 'mode': mode})
    validate_tree(seen)
    metadata = {'schema': 1, 'kind': 'animation-selected-sources', 'files': sorted(files, key=lambda x: x['path']),
                'external_dependencies': external,
                'limits': 'Only explicitly selected files. No automatic dependency discovery, native relinking, runtime installation or rerender is established.'}
    raw = (json.dumps(metadata, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    if len(raw) > MAX_METADATA_BYTES or used + len(raw) > maximum:
        raise ValueError('Bundle exceeds metadata limit or declared uncompressed byte budget')
    return root, metadata, raw, maximum


def zip_info(name, mode):
    info = zipfile.ZipInfo(name)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def pack(manifest, output, max_bytes=None):
    output = fresh(output)
    root, metadata, raw, maximum = selected_manifest(manifest, max_bytes)
    if any(root / item['path'] == output for item in metadata['files']):
        raise ValueError('Output cannot be a selected source')
    descriptor, temporary_name = tempfile.mkstemp(prefix='.animation-bundle-', suffix='.zip', dir=str(output.parent))
    temporary = Path(temporary_name)
    identity = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, 'w+b') as target:
            with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                archive.writestr(zip_info(META, 0o644), raw)
                for item in metadata['files']:
                    digest, count = hashlib.sha256(), 0
                    with open_regular(root / item['path']) as source, archive.open(zip_info(item['path'], item['mode']), 'w', force_zip64=True) as destination:
                        while True:
                            data = source.read(CHUNK)
                            if not data:
                                break
                            count += len(data)
                            if count > item['bytes']:
                                raise ValueError('Source changed during packaging: ' + item['path'])
                            digest.update(data)
                            destination.write(data)
                    if count != item['bytes'] or digest.hexdigest() != item['sha256']:
                        raise ValueError('Source changed during packaging: ' + item['path'])
            target.flush()
            os.fsync(target.fileno())
        # Atomic no-overwrite publication, including a destination created concurrently.
        guarded(output.parent)
        size, digest, _ = file_hash(temporary, temporary.stat().st_size)
        os.link(str(temporary), str(output))
        return {'operation': 'pack', 'archive': str(output), 'bytes': size, 'sha256': digest,
                'selected_files': len(metadata['files']), 'uncompressed_bytes': len(raw) + sum(x['bytes'] for x in metadata['files']),
                'external_dependencies': metadata['external_dependencies'], 'limits': metadata['limits']}
    finally:
        # Remove only this operation's still-identical temporary inode, never a replacement.
        try:
            current = temporary.lstat()
            if current.st_dev == identity.st_dev and current.st_ino == identity.st_ino:
                temporary.unlink()
        except FileNotFoundError:
            pass


def checked_archive(archive, maximum):
    infos = archive.infolist()
    if not 1 <= len(infos) <= MAX_FILES + 1:
        raise ValueError('Invalid archive entry count')
    members, total = {}, 0
    for info in infos:
        name = relative(info.filename, metadata=True)
        if name in members:
            raise ValueError('Duplicate archive member: ' + name)
        mode = info.external_attr >> 16
        if (info.is_dir() or stat.S_IFMT(mode) != stat.S_IFREG or mode & 0o7000
                or info.external_attr & 0x10 or info.flag_bits & 1
                or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
            raise ValueError('Unsupported or unsafe ZIP member type: ' + name)
        total += info.file_size
        if total > maximum:
            raise ValueError('Archive exceeds declared uncompressed byte budget')
        members[name] = info
    validate_tree(members)
    if META not in members or members[META].file_size > MAX_METADATA_BYTES:
        raise ValueError('Missing or oversized bundle metadata')
    raw = archive.read(members[META])
    metadata = json.loads(raw)
    if (not isinstance(metadata, dict) or metadata.get('schema') != 1
            or metadata.get('kind') != 'animation-selected-sources'
            or not isinstance(metadata.get('external_dependencies'), list)):
        raise ValueError('Unsupported bundle metadata')
    entries = metadata.get('files')
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_FILES:
        raise ValueError('Invalid bundle file index')
    indexed = {}
    for item in entries:
        if not isinstance(item, dict) or set(item) != {'path', 'bytes', 'sha256', 'mode'}:
            raise ValueError('Malformed bundle file record')
        name = relative(item['path'])
        if name in indexed:
            raise ValueError('Duplicate indexed file: ' + name)
        size, digest, mode = item['bytes'], item['sha256'], item['mode']
        if (type(size) is not int or size < 0 or not isinstance(digest, str) or not SHA.fullmatch(digest)
                or type(mode) is not int or not 0 <= mode <= 0o777):
            raise ValueError('Invalid bundle size/hash/mode: ' + name)
        if name not in members or members[name].file_size != size or (members[name].external_attr >> 16) & 0o777 != mode:
            raise ValueError('ZIP member differs from bundle index: ' + name)
        indexed[name] = item
    if set(members) != set(indexed) | {META}:
        raise ValueError('Archive contains missing or unindexed files')
    validate_tree(indexed)
    for name in indexed:
        digest, count = hashlib.sha256(), 0
        with archive.open(members[name]) as source:
            while True:
                data = source.read(CHUNK)
                if not data:
                    break
                count += len(data)
                if count > indexed[name]['bytes']:
                    raise ValueError('Expanded member exceeds indexed size: ' + name)
                digest.update(data)
        # Reading every member to EOF checks ZIP CRC as well as independent SHA256.
        if count != indexed[name]['bytes'] or digest.hexdigest() != indexed[name]['sha256']:
            raise ValueError('Bundle data SHA256 mismatch: ' + name)
    return metadata, total


def recover(archive_path, output, max_bytes=None):
    output = fresh(output)
    archive_path = guarded(archive_path)
    maximum = max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES
    created = False
    try:
        with open_regular(archive_path) as opened, zipfile.ZipFile(opened) as archive:
            metadata, total = checked_archive(archive, maximum)
            # No destination is created until paths, types, budgets, CRC and every hash pass.
            guarded(output.parent)
            output.mkdir(exist_ok=False)
            created = True
            for item in metadata['files']:
                destination = output / item['path']
                guarded(destination.parent)
                destination.parent.mkdir(parents=True, exist_ok=True)
                digest, count = hashlib.sha256(), 0
                with archive.open(item['path']) as source, destination.open('xb') as target:
                    while True:
                        data = source.read(CHUNK)
                        if not data:
                            break
                        count += len(data)
                        if count > item['bytes']:
                            raise ValueError('Archive changed during recovery: ' + item['path'])
                        digest.update(data)
                        target.write(data)
                if count != item['bytes'] or digest.hexdigest() != item['sha256']:
                    raise ValueError('Archive changed during recovery: ' + item['path'])
                os.chmod(str(destination), item['mode'])
            return {'operation': 'recover', 'archive': str(archive_path), 'directory': str(output),
                    'selected_files': len(metadata['files']), 'uncompressed_bytes': total,
                    'CRC_and_SHA256': 'passed before destination creation and hashes rechecked during recovery',
                    'external_dependencies': metadata['external_dependencies'],
                    'limits': 'Selected byte recovery only; native relink, receiving-application acceptance and rerender remain separate checks.'}
    except BaseException as error:
        if created:
            raise RuntimeError('Recovery failed; owned partial destination retained at {}: {}'.format(output, error)) from error
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('pack', help='Package an explicit source manifest without overwriting')
    create.add_argument('manifest', type=Path)
    create.add_argument('--output', required=True, type=Path)
    create.add_argument('--max-bytes', type=positive)
    restore = commands.add_parser('recover', help='Validate all archived bytes before creating a fresh directory')
    restore.add_argument('archive', type=Path)
    restore.add_argument('--out', required=True, type=Path)
    restore.add_argument('--max-bytes', type=positive)
    args = parser.parse_args(argv)
    try:
        report = pack(args.manifest, args.output, args.max_bytes) if args.command == 'pack' else recover(args.archive, args.out, args.max_bytes)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, zlib.error, EOFError, NotImplementedError) as error:
        print('sources: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
