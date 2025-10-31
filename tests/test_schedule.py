import os
import sys
import unittest
from datetime import date
from io import StringIO

# Import from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from thunderbird_schedule import generate_schedule, WEEKDAY_NAME, format_date, main  # noqa: E402


def lines_from_schedule(schedule):
    # Helper to render lines as the CLI prints them (aligned columns)
    rows = [(format_date(d), WEEKDAY_NAME[d.weekday()], label) for d, label in schedule]
    date_w = max(len(r[0]) for r in rows) if rows else 0
    day_w = max(len(r[1]) for r in rows) if rows else 0
    out = [f"{date:<{date_w}}  {day:<{day_w}}  {label}" for date, day, label in rows]
    return out


class TestGenerateSchedule(unittest.TestCase):
    def test_function_desktop_146(self):
        sched = generate_schedule('desktop', 146, date(2025, 10, 13))
        expected = [
            (date(2025, 10, 13), 'Thunderbird 146.0a1 starts'),
            (date(2025, 11, 3),  'Thunderbird 146.0a1 soft freeze starts'),
            (date(2025, 11, 6),  'Thunderbird 146.0a1 pre-merge review'),
            (date(2025, 11, 10), 'Thunderbird merge 146.0a1 central->beta'),
            (date(2025, 11, 12), 'Thunderbird 146.0b1'),
            (date(2025, 11, 19), 'Thunderbird 146.0b2'),
            (date(2025, 11, 26), 'Thunderbird 146.0b3'),
            (date(2025, 11, 27), 'Thunderbird 146.0 beta pre-merge review'),
            (date(2025, 12, 1),  'Thunderbird 146.0b4'),
            (date(2025, 12, 2),  'Thunderbird merge 146.0 beta->release'),
            (date(2025, 12, 9),  'Thunderbird 146.0'),
            (date(2025, 12, 23), 'Thunderbird 146.0.1'),
        ]
        self.assertEqual(sched, expected)

    def test_function_android_15(self):
        sched = generate_schedule('android', 15, date(2025, 10, 16))
        expected = [
            (date(2025, 10, 16), 'TfA 15.0a1 starts'),
            (date(2025, 11, 6),  'TfA 15.0a1 soft freeze starts'),
            (date(2025, 11, 13), 'TfA merge 15.0a1 main->beta'),
            (date(2025, 11, 17), 'TfA 15.0b1'),
            (date(2025, 11, 24), 'TfA 15.0b2'),
            (date(2025, 12, 1),  'TfA 15.0b3'),
            (date(2025, 12, 8),  'TfA merge 15.0 beta->release'),
            (date(2025, 12, 15), 'TfA 15.0'),
            (date(2025, 12, 29), 'TfA 15.1'),
        ]
        self.assertEqual(sched, expected)


class TestCLI(unittest.TestCase):
    def run_cli(self, args):
        # Call main() directly and capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Set locale env vars for consistent output
        old_env = os.environ.copy()
        os.environ.update({'LC_ALL': 'C', 'LANG': 'C'})

        try:
            # Simulate command-line invocation
            sys.argv = ['thunderbird-schedule'] + args
            exit_code = main(sys.argv)
            output = sys.stdout.getvalue()
            return output.strip().splitlines()
        finally:
            sys.stdout = old_stdout
            os.environ.clear()
            os.environ.update(old_env)

    def test_cli_desktop_146(self):
        lines = self.run_cli(['desktop', '146', '2025-10-13'])
        expected_lines = lines_from_schedule(generate_schedule('desktop', 146, date(2025, 10, 13)))
        self.assertEqual(lines, expected_lines)

    def test_cli_android_15(self):
        lines = self.run_cli(['android', '15', '2025-10-16'])
        expected_lines = lines_from_schedule(generate_schedule('android', 15, date(2025, 10, 16)))
        self.assertEqual(lines, expected_lines)

    def test_cli_desktop_non_monday_errors(self):
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['thunderbird-schedule', 'desktop', '146', '2025-10-18']
                main(sys.argv)
            stderr_output = sys.stderr.getvalue()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn('desktop a1 start date must be a Monday', stderr_output)
        finally:
            sys.stderr = old_stderr

    def test_cli_android_non_thursday_errors(self):
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                sys.argv = ['thunderbird-schedule', 'android', '15', '2025-10-15']
                main(sys.argv)
            stderr_output = sys.stderr.getvalue()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn('android a1 start date must be a Thursday', stderr_output)
        finally:
            sys.stderr = old_stderr


if __name__ == '__main__':
    unittest.main()
