"""Opt-in real-browser checks. No downloads; use existing local dependencies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.environ.get('ANIMATION_TEST_BROWSER'),
                     'Set ANIMATION_TEST_BROWSER to run optional existing-browser checks')
class MotionBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='animation-browser-test-')
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)
        self.helper = Path(__file__).resolve().parents[1] / 'scripts/check_motion.mjs'
        self.node = os.environ.get('ANIMATION_TEST_NODE') or shutil.which('node')
        self.assertTrue(self.node, 'Existing Node.js is required')

    def check(self, drawing, expect=True):
        source = self.root / 'scene'
        source.mkdir()
        (source / 'index.html').write_text('''<!doctype html><meta charset="utf-8">
<style>body{margin:0}#dot{position:absolute;top:40px;width:32px;height:32px;background:#123456}</style>
<main data-composition-id="test" data-width="320" data-height="180" data-duration="4"><div id="dot"></div></main>
<script>let x=0;window.renderFrame=t=>{''' + drawing + '''};renderFrame(0);</script>''')
        out = self.root / 'report'
        command = [self.node, str(self.helper), str(source), '--out', str(out),
                   '--browser', os.environ['ANIMATION_TEST_BROWSER']]
        if expect:
            command.append('--expect-motion')
        completed = subprocess.run(command, capture_output=True, text=True, timeout=90)
        self.assertTrue((out / 'report.json').is_file(), completed.stderr)
        return completed, json.loads((out / 'report.json').read_text()), command, out

    def test_stateless_motion_restores_pixels_and_refuses_existing_report(self):
        result, report, command, out = self.check("document.querySelector('#dot').style.left=(t*40)+'px'")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report['checks']['backward_seek_within_capture_tolerance'])
        self.assertTrue(report['checks']['sampled_pixels_change'])
        original = (out / 'report.json').read_bytes()
        retry = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(retry.returncode, 0)
        self.assertEqual((out / 'report.json').read_bytes(), original)

    def test_accumulating_state_fails_repeated_time_check(self):
        result, report, _, _ = self.check("x+=t*5;document.querySelector('#dot').style.left=x+'px'")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report['checks']['backward_seek_within_capture_tolerance'])

    def test_static_scene_does_not_count_noise_as_expected_motion(self):
        result, report, _, _ = self.check("document.querySelector('#dot').style.left='10px'")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report['checks']['sampled_pixels_change'])
        self.assertTrue(report['checks']['backward_seek_within_capture_tolerance'])


if __name__ == '__main__':
    unittest.main()
