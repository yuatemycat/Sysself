#!/usr/bin/env python3
"""
Official Grok CLI (grok.exe / Grok Build) System Prompt & Template Extractor
===========================================================================
Extracts embedded, session-delivered, and bundled system prompts, subagent workers,
personas, and tool specifications directly from the local Grok CLI runtime (~/.grok).

Extraction Targets:
- Main Interactive CLI Prompt: Grok 4.7 xAI system prompt with strict policy blocks.
- Modular Sections: <dangerous_actions>, <work_policy>, <memory>, <communication>, etc.
- Subagent Worker Prompt: Grok Build specialized subagent harness and instruction specs.
- Bundled Agents: general-purpose.md, explore.md, plan.md.
- Bundled Personas: implementer.toml, reviewer.toml, security-auditor.toml, etc.
- Tool Definitions: Canonical JSON tool signatures (run_terminal_command, grep, etc.).
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys

DEFAULT_GROK_DIR = os.path.expanduser(r"~\.grok")

def find_latest_prompts(grok_dir: str):
    sessions_root = os.path.join(grok_dir, "sessions")
    if not os.path.isdir(sessions_root):
        return None, None, None

    prompt_files = glob.glob(os.path.join(sessions_root, "*", "*", "system_prompt.txt"))
    if not prompt_files:
        return None, None, None

    interactive_prompt = None
    subagent_prompt = None
    tools_file = None

    # Sort prompt files by modification time (latest first)
    prompt_files.sort(key=os.path.getmtime, reverse=True)

    for p in prompt_files:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if not interactive_prompt and "You are Grok 4.7 released by xAI" in content:
                interactive_prompt = (p, content)
            elif not subagent_prompt and "You are a Grok Build subagent" in content:
                subagent_prompt = (p, content)
            
            # Find accompanying tool definitions
            session_dir = os.path.dirname(p)
            tool_path = os.path.join(session_dir, "tool_definitions.json")
            if not tools_file and os.path.isfile(tool_path):
                tools_file = tool_path

            if interactive_prompt and subagent_prompt and tools_file:
                break
        except Exception:
            continue

    return interactive_prompt, subagent_prompt, tools_file

def parse_xml_sections(text: str):
    """Splits the XML-tagged Grok system prompt into individual semantic modules."""
    sections = {}
    
    # 00. Identity / Intro (before first tag)
    first_tag = re.search(r"<([a-zA-Z0-9_]+)>", text)
    if first_tag:
        intro = text[:first_tag.start()].strip()
        sections["00_identity.md"] = f"# Grok 4.7 Core Identity & Objective\n\n{intro}\n"
    else:
        sections["00_identity.md"] = f"# Grok 4.7 Core Identity\n\n{text[:500]}\n"

    # Match all <tag>...</tag> blocks
    tag_matches = re.finditer(r"<([a-zA-Z0-9_]+)>\n?(.*?)\n?</\1>", text, re.DOTALL)
    
    order = [
        "dangerous_actions",
        "work_policy",
        "memory",
        "background_tasks",
        "scratch_files",
        "communication",
        "formatting",
        "user_guide",
        "browser_verification",
    ]
    
    found_tags = {}
    for m in tag_matches:
        tag_name = m.group(1)
        tag_content = m.group(2).strip()
        found_tags[tag_name] = tag_content

    for idx, tag in enumerate(order, start=1):
        if tag in found_tags:
            title = tag.replace("_", " ").title()
            filename = f"{idx:02d}_{tag}.md"
            sections[filename] = f"# Grok CLI: {title} (<{tag}>)\n\n{found_tags[tag]}\n"

    return sections

def extract_all(grok_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    raw_dir = os.path.join(output_dir, "raw")
    modules_dir = os.path.join(output_dir, "modules")
    assembled_dir = os.path.join(output_dir, "assembled")
    agents_dir = os.path.join(output_dir, "bundled_agents")
    personas_dir = os.path.join(output_dir, "personas")

    for d in (raw_dir, modules_dir, assembled_dir, agents_dir, personas_dir):
        os.makedirs(d, exist_ok=True)

    print(f"[*] Discovering Grok CLI prompt assets in: {grok_dir}")
    interactive, subagent, tools_file = find_latest_prompts(grok_dir)

    if not interactive:
        raise RuntimeError(f"Could not find interactive system_prompt.txt in {grok_dir}/sessions")

    # 1. Save Raw Assets
    with open(os.path.join(raw_dir, "system_prompt_interactive.txt"), "w", encoding="utf-8") as f:
        f.write(interactive[1])
    print(f"  [+] Wrote raw/system_prompt_interactive.txt ({len(interactive[1]):,} chars)")

    if subagent:
        with open(os.path.join(raw_dir, "system_prompt_subagent.txt"), "w", encoding="utf-8") as f:
            f.write(subagent[1])
        print(f"  [+] Wrote raw/system_prompt_subagent.txt ({len(subagent[1]):,} chars)")

    if tools_file:
        shutil.copy2(tools_file, os.path.join(raw_dir, "tool_definitions.json"))
        print(f"  [+] Copied raw/tool_definitions.json")

    # 2. Decompose into Modules
    sections = parse_xml_sections(interactive[1])
    for fname, content in sections.items():
        out_path = os.path.join(modules_dir, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [+] Wrote modules/{fname} ({len(content)} chars)")

    # If subagent prompt exists, add subagent worker module
    if subagent:
        sub_path = os.path.join(modules_dir, "10_subagent_worker.md")
        with open(sub_path, "w", encoding="utf-8") as f:
            f.write(f"# Grok Build: Subagent Worker System Prompt\n\n{subagent[1]}\n")
        print(f"  [+] Wrote modules/10_subagent_worker.md")

    # 3. Copy Bundled Agents
    bundled_agents_src = os.path.join(grok_dir, "bundled", "agents")
    if os.path.isdir(bundled_agents_src):
        for f in glob.glob(os.path.join(bundled_agents_src, "*.md")):
            shutil.copy2(f, agents_dir)
            print(f"  [+] Bundled Agent: {os.path.basename(f)}")

    # 4. Copy Bundled Personas
    bundled_personas_src = os.path.join(grok_dir, "bundled", "personas")
    if os.path.isdir(bundled_personas_src):
        for f in glob.glob(os.path.join(bundled_personas_src, "*.toml")):
            shutil.copy2(f, personas_dir)
            print(f"  [+] Bundled Persona: {os.path.basename(f)}")

    # 5. Generate Assembled Prompts
    assembled_main = f"""# Grok 4.7 CLI Official Assembled System Prompt

This document represents the fully assembled system prompt delivered to Grok 4.7 (xAI Grok Build CLI).

---

```markdown
{interactive[1].strip()}
```
"""
    with open(os.path.join(assembled_dir, "full_system_prompt.md"), "w", encoding="utf-8") as f:
        f.write(assembled_main.strip() + "\n")
    print(f"  [+] Wrote assembled/full_system_prompt.md")

    if subagent:
        assembled_sub = f"""# Grok Build Subagent Worker Assembled System Prompt

This document represents the autonomous worker system prompt delivered when spawning subagents.

---

```markdown
{subagent[1].strip()}
```
"""
        with open(os.path.join(assembled_dir, "subagent_prompt.md"), "w", encoding="utf-8") as f:
            f.write(assembled_sub.strip() + "\n")
        print(f"  [+] Wrote assembled/subagent_prompt.md")

    # 6. Generate README.md
    readme_content = f"""# Grok 4.7 CLI System Prompts & Agent Specifications

Extracted directly from the local xAI Grok Build CLI environment (`C:\\Users\\X\\.grok`).

## Architecture Overview

Grok CLI (xAI Grok Build v1.0.67+) utilizes structured XML boundary sections in its system prompt:

```mermaid
flowchart TD
    Grok["grok.exe (Rust Engine)"] --> Session["Live Session Dispatch"]
    
    Session --> Main["00_identity.md (Grok 4.7 by xAI)"]
    Session --> Actions["01_dangerous_actions.md (Destructive Approval)"]
    Session --> Policy["02_work_policy.md (Strict Requirements & Conventions)"]
    Session --> Memory["03_memory_architecture.md (Markdown Topics & Inbox)"]
    Session --> Tasks["04_background_tasks.md (Async Commands & Monitor)"]
    Session --> Scratch["05_scratch_files.md (%TEMP% File Protocol)"]
    Session --> Comm["06_communication_style.md (No AI Stock Filler / No Contrast)"]
    Session --> Format["07_formatting.md (GFM & Nested Fences)"]
    Session --> Guide["08_user_guide.md (Docs Navigation)"]
    Session --> Browser["09_browser_verification.md (Web E2E Verification)"]
    
    Session --> Subagent["10_subagent_worker.md (Subagent Worker Specification)"]
    Subagent --> Agents["bundled_agents/ (explore.md, plan.md, general-purpose.md)"]
    Subagent --> Personas["personas/ (implementer.toml, reviewer.toml, security-auditor.toml)"]
```

## Inventory

| Folder | Contents |
|---|---|
| [`modules/`](file:///E:/02_Projects/Sysself/prompts/grok/modules) | 11 semantic markdown modules decompiled from XML tags |
| [`assembled/`](file:///E:/02_Projects/Sysself/prompts/grok/assembled) | Canonical full system prompts for main session and subagents |
| [`bundled_agents/`](file:///E:/02_Projects/Sysself/prompts/grok/bundled_agents) | Pre-configured agent personas: `general-purpose.md`, `explore.md`, `plan.md` |
| [`personas/`](file:///E:/02_Projects/Sysself/prompts/grok/personas) | TOML persona definitions (`implementer`, `reviewer`, `security-auditor`) |
| [`raw/`](file:///E:/02_Projects/Sysself/prompts/grok/raw) | Raw unedited session system prompt text & `tool_definitions.json` |
"""
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content.strip() + "\n")
    print(f"  [+] Wrote prompts/grok/README.md")

    print(f"\n[+] Successfully extracted all Grok CLI prompt assets to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Extract official Grok CLI system prompts and agent specs")
    parser.add_argument("--grok-dir", default=DEFAULT_GROK_DIR, help="Path to .grok directory (default: ~/.grok)")
    parser.add_argument("--out", "--output", default="prompts/grok", help="Output directory (default: prompts/grok)")
    args = parser.parse_args()

    grok_dir = os.path.abspath(args.grok_dir)
    if not os.path.isdir(grok_dir):
        print(f"[-] Error: Grok directory not found at: {grok_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.abspath(args.out)
    extract_all(grok_dir, output_dir)

if __name__ == "__main__":
    main()
