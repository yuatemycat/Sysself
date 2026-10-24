# Grok 4.7 CLI System Prompts & Agent Specifications

Extracted directly from the local xAI Grok Build CLI environment (`C:\Users\X\.grok`).

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
