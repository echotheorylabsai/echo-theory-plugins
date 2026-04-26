#!/usr/bin/env python3
"""
Direct trigger check — tests whether installed skills fire for real queries.

Unlike run_eval.py (which uses a synthetic temp-command mechanism), this script
runs claude -p from the project root and detects whether the REAL installed skill
is invoked via the Skill tool. This gives accurate real-world trigger behavior.

Usage:
  python3 direct_eval.py --query-set <path> --skill-name <name> [--model <model>]
                         [--runs-per-query <n>] [--workers <n>] [--timeout <s>]
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


PROJECT_ROOT = Path("/Users/shubh/Desktop/src/echo-skills")


def run_single_query(
    query: str,
    skill_name: str,
    timeout: int,
    model: str | None = None,
) -> bool:
    """Run one query and return True if the named skill was invoked."""
    cmd = [
        "claude", "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    triggered = False
    start_time = time.time()
    buffer = ""
    pending_skill_tool = False
    accumulated_json = ""

    try:
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                remaining = process.stdout.read()
                if remaining:
                    buffer += remaining.decode("utf-8", errors="replace")
                break

            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue

            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if event.get("type") == "stream_event":
                    se = event.get("event", {})
                    se_type = se.get("type", "")

                    if se_type == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use" and cb.get("name") == "Skill":
                            pending_skill_tool = True
                            accumulated_json = ""

                    elif se_type == "content_block_delta" and pending_skill_tool:
                        delta = se.get("delta", {})
                        if delta.get("type") == "input_json_delta":
                            accumulated_json += delta.get("partial_json", "")
                            # Early return if skill name is already visible in stream
                            if f'"{skill_name}"' in accumulated_json:
                                return True

                    elif se_type == "content_block_stop" and pending_skill_tool:
                        try:
                            tool_input = json.loads(accumulated_json)
                            if tool_input.get("skill") == skill_name:
                                return True
                        except json.JSONDecodeError:
                            if skill_name in accumulated_json:
                                return True
                        pending_skill_tool = False
                        accumulated_json = ""

                    elif se_type == "message_stop":
                        return triggered

                # Fallback: full assistant message.
                # With --include-partial-messages, multiple ASSISTANT events fire as
                # the message builds up. Do NOT return on partial messages — only update
                # triggered and let the result/message_stop event end the loop.
                elif event.get("type") == "assistant":
                    for item in event.get("message", {}).get("content", []):
                        if item.get("type") == "tool_use" and item.get("name") == "Skill":
                            if item.get("input", {}).get("skill") == skill_name:
                                triggered = True

                elif event.get("type") == "result":
                    return triggered

    finally:
        if process.poll() is None:
            process.kill()
            process.wait()

    return triggered


def run_trigger_check(
    query_set: list[dict],
    skill_name: str,
    runs_per_query: int,
    num_workers: int,
    timeout: int,
    model: str | None,
    trigger_threshold: float = 0.5,
    verbose: bool = False,
) -> dict:
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_item = {}
        for item in query_set:
            for _ in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    timeout,
                    model,
                )
                future_to_item[future] = item

        query_triggers: dict[str, list[bool]] = {}
        query_meta: dict[str, dict] = {}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            q = item["query"]
            query_meta[q] = item
            query_triggers.setdefault(q, [])
            try:
                query_triggers[q].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[q].append(False)

    for q, triggers in query_triggers.items():
        item = query_meta[q]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        passed = (trigger_rate >= trigger_threshold) == should_trigger
        results.append({
            "query": q,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": passed,
            "tests_boundary": item.get("tests_boundary", ""),
        })

    passed_count = sum(1 for r in results if r["pass"])
    total = len(results)

    if verbose:
        print(f"Results: {passed_count}/{total} passed", file=sys.stderr)
        for r in results:
            status = "PASS" if r["pass"] else "FAIL"
            rate = f"{r['triggers']}/{r['runs']}"
            print(
                f"  [{status}] rate={rate} expected={r['should_trigger']}: {r['query'][:80]}",
                file=sys.stderr,
            )

    return {
        "skill_name": skill_name,
        "model": model or "default",
        "results": results,
        "summary": {
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "pass_rate": round(passed_count / total, 3) if total else 0,
            "false_negatives": sum(1 for r in results if r["should_trigger"] and not r["pass"]),
            "false_positives": sum(1 for r in results if not r["should_trigger"] and not r["pass"]),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Direct trigger check for installed skills")
    parser.add_argument("--query-set", required=True)
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--trigger-threshold", type=float, default=0.5)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", default=None, help="Write JSON result to file")
    args = parser.parse_args()

    query_set = json.loads(Path(args.query_set).read_text())
    output = run_trigger_check(
        query_set=query_set,
        skill_name=args.skill_name,
        runs_per_query=args.runs_per_query,
        num_workers=args.workers,
        timeout=args.timeout,
        model=args.model,
        trigger_threshold=args.trigger_threshold,
        verbose=args.verbose,
    )

    result_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result_json)
    else:
        print(result_json)


if __name__ == "__main__":
    main()
