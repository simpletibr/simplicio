"""Tests for the create-then-edit benchmark harness.

Run from this folder: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_bench
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import bench

QUOTA_LINE = json.dumps({
    "type": "error",
    "timestamp": 1793402060754,
    "sessionID": "ses_test",
    "error": {"type": "provider.quota", "message": "Go usage limit exceeded", "status": 429},
})
OK_OUTPUT = "\n".join([
    json.dumps({"type": "step_start", "sessionID": "ses_test"}),
    json.dumps({"type": "text", "sessionID": "ses_test", "text": "OK"}),
])
OK_RUN = {"exit": 0, "session_id": "ses_test", "quota_exhausted": False}
QUOTA_RUN = {"exit": 1, "session_id": "ses_test", "quota_exhausted": True}


class QuotaDetectionTest(unittest.TestCase):
    def test_provider_quota_error_is_detected(self):
        self.assertTrue(bench.quota_exhausted(QUOTA_LINE + "\n"))

    def test_normal_output_is_not_quota(self):
        self.assertFalse(bench.quota_exhausted(OK_OUTPUT))

    def test_non_json_lines_are_ignored(self):
        self.assertFalse(bench.quota_exhausted("warning: something\n{not json\n"))


class SaveResultsTest(unittest.TestCase):
    def test_writes_into_the_given_folder_and_merges_by_key(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bench, "STATE", Path(tmp) / "state"):
            out = Path(tmp) / "run"
            bench.save_results(out, [{"condition": "no-mcp", "rep": 0, "marker": 1}])
            bench.save_results(out, [
                {"condition": "no-mcp", "rep": 0, "marker": 2},
                {"condition": "simplicio-3.10.7", "rep": 0, "marker": 3},
            ])
            saved = json.loads((out / "results.json").read_text())
        self.assertEqual([(r["condition"], r["marker"]) for r in saved],
                         [("no-mcp", 2), ("simplicio-3.10.7", 3)])


class QuotaStopTest(unittest.TestCase):
    def run_session(self, phases):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(bench, "STATE", Path(tmp) / "state"), \
                mock.patch.object(bench, "OpencodeServer", mock.MagicMock()), \
                mock.patch.dict(bench.SCENARIOS, {"page": ("create", "edit", lambda work, edited: {"ok": True}, "users.json", bench.USERS)}), \
                mock.patch.object(bench, "run_phase", side_effect=phases):
            return bench.run_one("no-mcp", 0, keep=False)

    def test_quota_on_create_stops_before_the_edit(self):
        with self.assertRaises(bench.QuotaExhausted):
            self.run_session([QUOTA_RUN])

    def test_quota_on_edit_stops_the_session(self):
        with self.assertRaises(bench.QuotaExhausted):
            self.run_session([OK_RUN, QUOTA_RUN])


class SessionFolderTest(unittest.TestCase):
    def test_two_runs_of_one_repetition_never_share_a_folder(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bench, "STATE", Path(tmp)):
            first = bench.session_folder("no-mcp", 2)
            second = bench.session_folder("no-mcp", 2)
            self.assertNotEqual(first, second)
            self.assertEqual(first.parent, Path(tmp) / "work" / "no-mcp")


class IsolationTest(unittest.TestCase):
    def test_no_mcp_has_no_server_and_nothing_handles_a_login(self):
        self.assertEqual(bench.condition_config("no-mcp")["mcp"]["servers"], {})
        self.assertFalse(hasattr(bench, "sync_auth"))

    def test_the_model_reaches_the_config(self):
        self.assertEqual(bench.condition_config("no-mcp", "opencode/x-free")["model"], "opencode/x-free")

    def test_versions_run_through_the_sandbox_launcher(self):
        command = bench.server_command("simplicio-3.10.7")
        self.assertTrue(command[1].endswith("run.sh"))
        self.assertEqual(command[2], "3.10.7")


class OpenRouterRouteTest(unittest.TestCase):
    MODEL = "openrouter/deepseek/deepseek-v4.1-flash-1017"

    def test_the_route_pins_one_provider_so_sessions_stay_comparable(self):
        route = bench.condition_config("no-mcp", self.MODEL)["providers"]["openrouter"]
        self.assertEqual(route["body"]["provider"], {"order": ["cloudflare"], "allow_fallbacks": False})
        self.assertEqual(list(route["models"]), ["deepseek/deepseek-v4.1-flash-1017"])

    def test_the_config_names_the_key_and_never_holds_it(self):
        with mock.patch.dict(bench.os.environ, {"OPENROUTER_API_KEY": "sk-or-not-a-real-key"}):
            config = bench.condition_config("no-mcp", self.MODEL)
        self.assertEqual(config["providers"]["openrouter"]["env"], ["OPENROUTER_API_KEY"])
        self.assertNotIn("sk-or-not-a-real-key", json.dumps(config))

    def test_other_routes_keep_the_config_they_had(self):
        self.assertNotIn("providers", bench.condition_config("no-mcp", "opencode/x-free"))


class CatalogScenarioTest(unittest.TestCase):
    def test_the_catalog_prompts_use_their_own_files(self):
        create, edit, _check, name, rows = bench.SCENARIOS["catalog"]
        self.assertEqual(name, "products.json")
        self.assertEqual(len(rows), 30)
        self.assertIn("catalog.html", create)
        self.assertNotIn("users", create + edit)

    def test_the_catalog_check_expects_the_data_it_seeds(self):
        self.assertEqual(bench.CATALOG_SPEC.filter_rows, 10)
        self.assertEqual(len(set(bench.CATALOG_SPEC.values)), 30)
        matching = [p for p in bench.PRODUCTS if bench.CATALOG_SPEC.search_term in p["name"].lower()]
        self.assertTrue(0 < len(matching) < 30)


class ControlCheckTest(unittest.TestCase):
    SCRIPT = (
        "import json, sys\n"
        "users = json.load(open('users.json'))\n"
        "status = sys.argv[2] if len(sys.argv) > 2 else None\n"
        "users = [u for u in users if status is None or u['status'] == status]\n"
        "roles = {}\n"
        "for u in users:\n"
        "    roles[u['papel']] = roles.get(u['papel'], 0) + 1\n"
        "print(json.dumps({'total': len(users), 'por_papel': roles, 'status': status}))\n"
    )

    def work(self, tmp):
        work = Path(tmp)
        (work / "users.json").write_text(json.dumps(bench.USERS))
        return work

    def test_a_correct_script_passes_both_phases(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = self.work(tmp)
            (work / "stats.py").write_text(self.SCRIPT)
            self.assertTrue(bench.validate_control(work, edited=False)["ok"])
            self.assertTrue(bench.validate_control(work, edited=True)["ok"])

    def test_a_script_ignoring_the_option_fails_after_the_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = self.work(tmp)
            (work / "stats.py").write_text(self.SCRIPT.replace("if status is None or u['status'] == status", ""))
            self.assertFalse(bench.validate_control(work, edited=True)["ok"])

    def test_a_missing_script_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(bench.validate_control(self.work(tmp), edited=False)["ok"])


class ServerReadyTest(unittest.TestCase):
    def ready(self, answers, needs_mcp=True):
        server = bench.OpencodeServer.__new__(bench.OpencodeServer)
        server.needs_mcp = needs_mcp
        with mock.patch.object(bench.OpencodeServer, "mcp_status", side_effect=answers), \
                mock.patch.object(bench.time, "sleep"):
            server.wait_ready()

    def test_waits_until_no_server_is_pending(self):
        answers = [None, {"simplicio": "pending"}, {"simplicio": "connected"}]
        self.ready(answers)

    def test_a_failed_mcp_server_stops_the_session(self):
        with self.assertRaises(RuntimeError):
            self.ready([{"simplicio": "failed"}])

    def test_no_mcp_only_needs_the_location_loaded(self):
        self.ready([{"opencode_console": "connected"}], needs_mcp=False)


class StopRunTest(unittest.TestCase):
    def test_quota_stops_the_run_with_exit_3_and_saves_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            argv = ["bench.py", "--reps", "3", "--conditions", "no-mcp", "--out", str(out)]
            with mock.patch.object(bench, "STATE", Path(tmp) / "state"), \
                    mock.patch.object(bench, "run_one",
                                      side_effect=bench.QuotaExhausted("no-mcp rep 0 create")) as run_one, \
                    mock.patch.object(sys, "argv", argv):
                code = bench.main()
            self.assertEqual(code, 3)
            self.assertEqual(run_one.call_count, 1)
            self.assertFalse((out / "results.json").exists())


if __name__ == "__main__":
    unittest.main()


class ModelRoutesTest(unittest.TestCase):
    def test_each_model_keeps_its_own_fixed_endpoint(self):
        for model, endpoint in (
            ("anthropic/claude-haiku-5.5", "google-vertex/global"),
            ("openai/gpt-6-luna", "azure"),
            ("x-ai/grok-4.7", "xai/zdr"),
            ("meta/muse-spark-1.3", "meta"),
            ("qwen/qwen3.8-27b", "primeintellect/fp8"),
            ("deepseek/deepseek-v4.1-flash-1017", "cloudflare"),
        ):
            config = bench.condition_config("no-mcp", "openrouter/" + model)
            route = config["providers"]["openrouter"]
            self.assertEqual(route["body"]["provider"], {"order": [endpoint], "allow_fallbacks": False})
            self.assertEqual(list(route["models"]), [model])

    def test_a_model_without_a_measured_route_stops_the_run(self):
        with self.assertRaises(KeyError):
            bench.condition_config("no-mcp", "openrouter/acme/unknown-1")


class DeliveredFilesTest(unittest.TestCase):
    def test_what_the_session_created_is_kept_and_the_seed_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            work, out = Path(tmp, "work"), Path(tmp, "out")
            work.mkdir()
            for name in ("users.html", "users.json", "README.md", "opencode.json"):
                (work / name).write_text(name)
            (work / ".git").mkdir()
            bench.keep_delivered(work, out / "no-mcp-rep-00", "users.json")
            self.assertEqual(sorted(p.name for p in (out / "no-mcp-rep-00").iterdir()), ["users.html"])
            self.assertEqual((out / "no-mcp-rep-00" / "users.html").read_text(), "users.html")
