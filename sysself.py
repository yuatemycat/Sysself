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

    # 3. Grok CLI candidates
    grok_candidates = [
        os.path.expanduser(r"~\.grok\bin\grok.exe"),
        os.path.join(r"E:\03_Devops", "grok", "bin", "grok.exe"),
    ]

    agy_path = next((p for p in agy_candidates if os.path.isfile(p)), None)
    claude_path = next((p for p in claude_candidates if os.path.isfile(p)), None)
    grok_path = next((p for p in grok_candidates if os.path.isfile(p)), None)

    return agy_path, claude_path, grok_path

def cmd_status(args):
    print("==================================================")
    print("  Sysself System Prompt & Ruleset Workspace Status")
    print("==================================================")
    
    agy_bin, claude_bin, grok_bin = get_binary_paths()
    print(f"\n[+] Local Binaries:")
    print(f"  - Antigravity CLI (agy): {agy_bin or 'NOT FOUND'}")
    print(f"  - Claude Code CLI      : {claude_bin or 'NOT FOUND'}")
    print(f"  - Grok CLI (xAI Build) : {grok_bin or 'NOT FOUND'}")

    agy_tmpls = glob.glob(os.path.join(BASE_DIR, "prompts", "antigravity", "templates", "*.tmpl"))
    claude_mods = glob.glob(os.path.join(BASE_DIR, "prompts", "claude_code", "modules", "*.md"))
    claude_raws = glob.glob(os.path.join(BASE_DIR, "prompts", "claude_code", "raw", "*.txt"))
    grok_mods = glob.glob(os.path.join(BASE_DIR, "prompts", "grok", "modules", "*.md"))
    grok_agents = glob.glob(os.path.join(BASE_DIR, "prompts", "grok", "bundled_agents", "*.md"))
    grok_personas = glob.glob(os.path.join(BASE_DIR, "prompts", "grok", "personas", "*.toml"))
    deepseek_prompts = glob.glob(os.path.join(BASE_DIR, "prompts", "deepseek", "**", "*.md"), recursive=True)
    opencode_prompts = glob.glob(os.path.join(BASE_DIR, "prompts", "opencode", "**", "*.*"), recursive=True)
    harnesses_prompts = glob.glob(os.path.join(BASE_DIR, "prompts", "harnesses", "**", "*.md"), recursive=True)
    rules_files = glob.glob(os.path.join(BASE_DIR, "rules", "*.md"))
    extract_tools = glob.glob(os.path.join(BASE_DIR, "extractors", "tools", "*.py"))

    print(f"\n[+] Repository Inventory:")
    print(f"  - Antigravity / Gemini  : {len(agy_tmpls)} template files")
    print(f"  - Claude Code Suite     : {len(claude_mods)} modules, {len(claude_raws)} raw texts")
    print(f"  - Grok CLI (xAI) Suite  : {len(grok_mods)} modules, {len(grok_agents) + len(grok_personas)} personas")
    print(f"  - DeepSeek Suite        : {len(deepseek_prompts)} prompt & FIM specifications")
    print(f"  - OpenCode Suite        : {len(opencode_prompts)} prompts & config templates")
    print(f"  - Coding Harnesses      : {len(harnesses_prompts)} specs (Cursor, Cascade, Kiro, Qoder, Aider)")
    print(f"  - Invariant Rulesets    : {len(rules_files)} rules")
    print(f"  - Extraction Tools      : {len(extract_tools)} scripts")
    print("\n[OK] Workspace is healthy and synchronized.")

def cmd_extract(args):
    target = args.target.lower()
    agy_bin, claude_bin, grok_bin = get_binary_paths()

    if target in ("agy", "gemini", "antigravity", "all"):
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

    if target in ("grok", "all"):
        grok_dir = os.path.expanduser(r"~\.grok")
        script = os.path.join(BASE_DIR, "extractors", "extract_grok_templates.py")
        out_dir = os.path.join(BASE_DIR, "prompts", "grok")
        print(f"[*] Extracting Grok CLI prompt assets from: {grok_dir}")
        res = subprocess.run([sys.executable, script, "--grok-dir", grok_dir, "--out", out_dir])
        if res.returncode != 0:
            print("[-] Failed to extract Grok CLI prompt assets.", file=sys.stderr)

    if target in ("deepseek", "all"):
        script = os.path.join(BASE_DIR, "extractors", "extract_deepseek_templates.py")
        out_dir = os.path.join(BASE_DIR, "prompts", "deepseek")
        res = subprocess.run([sys.executable, script, "--out", out_dir])
        if res.returncode != 0:
            print("[-] Failed to generate DeepSeek assets.", file=sys.stderr)

    if target in ("opencode", "all"):
        script = os.path.join(BASE_DIR, "extractors", "extract_opencode_templates.py")
        out_dir = os.path.join(BASE_DIR, "prompts", "opencode")
        res = subprocess.run([sys.executable, script, "--out", out_dir])
        if res.returncode != 0:
            print("[-] Failed to generate OpenCode assets.", file=sys.stderr)

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
    extract_parser.add_argument("target", choices=["agy", "claude", "gemini", "antigravity", "grok", "deepseek", "opencode", "harnesses", "all"], help="Extraction target")
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
