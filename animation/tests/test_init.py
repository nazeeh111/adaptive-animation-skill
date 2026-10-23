"""Fresh-project routing and preservation probes; no engine/network required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='animation-init-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def initialize(self, name, *options):
        project = self.root / name
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/studio.py'), 'init',
            str(project), '--brief', 'An authored subject and consequence', *options],
            capture_output=True, text=True, timeout=15)
        return project, result

    def test_bare_workspace_does_not_copy_a_scene(self):
        project, result = self.initialize('empty')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list((project / 'source').iterdir()), [])
        self.assertEqual(list((project / 'assets').iterdir()), [])
        config = json.loads((project / 'studio.json').read_text())
        self.assertEqual(config['template'], 'empty')
        self.assertIsNone(config['example'])

    def test_generic_capture_has_requested_geometry_clock_and_no_authored_identity(self):
        project, result = self.initialize('capture', '--template', 'motion', '--size',
            '720x900', '--duration', '4.5')
        self.assertEqual(result.returncode, 0, result.stderr)
        source = project / 'source/motion'
        html = (source / 'index.html').read_text()
        self.assertIn('data-width="720"', html)
        self.assertIn('data-height="900"', html)
        self.assertIn('data-duration="4.5"', html)
        self.assertNotIn('@DURATION@', html)
        self.assertEqual({p.name for p in (source / 'assets').iterdir()}, {'gsap.min.js'})
        # The actual artwork/font files of the explicit study must not be routed here.
        self.assertNotEqual((source / 'motion.js').read_bytes(),
            (ROOT / 'assets/examples/orbit-title/motion.js').read_bytes())
        self.assertNotIn('@font-face', (source / 'style.css').read_text())
        self.assertEqual(json.loads((project / 'studio.json').read_text())['duration'], 4.5)

    def test_explicit_study_preserves_authored_sources_fonts_and_licenses(self):
        project, result = self.initialize('study', '--template', 'motion', '--example',
            'orbit-title', '--size', '640x360')
        self.assertEqual(result.returncode, 0, result.stderr)
        source = project / 'source/motion'
        for name in ('index.html', 'style.css', 'motion.js'):
            expected = (ROOT / 'assets/examples/orbit-title' / name).read_text()
            expected = expected.replace('@WIDTH@', '640').replace('@HEIGHT@', '360')
            self.assertEqual((source / name).read_text(), expected)
        for original in (ROOT / 'assets/fonts').iterdir():
            if original.is_file():
                self.assertEqual((source / 'assets' / original.name).read_bytes(), original.read_bytes())
        self.assertEqual(json.loads((project / 'studio.json').read_text())['example'], 'orbit-title')

    def test_invalid_selection_fails_before_creation_and_retry_preserves_bytes(self):
        for name, options in (
            ('requires-motion', ('--example', 'orbit-title')),
            ('wrong-clock', ('--template', 'motion', '--example', 'orbit-title', '--duration', '8')),
            ('nonfinite', ('--template', 'motion', '--duration', 'nan'))):
            with self.subTest(name=name):
                project, result = self.initialize(name, *options)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(project.exists(), result.stdout + result.stderr)
        project, result = self.initialize('keep')
        self.assertEqual(result.returncode, 0, result.stderr)
        sentinel = project / 'source/precious.txt'
        sentinel.write_bytes(b'unrelated authored work\x00')
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        _, retry = self.initialize('keep', '--template', 'motion')
        self.assertNotEqual(retry.returncode, 0)
        self.assertEqual(before, {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
