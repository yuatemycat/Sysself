# Sysself

> **Sysself**: Authoritative System Prompts, Binary Extractors, and Engineering Invariants for Agentic AI Coding Environments.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Workspace-Synchronized-success.svg)](sysself.py)

```mermaid
flowchart TD
    subgraph Binaries["Upstream Agent Executables"]
        AGY["agy.exe (Google Antigravity CLI)"]
        CLAUDE["claude.exe (Anthropic Claude Code)"]
    end

    subgraph Extractors["Sysself Extraction Suite"]
        EXT_AGY["extract_agy_templates.py (Go embed.FS)"]
        EXT_CLAUDE["extract_claude_templates.py (Bun PE)"]
        TOOLS["50+ Reverse Engineering Probes (tools/)"]
        CLI["sysself.py Unified CLI"]
    end

    subgraph Output["Artifact Repositories"]
        P_AGY["prompts/antigravity (17 Go .tmpl & Assembled)"]
        P_CLAUDE["prompts/claude_code (14 Modules & Raw)"]
        RULES["rules/ (11 Invariant Rulesets)"]
    end

    AGY --> EXT_AGY
    CLAUDE --> EXT_CLAUDE
    EXT_AGY --> P_AGY
    EXT_CLAUDE --> P_CLAUDE
    CLI --> EXT_AGY
    CLI --> EXT_CLAUDE
```

## Quick Start

### 1. View Workspace Status
```bash
python sysself.py status
```

### 2. Extract Official Prompts
```bash
# Extract Google Antigravity templates from agy.exe
python sysself.py extract agy

# Extract Anthropic Claude Code modules from claude.exe
python sysself.py extract claude

# Extract both simultaneously
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
│   ├── antigravity/
│   │   ├── assembled/          # Complete assembled runtime prompt
│   │   └── templates/          # 17 Go embed.FS templates (.tmpl)
│   └── claude_code/
│       ├── assembled/          # Composed lin() prompt markdown
│       ├── modules/            # 14 decompiled functional modules
│       └── raw/                # Unescaped JS bundle strings & dumps
├── extractors/
│   ├── extract_agy_templates.py    # Go embed.FS 48-byte table parser
│   ├── extract_claude_templates.py # Bun standalone PE bundle parser
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
