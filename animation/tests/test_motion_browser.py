"""Opt-in real-browser checks. No downloads; use existing local dependencies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
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
        self.run_count = 0

    def check(self, drawing, expect=True, extra_args=None, duration=4):
        self.run_count += 1
        source = self.root / ('scene-' + str(self.run_count))
        source.mkdir()
        (source / 'index.html').write_text(('''<!doctype html><meta charset="utf-8">
<style>body{margin:0}#dot{position:absolute;top:40px;width:32px;height:32px;background:#123456}</style>
<main data-composition-id="test" data-width="320" data-height="180" data-duration="DURATION"><div id="dot"></div></main>
<script>let x=0;window.renderFrame=t=>{''' + drawing + '''};renderFrame(0);</script>''').replace('DURATION', str(duration)))
        out = self.root / ('report-' + str(self.run_count))
        command = [self.node, str(self.helper), str(source), '--out', str(out),
                   '--browser', os.environ['ANIMATION_TEST_BROWSER']]
        command.extend(extra_args or [])
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

    def test_generic_scaffold_is_an_awaitable_capture_consumer_without_motion(self):
        # A returned paused GSAP Timeline is thenable and hangs an awaiting capturer.
        project = self.root / 'generic-scaffold'
        initialized = subprocess.run([sys.executable, str(self.helper.parent / 'studio.py'),
            'init', str(project), '--brief', 'Author a scene after initialization',
            '--template', 'motion', '--duration', '4.5', '--size', '320x180'],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        out = self.root / 'generic-report'
        completed = subprocess.run([self.node, str(self.helper), str(project / 'source/motion'),
            '--out', str(out), '--browser', os.environ['ANIMATION_TEST_BROWSER'], '--exact'],
            # Let the checker's owned 60-second browser cleanup finish before an outer timeout.
            capture_output=True, text=True, timeout=90)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads((out / 'report.json').read_text())
        self.assertTrue(report['checks']['backward_seek_within_capture_tolerance'])
        self.assertFalse(report['checks']['sampled_pixels_change'])

    def test_accumulating_state_fails_repeated_time_check(self):
        result, report, _, _ = self.check("x+=t*5;document.querySelector('#dot').style.left=x+'px'")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report['checks']['backward_seek_within_capture_tolerance'])

    def test_static_scene_does_not_count_noise_as_expected_motion(self):
        result, report, _, _ = self.check("document.querySelector('#dot').style.left='10px'")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report['checks']['sampled_pixels_change'])
        self.assertTrue(report['checks']['backward_seek_within_capture_tolerance'])

    def test_explicit_action_times_find_motion_missed_by_duration_samples(self):
        drawing = "document.querySelector('#dot').style.left=(t>=2&&t<2.3?120:10)+'px'"
        baseline, old_report, _, _ = self.check(drawing, duration=12)
        self.assertNotEqual(baseline.returncode, 0)
        self.assertFalse(old_report['checks']['sampled_pixels_change'])
        selected, report, _, _ = self.check(drawing, duration=12,
            extra_args=['--times', '2.2,1.95,2.05,2.2,2.35'])
        self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
        self.assertEqual(report['sampling']['forward_times'], [0, 1.95, 2.05, 2.2, 2.35])
        self.assertTrue(report['checks']['sampled_pixels_change'])
        self.assertTrue(report['checks']['backward_seek_within_capture_tolerance'])

    def test_explicit_time_outside_scene_fails_before_capture(self):
        result, report, _, _ = self.check("document.querySelector('#dot').style.left=(t*40)+'px'",
            extra_args=['--times', '1,4.01'])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['samples'], [])
        self.assertTrue(any('composition duration' in message for message in report['failures']))


if __name__ == '__main__':
    unittest.main()
