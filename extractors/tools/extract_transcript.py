import json
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding='utf-8')

transcript_path = Path(r"C:/Users/X/.gemini/antigravity-cli/brain/ab4dfa29-1967-488c-806d-95cfbe5bcafd/.system_generated/logs/transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            step_idx = data.get("step_index")
            source = data.get("source")
            msg_type = data.get("type")
            content = data.get("content")
            if step_idx and step_idx >= 180:
                if msg_type == "USER_INPUT":
                    print(f"\n[USER step {step_idx}]: {content[:300]}")
                elif msg_type == "PLANNER_RESPONSE" and content:
                    print(f"\n[ASSISTANT step {step_idx}]: {content[:300]}")

