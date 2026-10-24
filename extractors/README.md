# Reverse Engineering & Prompt Extractor Toolchain

High-fidelity binary extractors and forensic analysis scripts designed to recover embedded system prompts, traits, and agent harnesses without executing arbitrary code or interrupting running sessions.

## Core Extractors

| Tool | Target Binary | Architecture / Packager | Extraction Method |
|---|---|---|---|
| [`extract_agy_templates.py`](file:///E:/02_Projects/Sysself/extractors/extract_agy_templates.py) | `agy.exe` (Antigravity CLI) | Go PE x86_64 (`embed.FS`) | Traverses 48-byte Go `embed.file` descriptor tables from image base |
| [`extract_claude_templates.py`](file:///E:/02_Projects/Sysself/extractors/extract_claude_templates.py) | `claude.exe` (Claude Code) | Bun Standalone Executable | Scans PE `.bun` payload and extracts JS prompt assembler functions (`lin`, `Opi`, `Uvs`) |

## Quick Usage via `sysself` CLI

```bash
# Extract Antigravity templates from default agy.exe
python sysself.py extract agy

# Extract Claude Code templates from default claude.exe
python sysself.py extract claude

# Extract both and verify integrity
python sysself.py extract all

# Check binary discovery and environment status
python sysself.py status
```

## Diagnostic & Forensic Tools (`tools/`)

The `tools/` subfolder contains 50+ specialized probes:
- `dump_claude_full_prompt.py`: Slice and isolate the unescaped 30KB Claude Code system prompt.
- `dump_systemprompt_init.py`: Disassemble `systemprompt.init` using Capstone engine to trace RIP-relative string references.
- `find_prompt_combos.py`: Scan for paired system prompt builders.
- `inspect_bun_magic.py`: Audit Bun executable trailer headers and payload boundaries.
