"""The resume driver: run only what a round lacks, and wait out the provider limit."""
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

import bench
import resume

CONDITIONS = ["no-mcp", "simplicio-3.9.2", "simplicio-candidate"]


def session(condition, rep, **extra):
    record = {"condition": condition, "rep": rep, "create_run": {"session_id": "s"}}
    record.update(extra)
    return record


class MissingTest(unittest.TestCase):
    def folder(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name)
        (out / "results.json").write_text(json.dumps(rows))
        return out

    def test_a_new_folder_lacks_everything_one_rep_at_a_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo = resume.missing(Path(tmp) / "none", CONDITIONS, 2)
        self.assertEqual(todo[:3], [(0, c) for c in CONDITIONS])
        self.assertEqual(len(todo), 6)

    def test_saved_sessions_are_not_repeated(self):
        out = self.folder([session("no-mcp", 0), session("simplicio-3.9.2", 0)])
        self.assertEqual(resume.missing(out, CONDITIONS, 1), [(0, "simplicio-candidate")])

    def test_a_session_saved_with_an_error_counts_as_missing(self):
        out = self.folder([session("no-mcp", 0, error="RuntimeError('MCP server not connected')")])
        self.assertIn((0, "no-mcp"), resume.missing(out, ["no-mcp"], 1))


class DriverTest(unittest.TestCase):
    ROUND = resume.Round("page", Path("unused"), 2)

    def drive(self, codes, todo):
        """Runs one round against scripted sessions; returns the sessions run and the waits."""
        runs, waits = [], []

        def fake_run(round_, rep, condition, model):
            runs.append((rep, condition))
            return codes.pop(0)

        with mock.patch.object(resume, "missing", side_effect=todo), \
                mock.patch.object(resume, "run_session", side_effect=fake_run), \
                mock.patch.object(resume, "login_ok", return_value=True), \
                mock.patch.object(resume.time, "sleep", side_effect=waits.append):
            result = resume.run_round(self.ROUND, ["no-mcp"], "m")
        return result, runs, waits

    def test_the_limit_waits_and_repeats_the_same_session(self):
        limit = (resume.LIMIT_EXIT, 60000)
        result, runs, waits = self.drive([limit, (0, None)], [[(0, "no-mcp")], [(0, "no-mcp")], []])
        self.assertTrue(result)
        self.assertEqual(runs, [(0, "no-mcp"), (0, "no-mcp")])
        self.assertEqual(waits, [60 + resume.WAIT_MARGIN_S])

    def test_a_limit_without_a_time_waits_the_default(self):
        limit = (resume.LIMIT_EXIT, None)
        _result, _runs, waits = self.drive([limit, (0, None)], [[(0, "no-mcp")], [(0, "no-mcp")], []])
        self.assertEqual(waits, [resume.DEFAULT_WAIT_S])

    def test_a_session_that_keeps_failing_is_given_up_and_reported(self):
        failing = [(1, None)] * resume.MAX_ATTEMPTS
        result, runs, _waits = self.drive(list(failing), [[(0, "no-mcp")]] * (resume.MAX_ATTEMPTS + 1))
        self.assertFalse(result)
        self.assertEqual(len(runs), resume.MAX_ATTEMPTS)

    def test_the_limit_does_not_use_up_attempts(self):
        codes = [(resume.LIMIT_EXIT, 1000)] * (resume.MAX_ATTEMPTS + 1) + [(0, None)]
        todo = [[(0, "no-mcp")]] * (resume.MAX_ATTEMPTS + 2) + [[]]
        result, runs, _waits = self.drive(codes, todo)
        self.assertTrue(result)
        self.assertEqual(Counter(runs)[(0, "no-mcp")], resume.MAX_ATTEMPTS + 2)

    def test_a_broken_login_stops_the_round_before_any_session(self):
        with mock.patch.object(resume, "missing", return_value=[(0, "no-mcp")]), \
                mock.patch.object(resume, "run_session") as run, \
                mock.patch.object(resume, "login_ok", return_value=False):
            self.assertFalse(resume.run_round(self.ROUND, ["no-mcp"], "m"))
        run.assert_not_called()


class ParseRoundTest(unittest.TestCase):
    def test_a_round_can_name_its_own_conditions(self):
        round_ = resume.parse_round("catalog:out:6:simplicio-3.9.2,simplicio-candidate")
        self.assertEqual(round_.conditions, ["simplicio-3.9.2", "simplicio-candidate"])
        self.assertEqual(round_.reps, 6)

    def test_a_round_without_conditions_uses_the_shared_list(self):
        self.assertIsNone(resume.parse_round("page:out:10").conditions)


class RetryAfterTest(unittest.TestCase):
    EVENT = json.dumps({"type": "error", "error": {"type": "provider.free-limit", "retryAfterMs": 29036000}})

    def test_the_wait_is_read_from_the_error_event(self):
        self.assertEqual(bench.retry_after_ms(self.EVENT + "\n"), 29036000)

    def test_output_without_a_limit_has_no_wait(self):
        self.assertIsNone(bench.retry_after_ms('{"type":"text"}\nnot json\n'))

    def test_the_stop_line_carries_the_wait(self):
        self.assertEqual(resume.wait_from_output("x\nSTOP: limit reached at a retry_after_ms=1500\n"), 1500)
        self.assertIsNone(resume.wait_from_output("nothing here\n"))


if __name__ == "__main__":
    unittest.main()
