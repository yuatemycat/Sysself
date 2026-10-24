#!/usr/bin/env python3
"""
Sysself CLI - System Prompt & Ruleset Management Suite
======================================================
Unified tool for extracting, verifying, and managing official agent system prompts
and engineering invariant rulesets across Antigravity CLI and Claude Code.
"""

import argparse
import glob
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_binary_paths():
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\X\AppData\Local")
    
    # 1. Antigravity CLI candidates
    agy_candidates = [
        os.path.join(local_app_data, "agy", "bin", "agy.exe"),
        os.path.join(r"E:\03_Devops", "agy", "bin", "agy.exe"),
    ]
    agy_pristine = sorted(
        glob.glob(os.path.join(local_app_data, "agy", "bin", "agy.exe.bak*pristine")),
        key=os.path.getmtime,
        reverse=True
    )
    if agy_pristine:
        agy_candidates.insert(0, agy_pristine[0])

    # 2. Claude Code candidates
    claude_candidates = [
        os.path.expanduser(r"~\.local\bin\claude.exe"),
        os.path.join(local_app_data, r"Programs\Claude\claude.exe"),
        os.path.join(r"E:\03_Devops", "claude", "bin", "claude.exe"),
    ]

    agy_path = next((p for p in agy_candidates if os.path.isfile(p)), None)
    claude_path = next((p for p in claude_candidates if os.path.isfile(p)), None)

    return agy_path, claude_path

def cmd_status(args):
    print("==================================================")
    print("  Sysself System Prompt & Ruleset Workspace Status")
    print("==================================================")
    
    agy_bin, claude_bin = get_binary_paths()
    print(f"\n[+] Local Binaries:")
    print(f"  - Antigravity CLI (agy): {agy_bin or 'NOT FOUND'}")
    print(f"  - Claude Code CLI      : {claude_bin or 'NOT FOUND'}")

    agy_tmpls = glob.glob(os.path.join(BASE_DIR, "prompts", "antigravity", "templates", "*.tmpl"))
    claude_mods = glob.glob(os.path.join(BASE_DIR, "prompts", "claude_code", "modules", "*.md"))
    claude_raws = glob.glob(os.path.join(BASE_DIR, "prompts", "claude_code", "raw", "*.txt"))
    rules_files = glob.glob(os.path.join(BASE_DIR, "rules", "*.md"))
    extract_tools = glob.glob(os.path.join(BASE_DIR, "extractors", "tools", "*.py"))

    print(f"\n[+] Repository Inventory:")
    print(f"  - Antigravity Templates : {len(agy_tmpls)} files")
    print(f"  - Claude Code Modules   : {len(claude_mods)} files")
    print(f"  - Claude Code Raw Texts : {len(claude_raws)} files")
    print(f"  - Invariant Rulesets    : {len(rules_files)} files")
    print(f"  - Extraction Tools      : {len(extract_tools)} scripts")
    print("\n[OK] Workspace is healthy and synchronized.")

def cmd_extract(args):
    target = args.target.lower()
    agy_bin, claude_bin = get_binary_paths()

    if target in ("agy", "all"):
        bin_path = args.bin or agy_bin
        if not bin_path or not os.path.isfile(bin_path):
            print("[-] Error: agy.exe not found. Specify via --bin <path>", file=sys.stderr)
            if target != "all":
                sys.exit(1)
        else:
            script = os.path.join(BASE_DIR, "extractors", "extract_agy_templates.py")
            out_dir = os.path.join(BASE_DIR, "prompts", "antigravity", "templates")
            print(f"[*] Extracting Antigravity templates from: {bin_path}")
            res = subprocess.run([sys.executable, script, "--bin", bin_path, "--out", out_dir])
            if res.returncode != 0:
                print("[-] Failed to extract Antigravity templates.", file=sys.stderr)

    if target in ("claude", "all"):
        bin_path = args.bin or claude_bin
        if not bin_path or not os.path.isfile(bin_path):
            print("[-] Error: claude.exe not found. Specify via --bin <path>", file=sys.stderr)
            if target != "all":
                sys.exit(1)
        else:
            script = os.path.join(BASE_DIR, "extractors", "extract_claude_templates.py")
            out_dir = os.path.join(BASE_DIR, "prompts", "claude_code", "modules")
            print(f"[*] Extracting Claude Code templates from: {bin_path}")
            res = subprocess.run([sys.executable, script, "--bin", bin_path, "--out", out_dir])
            if res.returncode != 0:
                print("[-] Failed to extract Claude Code templates.", file=sys.stderr)

def cmd_rules(args):
    print("==================================================")
    print("  Authoritative Engineering Invariant Rulesets")
    print("==================================================")
    rules_dir = os.path.join(BASE_DIR, "rules")
    for f in sorted(glob.glob(os.path.join(rules_dir, "*.md"))):
        name = os.path.basename(f)
        with open(f, "r", encoding="utf-8", errors="ignore") as r_f:
            first_line = r_f.readline().strip().lstrip("#").strip()
        print(f"  - {name:48s} : {first_line}")

def main():
    parser = argparse.ArgumentParser(
        description="Sysself CLI: System Prompts & Invariants Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Status
    subparsers.add_parser("status", help="Show workspace status and binary inventory")

    # Extract
    extract_parser = subparsers.add_parser("extract", help="Run binary extractors")
    extract_parser.add_argument("target", choices=["agy", "claude", "all"], help="Extraction target")
    extract_parser.add_argument("--bin", help="Explicit path to target binary (.exe)")

    # Rules
    subparsers.add_parser("rules", help="List and verify engineering rulesets")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        cmd_status(args)
    elif args.command == "extract":
        cmd_extract(args)
    elif args.command == "rules":
        cmd_rules(args)

if __name__ == "__main__":
    main()
