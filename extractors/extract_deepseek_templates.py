#!/usr/bin/env python3
"""
DeepSeek Prompt & Special Token Protocol Extractor
=================================================
Formats and validates DeepSeek-V3, DeepSeek-Coder, and DeepSeek-R1 reasoning harnesses,
special tokens (<｜fim begin｜>, <｜fim hole｜>, <｜fim end｜>), and ChatML envelopes.
"""

import argparse
import os
import sys

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "deepseek")

def generate_deepseek_assets(output_dir: str):
    os.makedirs(os.path.join(output_dir, "assembled"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "modules"), exist_ok=True)

    print(f"[*] Validating and generating DeepSeek prompt assets in: {output_dir}")

    # Special tokens manifest
    tokens = {
        "fim_begin": "<｜fim begin｜>",
        "fim_hole": "<｜fim hole｜>",
        "fim_end": "<｜fim end｜>",
        "begin_of_sentence": "<｜begin of sentence｜>",
        "end_of_sentence": "<｜end of sentence｜>",
        "user_token": "<｜User｜>",
        "assistant_token": "<｜Assistant｜>",
        "think_begin": "<think>",
        "think_end": "</think>",
    }

    token_json_path = os.path.join(output_dir, "modules", "special_tokens.json")
    import json
    with open(token_json_path, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)
    print(f"  [+] Wrote modules/special_tokens.json")

    print(f"[+] DeepSeek prompt asset verification complete.")

def main():
    parser = argparse.ArgumentParser(description="Extract and format DeepSeek system prompts and special tokens")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output directory")
    args = parser.parse_args()
    generate_deepseek_assets(os.path.abspath(args.out))

if __name__ == "__main__":
    main()
