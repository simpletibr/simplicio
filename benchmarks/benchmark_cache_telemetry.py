#!/usr/bin/env python3
"""Benchmark telemetry harness: decouples local AST/envelope cache from remote provider KV Cache.

Emits structured synthesis tables with separate columns for local mapper/envelope cache
and remote provider prompt cache tokens, preventing false 100% cache claims when remote
LLM providers report 0 cached tokens.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


def format_cache_telemetry_table(records: Sequence[Mapping[str, Any]]) -> str:
    """Format benchmark execution receipts into a Markdown synthesis table with decoupled cache columns."""
    headers = [
        "Scenario",
        "Model",
        "Local Cache Status",
        "Remote KV Cache Tokens",
        "Provider Discount ($)",
        "Latency (s)",
        "Outcome",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for r in records:
        scenario = str(r.get("scenario") or r.get("api_request_id") or "default")
        model = str(r.get("model") or "unknown")
        local_status = str(r.get("cache_local_status") or r.get("mapper_cache_status") or "bypassed")
        
        # Explicit decoupling: verify remote tokens independently of local status
        provider_tokens = r.get("cache_provider_tokens")
        if provider_tokens is None:
            provider_tokens = (
                r.get("provider_prompt_cache", {}).get("cache_read_tokens")
                if isinstance(r.get("provider_prompt_cache"), dict)
                else None
            )
        tokens_str = f"{provider_tokens:,}" if isinstance(provider_tokens, int) else "0"

        discount = r.get("cache_provider_discount_usd")
        if discount is None and isinstance(r.get("savings"), dict):
            discount = r.get("savings", {}).get("cache_provider_discount_usd")
        discount_str = f"${float(discount):.4f}" if discount is not None else "$0.0000"

        latency = r.get("latency_ms")
        latency_str = f"{(latency / 1000.0):.2f}s" if isinstance(latency, (int, float)) else "-"
        outcome = str(r.get("run_outcome") or r.get("event_status") or "completed")

        row = [scenario, model, local_status, tokens_str, discount_str, latency_str, outcome]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def evaluate_telemetry_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Validate that local cache and provider KV cache are cleanly decoupled."""
    local_status = receipt.get("cache_local_status") or receipt.get("mapper_cache", {}).get("status")
    provider_tokens = receipt.get("cache_provider_tokens")
    if provider_tokens is None and isinstance(receipt.get("provider_prompt_cache"), dict):
        provider_tokens = receipt["provider_prompt_cache"].get("cache_read_tokens")

    prompt_details = receipt.get("usage", {}).get("prompt_tokens_details") or {}
    reported_cached = prompt_details.get("cached_tokens")

    # Invariant: local cache hit MUST NOT force provider cached tokens if reported 0
    if reported_cached == 0 and provider_tokens not in (0, None):
        return {
            "valid": False,
            "reason": "provider_tokens_fabricated_from_local_hit",
            "local_status": local_status,
            "provider_tokens": provider_tokens,
        }

    return {
        "valid": True,
        "local_status": local_status,
        "provider_tokens": provider_tokens or 0,
        "discount_usd": receipt.get("cache_provider_discount_usd") or 0.0,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simplicio Cache Telemetry Synthesis Benchmark")
    parser.add_argument("--receipts", type=Path, help="Path to JSON/JSONL receipts file")
    parser.add_argument("--table", action="store_true", help="Print Markdown synthesis table")
    parser.add_argument("--output", type=Path, help="Write synthesis output to file")
    args = parser.parse_args(argv)

    records: list[dict[str, Any]] = []
    if args.receipts and args.receipts.exists():
        text = args.receipts.read_text(encoding="utf-8").strip()
        if text.startswith("["):
            records = json.loads(text)
        else:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    records.append(json.loads(line))

    table_md = format_cache_telemetry_table(records)
    if args.table or not args.output:
        print(table_md)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(table_md + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
