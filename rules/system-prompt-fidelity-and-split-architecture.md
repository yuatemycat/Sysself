# System Prompt Fidelity, Split-Prompt Architecture & Wire Extraction Invariants

## 1. Strict Prompt Anti-Summarization Invariant
- **Zero-Stub Enforcement**:
  - Whenever asked to port, extract, decompile, or assemble AI agent system prompts, **NEVER** emit synthesized summaries, bulleted stubs, high-level overviews, or placeholder mocks.
  - System prompts must always be preserved **verbatim, unabridged, and full-length** (typically 500–1,500+ lines).
- **Line-Count & Byte Verification**:
  - Before declaring any prompt assembly complete, explicitly audit line counts against live wire baselines.
  - If a vendor prompt is under 100 lines, flag it immediately as an incomplete stub unless verified as a pure minimal reasoning delimiter (e.g. DeepSeek-R1 `<think>` conditioning).

## 2. The Split-Prompt Architecture Law (Binary vs. Wire)
Modern agentic developer CLI tools (Claude Code, Antigravity/Gemini, Grok CLI, Cursor Composer, Windsurf Cascade) employ a **hybrid split-prompt architecture**:
1. **Client-Side PE/ELF Binary (On Disk)**:
   - Houses local CLI execution modules, terminal formatting, tool schemas, and local subagent coordinators (e.g., `claude.exe` Bun chunks, `agy.exe` Go templates, `grok.exe` `.rdata` tables).
   - **Extractable via Static Reverse Engineering**: Superghidra, PyGhidra, binary string tables, and bytecode decompilers.
2. **Server-Side Wire Payload (In Transit)**:
   - Houses the massive core behavioral models, copyright safe-harbor rules, refusal boundaries, few-shot cases, and persistent memory (e.g., `<claude_behavior>`, `<agentic_behavior>`, Anthropic Mythos tiers).
   - **Non-Existent in the Binary**: These bytes are physically NOT in the `.exe` on disk and can **never** be recovered by Ghidra/Superghidra decompilation alone.
   - **Mandatory Wire Interception**: Must be captured over the network via transparent proxy interceptors (`sysself.py listen`), live session transcripts (`transcript_full.jsonl`), or intercepted API JSON payloads (`message.txt`, Proxymateur logs).

## 3. Runtime Subsystem Envelope Accounting
When inspecting or presenting system prompts, always distinguish between:
1. **Pure Vendor Baseline**:
   - The unadorned vendor-authored instructions (e.g., Google DeepMind's ~175-line base Antigravity prompt, Anthropic's 894-line `<claude_behavior>`).
2. **Live Session Context-Populated Envelope**:
   - The expanded 450–1,400+ line wire payload generated at runtime when dynamic subsystems are populated:
     - Active MCP server tool registries (`<mcp_servers>`)
     - Active workspace skill definitions (`<skills>`)
     - User-defined rule blocks (`<user_rules>`)
     - Workspace filesystem metadata (`<user_information>`)

## 4. Automated Transparent Sniffer Invariant
- To capture authentic in-flight system prompts without requiring manual session exports:
  - Route client CLIs through a zero-dependency transparent loopback proxy (`sysself.py listen --port 8082`).
  - Target Anthropic CLI via `$env:ANTHROPIC_BASE_URL="http://127.0.0.1:8082"`.
  - Target Antigravity / Gemini CLI via `$env:GEMINI_API_ENDPOINT="http://127.0.0.1:8082"` or `$env:AGY_LLM_GATEWAY_URL="http://127.0.0.1:8082"`.
