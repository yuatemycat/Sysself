#!/usr/bin/env python3
"""
Deep extractor for concrete proof-of-usage transcript records.
Finds full tool_call entries, arguments, thinking blocks, and responses
from ~/.gemini/antigravity-cli/brain/ to showcase in documentation.
"""

import os
import json
from pathlib import Path

brain_dir = Path(os.path.expanduser("~/.gemini/antigravity-cli/brain"))

targets = {
    "subagent_hub": {
        "title": "Group 1: Multi-Agent & Subagent Hub Execution",
        "match": lambda obj: any(
            tc.get("name") in ["invoke_subagent", "manage_subagents", "send_message"]
            for tc in obj.get("tool_calls", [])
        ),
        "results": []
    },
    "programmatic_tools": {
        "title": "Group 2: Programmatic Tool Synthesis & Benchmarking",
        "match": lambda obj: any(
            "benchmark" in str(tc.get("arguments", {})).lower() or
            "perf_counter" in str(tc.get("arguments", {})).lower()
            for tc in obj.get("tool_calls", [])
        ),
        "results": []
    },
    "scheduled_tasks_v2": {
        "title": "Group 6: Scheduled Tasks v2 (Cron & Jitter Controls)",
        "match": lambda obj: any(
            tc.get("name") == "schedule"
            for tc in obj.get("tool_calls", [])
        ),
        "results": []
    },
    "cortex_and_planning": {
        "title": "Group 7: Cortex State, Direct Planning & Component Rewrite",
        "match": lambda obj: any(
            tc.get("name") in ["edit_file", "write_file"] and 
            ("ArtifactMetadata" in str(tc.get("arguments", {})) or "plan" in str(tc.get("arguments", {})).lower())
            for tc in obj.get("tool_calls", [])
        ),
        "results": []
    },
    "guardrails_safety": {
        "title": "Group 5: Safety Guardrails & Command Assessor",
        "match": lambda obj: any(
            "run_command" == tc.get("name") and
            any(w in str(tc.get("arguments", {})).lower() for w in ["powershell", "cargo", "test"])
            for tc in obj.get("tool_calls", [])
        ),
        "results": []
    }
}

for t_file in brain_dir.glob("*/.system_generated/logs/transcript.jsonl"):
    conv_id = t_file.parent.parent.parent.name
    try:
        with open(t_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                for k, v in targets.items():
                    if len(v["results"]) < 2 and v["match"](obj):
                        v["results"].append({
                            "conversation_id": conv_id,
                            "step_index": obj.get("step_index"),
                            "type": obj.get("type"),
                            "tool_calls": obj.get("tool_calls"),
                        })
    except Exception:
        continue

output_path = Path("scratch/extracted_transcript_proofs.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({k: {"title": v["title"], "results": v["results"]} for k, v in targets.items()}, f, indent=2)

print(f"Extracted transcript proofs saved to {output_path}")
for k, v in targets.items():
    print(f"{v['title']}: {len(v['results'])} proofs found")
