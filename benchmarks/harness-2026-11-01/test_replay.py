"""Tests for replay.py. Run: python3 -m unittest -v test_replay"""
import json
import unittest

import replay

PRICE = {"input": 1.0, "output": 2.0, "cache_read": 0.1, "cache_write": 1.25}


def assistant(created, completed, tokens, content):
    return ("assistant", json.dumps({"time": {"created": created, "completed": completed},
                                     "tokens": tokens, "content": content}))


class LabelsTest(unittest.TestCase):
    def test_a_private_path_never_reaches_a_label(self):
        label = replay.clean("cat /Users/someone/x/users.json /private/var/folders/4w/abc/file")
        self.assertNotIn("someone", label)
        self.assertNotIn("/private", label)

    def test_a_session_folder_never_reads_as_the_home_directory(self):
        # The folder a session ran in is not the user's home: "rm -rf ~" would be a false and alarming label.
        label = replay.clean("rm -rf /private/var/folders/4w/abc/T/bench-cli-x/work && ls")
        self.assertNotIn("~", label)
        self.assertEqual(label, "rm -rf <dir> && ls")

    def test_a_label_saved_with_a_tilde_never_reaches_the_site(self):
        # Rounds saved before the fix hold "~" where a session folder was. None of them is a real home path.
        import site_bench
        step = {"t0": 0, "t1": 1, "output": 5, "cost": 0.1, "tools": [{"kind": "tool", "label": "$ rm -rf ~ && ls"}]}
        self.assertEqual(site_bench.compact([step])[0]["l"][0][1], "$ rm -rf <dir> && ls")

    def test_a_long_command_is_cut(self):
        self.assertLessEqual(len(replay.clean("a" * 300)), replay.LABEL_MAX)

    def test_code_mode_shows_the_simplicio_tool_it_called(self):
        item = {"name": "execute", "state": {"input": {"code": "await tools.simplicio.simplicio_codegen({})"}}}
        self.assertEqual(replay.tool_label(item), ("simplicio", "simplicio_codegen"))

    def test_a_write_shows_the_file_name_only(self):
        item = {"name": "write", "state": {"input": {"filePath": "/Users/w/work/users.html"}}}
        self.assertEqual(replay.tool_label(item), ("tool", "write users.html"))


class StepsTest(unittest.TestCase):
    def test_times_are_relative_and_tokens_add_up(self):
        rows = [
            ("user", "{}"),
            assistant(1000, 3000, {"input": 10, "output": 5, "reasoning": 1, "cache": {"read": 100, "write": 4}},
                      [{"type": "tool", "name": "shell", "state": {"input": {"command": "ls"}}}]),
            assistant(4000, 5500, {"input": 2, "output": 3, "cache": {"read": 50}}, [{"type": "text", "text": "OK"}]),
        ]
        built = replay.steps_from_rows(rows, PRICE)
        self.assertEqual([s["t0"] for s in built["steps"]], [0.0, 3.0])
        self.assertEqual(built["total"]["seconds"], 4.5)
        self.assertEqual(built["total"]["requests"], 2)
        self.assertEqual(built["total"]["output_tokens"], 9)
        self.assertEqual(built["total"]["input_tokens"], 166)
        self.assertEqual(built["steps"][0]["tools"], [{"kind": "tool", "label": "$ ls"}])
        self.assertTrue(built["steps"][1]["text"])

    def test_cost_prices_each_kind_of_token(self):
        tokens = {"input": 1_000_000, "output": 1_000_000, "reasoning": 0, "cache": {"read": 1_000_000, "write": 1_000_000}}
        self.assertAlmostEqual(replay.cost_of(tokens, PRICE), 1 + 2 + 0.1 + 1.25)

    def test_no_output_text_or_tool_result_is_kept(self):
        rows = [assistant(1000, 2000, {"input": 1, "output": 1}, [
            {"type": "tool", "name": "shell", "state": {"input": {"command": "cat x"}, "content": "SECRET OUTPUT"}},
            {"type": "text", "text": "SECRET TEXT"}])]
        self.assertNotIn("SECRET", json.dumps(replay.steps_from_rows(rows, PRICE)))


class MedianSessionTest(unittest.TestCase):
    @staticmethod
    def record(rep, seconds, ok=True):
        return {"rep": rep, "create_run": {"wall_s": seconds}, "edit_run": {"wall_s": 0},
                "files_after_create": {"ok": ok}, "files_after_edit": {"ok": ok}}

    def test_the_session_closest_to_the_median_is_chosen(self):
        records = [self.record(0, 10), self.record(1, 20), self.record(2, 90)]
        self.assertEqual(replay.median_session(records)["rep"], 1)

    def test_a_failed_session_is_never_the_one_shown_when_another_delivered(self):
        records = [self.record(0, 20, ok=False), self.record(1, 10), self.record(2, 30)]
        self.assertTrue(replay.delivered(replay.median_session(records)))


if __name__ == "__main__":
    unittest.main()
