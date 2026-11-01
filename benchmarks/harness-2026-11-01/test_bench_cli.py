"""Tests for the Claude Code and Grok Build rounds. Run: python3 -m unittest -v test_bench_cli"""
import json
import unittest

import bench_cli

PRICE = {"input": 2.0, "output": 10.0, "cache_read": 0.1, "cache_write": 2.5}
GROK = {"input": 2.0, "output": 6.0, "cache_read": 0.5, "cache_write": 2.0}


def stamp(seconds):
    return "2026-11-01T02:29:%06.3fZ" % seconds


def assistant(mid, seconds, usage, content):
    return {"type": "assistant", "timestamp": stamp(seconds), "message": {"id": mid, "usage": usage, "content": content}}


class ClaudeStepsTest(unittest.TestCase):
    ROWS = [
        {"type": "user", "timestamp": stamp(10), "message": {"content": "create it"}},
        assistant("m1", 12, {"input_tokens": 2, "output_tokens": 1, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 50},
                  [{"type": "thinking"}]),
        assistant("m1", 13, {"input_tokens": 2, "output_tokens": 40, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 50},
                  [{"type": "tool_use", "name": "mcp__simplicio__simplicio_map", "input": {"task": "x"}}]),
        {"type": "user", "timestamp": stamp(14), "message": {"content": [{"type": "tool_result"}]}},
        assistant("m2", 15, {"input_tokens": 1, "output_tokens": 4, "cache_read_input_tokens": 150, "cache_creation_input_tokens": 0},
                  [{"type": "text", "text": "OK"}]),
    ]

    def test_blocks_of_one_message_become_one_step_with_its_final_usage(self):
        steps = bench_cli.claude_steps(self.ROWS, PRICE)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["output"], 40)
        self.assertEqual(steps[0]["input"], 152)
        self.assertEqual(steps[0]["tools"], [{"kind": "simplicio", "label": "simplicio_map"}])

    def test_times_start_at_the_first_prompt(self):
        steps = bench_cli.claude_steps(self.ROWS, PRICE)
        self.assertEqual((steps[0]["t0"], steps[0]["t1"]), (0.0, 3.0))
        self.assertEqual((steps[1]["t0"], steps[1]["t1"]), (4.0, 5.0))

    def test_cost_prices_cache_writes_and_reads(self):
        steps = bench_cli.claude_steps(self.ROWS, PRICE)
        expected = (2 * 2.0 + 40 * 10.0 + 100 * 0.1 + 50 * 2.5) / 1e6
        self.assertAlmostEqual(steps[0]["cost"], expected, places=6)

    def test_a_bash_label_hides_private_paths(self):
        kind, label = bench_cli.claude_label({"name": "Bash", "input": {"command": "cat /Users/someone/x.json"}})
        self.assertEqual(kind, "tool")
        self.assertNotIn("someone", label)


class GrokStepsTest(unittest.TestCase):
    EVENTS = [
        (0.5, {"type": "thought", "data": "x"}),
        (3.0, {"type": "usage", "usage": {"input_tokens": 24000, "output_tokens": 700, "cache_read_input_tokens": 1000}}),
        (3.1, {"type": "tool_call", "toolCallId": "a", "toolName": "write", "rawInput": {"file_path": "/Users/x/users.html"}}),
        (3.2, {"type": "tool_call_update", "toolCallId": "a", "status": "completed"}),
        (5.0, {"type": "usage", "usage": {"input_tokens": 3000, "output_tokens": 30, "cache_read_input_tokens": 26000}}),
        (5.1, {"type": "end", "total_cost_usd": 0.07}),
    ]

    def test_each_usage_closes_a_step_and_owns_the_tools_after_it(self):
        steps = bench_cli.grok_steps(self.EVENTS, GROK)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["tools"], [{"kind": "tool", "label": "write users.html"}])
        self.assertEqual(steps[1]["tools"], [])
        self.assertTrue(steps[1]["text"])

    def test_times_and_tokens(self):
        steps = bench_cli.grok_steps(self.EVENTS, GROK)
        self.assertEqual((steps[0]["t0"], steps[0]["t1"]), (0.0, 3.0))
        self.assertEqual((steps[1]["t0"], steps[1]["t1"]), (3.2, 5.0))
        self.assertEqual(steps[0]["output"], 700)
        self.assertEqual(steps[0]["input"], 25000)

    def test_cost_matches_the_client_total(self):
        steps = bench_cli.grok_steps(self.EVENTS, GROK)
        total = sum(s["cost"] for s in steps)
        self.assertAlmostEqual(total, (27000 * 2 + 730 * 6 + 27000 * 0.5) / 1e6, places=6)

    def test_a_simplicio_tool_is_marked(self):
        events = [(1.0, {"type": "usage", "usage": {"input_tokens": 1, "output_tokens": 1}}),
                  (1.1, {"type": "tool_call", "toolCallId": "b", "toolName": "mcp__simplicio__simplicio_codegen", "rawInput": {}})]
        self.assertEqual(bench_cli.grok_steps(events, GROK)[0]["tools"], [{"kind": "simplicio", "label": "simplicio_codegen"}])


class TotalsTest(unittest.TestCase):
    def test_phase_totals_add_up(self):
        steps = [{"output": 5, "input": 10, "cost": 0.1, "tools": [], "text": True, "t0": 0, "t1": 1, "tokens": {"input": 1, "output": 5, "cache_read": 8, "cache_write": 1}},
                 {"output": 7, "input": 20, "cost": 0.2, "tools": [], "text": True, "t0": 1, "t1": 2, "tokens": {"input": 2, "output": 7, "cache_read": 17, "cache_write": 1}}]
        phase = bench_cli.phase_totals(steps)
        self.assertEqual(phase["requests"], 2)
        self.assertEqual(phase["tokens"], {"input": 3, "output": 12, "reasoning": 0, "cache_read": 25, "cache_write": 2})
        self.assertAlmostEqual(phase["cost"], 0.3)


class SpendTest(unittest.TestCase):
    def test_the_budget_counts_sessions_already_saved(self):
        rows = [{"create_phase": {"cost": 0.4}, "edit_phase": {"cost": 0.1}}, {"create_phase": {"cost": 0.2}, "edit_phase": {"cost": 0.2}}]
        self.assertAlmostEqual(bench_cli.spent(rows), 0.9)


if __name__ == "__main__":
    unittest.main()
