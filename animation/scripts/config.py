"""Shared nonsecret runtime configuration. Python 3.9+, standard library only.

ANIMATION_CONFIG selects a configuration explicitly. Otherwise local.json is used
when present, followed by local.example.json. Relative paths use the selected
configuration directory; bare executable names use the current PATH. No installs,
credential discovery, environment-file loading, or network access are performed.
"""
import json
import os
from pathlib import Path
import shutil

SCRIPTS = Path(__file__).resolve().parent


class Settings(dict):
    def __init__(self, value, source):
        super().__init__(value)
        self.source = source


def settings(path=None):
    selected = path if path is not None else os.environ.get('ANIMATION_CONFIG')
    if selected is not None:
        if not str(selected).strip():
            raise ValueError('ANIMATION_CONFIG must name a JSON file')
        source = Path(selected).expanduser().absolute()
    else:
        source = SCRIPTS / 'local.json'
        if not source.is_file():
            source = SCRIPTS / 'local.example.json'
    try:
        value = json.loads(source.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError('Cannot read animation configuration {}: {}'.format(source, error)) from error
    if not isinstance(value, dict):
        raise ValueError('Animation configuration must be a JSON object: ' + str(source))
    if any(not isinstance(k, str) or (v is not None and not isinstance(v, str)) for k, v in value.items()):
        raise ValueError('Animation configuration values must be path strings or null: ' + str(source))
    return Settings(value, source)


def configured(config, key):
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Configure {} in ANIMATION_CONFIG or scripts/local.json'.format(key))
    value = value.strip()
    if '/' not in value and '\\' not in value and not value.startswith('.'):
        found = shutil.which(value)
        if found:
            return Path(found).absolute()
    path = Path(value).expanduser()
    base = getattr(config, 'source', SCRIPTS / 'local.json').parent
    return Path(os.path.abspath(str(path if path.is_absolute() else base / path)))
