# Official System Prompts & Assembly Manifest

This directory contains pristine, decompiled, and extracted system prompts and templates from next-generation AI coding agents.

```mermaid
graph TD
    A["Sysself System Prompts"] --> B["Antigravity / Gemini (Google DeepMind)"]
    A --> C["Claude Code (Anthropic)"]
    A --> D["Grok CLI / Grok Build (xAI)"]
    
    B --> B1["templates/ (*.tmpl Go embed.FS)"]
    B --> B2["assembled/ (full_system_prompt.md)"]
    
    C --> C1["modules/ (00 to 12 Markdown Sections)"]
    C --> C2["raw/ (Raw JavaScript Bun Strings)"]
    C --> C3["assembled/ (full_system_prompt.md)"]

    D --> D1["modules/ (00 to 10 XML Tag Sections)"]
    D --> D2["bundled_agents/ & personas/ (explore, plan, implementer)"]
    D --> D3["assembled/ (full_system_prompt.md & subagent)"]
```

## Directory Structure

- **`antigravity/`**:
  - `templates/`: 17 Go `text/template` files extracted directly from `agy.exe` (`embed.FS`).
  - `assembled/`: Fully composed runtime prompt used in active Antigravity 2.0 agent sessions.
- **`claude_code/`**:
  - `modules/`: Modular breakdown of the Claude Code prompt (13 core components).
  - `raw/`: Unprocessed extracted chunks and JS string literals from `claude.exe` (`.bun` bundle).
  - `assembled/`: Complete, unified Claude Code system prompt.
- **`grok/`**:
  - `modules/`: Semantic breakdown of Grok 4.7 XML policy sections (`<dangerous_actions>`, `<work_policy>`, `<memory>`, `<communication>`, etc.).
  - `bundled_agents/` & `personas/`: Native xAI agents (`explore.md`, `plan.md`, `general-purpose.md`) and TOML personas.
  - `raw/`: Complete session prompts and canonical `tool_definitions.json`.
  - `assembled/`: Unified interactive and subagent worker prompts.
