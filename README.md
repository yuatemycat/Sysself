# Sysself

> **Sysself**: Authoritative System Prompts, Binary Extractors, and Engineering Invariants for Agentic AI Coding Environments.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Workspace-Synchronized-success.svg)](sysself.py)

```mermaid
flowchart TD
    subgraph Binaries["Upstream Agent Executables"]
        AGY["agy.exe (Google Antigravity CLI / Gemini)"]
        CLAUDE["claude.exe (Anthropic Claude Code)"]
        GROK["grok.exe (xAI Grok Build CLI)"]
    end

    subgraph Extractors["Sysself Extraction Suite"]
        EXT_AGY["extract_agy_templates.py (Go embed.FS)"]
        EXT_CLAUDE["extract_claude_templates.py (Bun PE)"]
        EXT_GROK["extract_grok_templates.py (Rust Runtime / XML)"]
        TOOLS["50+ Reverse Engineering Probes (tools/)"]
        CLI["sysself.py Unified CLI"]
    end

    subgraph Output["Artifact Repositories"]
        P_AGY["prompts/antigravity (17 Go .tmpl & Assembled)"]
        P_CLAUDE["prompts/claude_code (14 Modules & Raw)"]
        P_GROK["prompts/grok (11 Modules, Personas & Raw)"]
        RULES["rules/ (11 Invariant Rulesets)"]
    end

    AGY --> EXT_AGY
    CLAUDE --> EXT_CLAUDE
    GROK --> EXT_GROK
    EXT_AGY --> P_AGY
    EXT_CLAUDE --> P_CLAUDE
    EXT_GROK --> P_GROK
    CLI --> EXT_AGY
    CLI --> EXT_CLAUDE
    CLI --> EXT_GROK
```

## Quick Start

### 1. View Workspace Status
```bash
python sysself.py status
```

### 2. Extract Official Prompts
```bash
# Extract Google Antigravity / Gemini templates from agy.exe
python sysself.py extract gemini

# Extract Anthropic Claude Code modules from claude.exe
python sysself.py extract claude

# Extract xAI Grok Build prompts and personas from ~/.grok
python sysself.py extract grok

# Extract all agent suites simultaneously
python sysself.py extract all
```

### 3. Audit Engineering Rulesets
```bash
python sysself.py rules
```

---

## Directory Architecture

```
Sysself/
├── prompts/
│   ├── antigravity/            # Google DeepMind Antigravity & Gemini CLI
│   │   ├── assembled/          # Complete assembled runtime prompt
│   │   └── templates/          # 17 Go embed.FS templates (.tmpl)
│   ├── claude_code/            # Anthropic Claude Code
│   │   ├── assembled/          # Composed lin() prompt markdown
│   │   ├── modules/            # 14 decompiled functional modules
│   │   └── raw/                # Unescaped JS bundle strings & dumps
│   └── grok/                   # xAI Grok Build CLI
│       ├── assembled/          # Canonical interactive & subagent prompts
│       ├── modules/            # 11 XML tag modules (<dangerous_actions>, etc.)
│       ├── bundled_agents/     # general-purpose.md, explore.md, plan.md
│       ├── personas/           # 7 native TOML personas
│       └── raw/                # Session prompt text & tool_definitions.json
├── extractors/
│   ├── extract_agy_templates.py    # Go embed.FS 48-byte table parser
│   ├── extract_claude_templates.py # Bun standalone PE bundle parser
│   ├── extract_grok_templates.py   # Grok runtime session & XML parser
│   └── tools/                      # 50+ reverse-engineering probes
├── rules/
│   ├── developer-environment-and-toolchain-invariants.md
│   ├── android-runtime-and-emulator-invariants.md
│   ├── antigravity-runtime-and-model-invariants.md
│   ├── claude-code-and-promon-automation.md
│   ├── context-and-code-delivery-invariants.md
│   ├── cross-tool-session-handoff.md
│   ├── huggingface-hub-invariants.md
│   ├── mobile-store-listing-invariants.md
│   ├── powershell-execution.md
│   ├── windows-background-automation.md
│   └── github-repository-ruleset.json
├── sysself.py                  # Master CLI controller
├── AGENTS.md                   # Multi-agent coordination rules
├── CLAUDE.md                   # Claude Code workspace guidelines
├── GEMINI.md                   # Google Gemini / Antigravity guidelines
├── .cursorrules                # Cursor IDE ruleset
└── .windsurfrules              # Windsurf / Cascade ruleset
```

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
