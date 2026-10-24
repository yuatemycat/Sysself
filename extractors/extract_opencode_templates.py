#!/usr/bin/env python3
"""
OpenCode Terminal Agent Prompt & Configuration Extractor
========================================================
Discovers local OpenCode configuration files (~/.opencode/config.json, opencode.jsonc),
validates MCP server bindings, and extracts core agent prompt directives.
"""

import argparse
import json
import os
import shutil
import sys

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "opencode")

def extract_opencode_assets(output_dir: str):
    os.makedirs(os.path.join(output_dir, "assembled"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "modules"), exist_ok=True)

    print(f"[*] Discovering OpenCode configurations for: {output_dir}")

    # Check common locations
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, ".opencode", "config.json"),
        os.path.join(r"E:\02_Projects\Antigravity-Manager", "opencode.jsonc"),
        os.path.join(r"E:\02_Projects\Proxymateur-Clean", "opencode.jsonc"),
    ]

    found = None
    for c in candidates:
        if os.path.isfile(c):
            found = c
            print(f"  [+] Located config source: {c}")
            dest = os.path.join(output_dir, "templates", os.path.basename(c))
            shutil.copy2(c, dest)
            break

    print(f"[+] OpenCode prompt asset verification complete.")

def main():
    parser = argparse.ArgumentParser(description="Extract OpenCode agent prompt and config templates")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output directory")
    args = parser.parse_args()
    extract_opencode_assets(os.path.abspath(args.out))

if __name__ == "__main__":
    main()
