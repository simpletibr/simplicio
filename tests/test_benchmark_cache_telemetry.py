#!/usr/bin/env python3
"""Tests for benchmark_cache_telemetry synthesis and decoupling invariants."""

from __future__ import annotations

import pytest
from benchmarks.benchmark_cache_telemetry import (
    evaluate_telemetry_receipt,
    format_cache_telemetry_table,
)


def test_format_cache_telemetry_table_renders_decoupled_columns():
    records = [
        {
            "scenario": "snake_game_init",
            "model": "deepseek/deepseek-chat",
            "cache_local_status": "hit",
            "cache_provider_tokens": 0,
            "cache_provider_discount_usd": 0.0,
            "latency_ms": 1500,
            "run_outcome": "completed",
        },
        {
            "scenario": "snake_game_color_edit",
            "model": "deepseek/deepseek-chat",
            "cache_local_status": "hit",
            "cache_provider_tokens": 2048,
            "cache_provider_discount_usd": 0.00028,
            "latency_ms": 750,
            "run_outcome": "completed",
        },
    ]
    table = format_cache_telemetry_table(records)
    assert "| Local Cache Status | Remote KV Cache Tokens | Provider Discount ($) |" in table
    assert "| snake_game_init | deepseek/deepseek-chat | hit | 0 | $0.0000 | 1.50s | completed |" in table
    assert "| snake_game_color_edit | deepseek/deepseek-chat | hit | 2,048 | $0.0003 | 0.75s | completed |" in table


def test_evaluate_telemetry_receipt_enforces_decoupling():
    # Valid: local hit with 0 remote tokens
    valid_record = {
        "cache_local_status": "hit",
        "cache_provider_tokens": 0,
        "usage": {"prompt_tokens_details": {"cached_tokens": 0}},
    }
    eval_result = evaluate_telemetry_receipt(valid_record)
    assert eval_result["valid"] is True
    assert eval_result["local_status"] == "hit"
    assert eval_result["provider_tokens"] == 0

    # Invalid: local hit fabricating provider tokens when provider reported 0
    fabricated_record = {
        "cache_local_status": "hit",
        "cache_provider_tokens": 1500,
        "usage": {"prompt_tokens_details": {"cached_tokens": 0}},
    }
    invalid_result = evaluate_telemetry_receipt(fabricated_record)
    assert invalid_result["valid"] is False
    assert invalid_result["reason"] == "provider_tokens_fabricated_from_local_hit"
