# Claude Code & Claude Agent SDK Prompt Architecture

This directory houses the comprehensive, reverse-engineered and live-captured prompt system for Anthropic's **Claude Code CLI** (v2.1.304+) and the **Claude Agent SDK**.

---

## 1. Directory Structure

```
prompts/claude_code/
├── assembled/
│   ├── full_system_prompt.md            # Master assembled prompt (1,400+ lines: Agent SDK + CLI modules + Tool protocols)
│   ├── claude_agent_sdk_wire_prompt.md  # Official Anthropic live wire prompt (894 lines: <claude_behavior>, <agentic_behavior>, etc.)
│   └── claude_code_cli_runtime_prompt.md# CLI runtime prompt assembled from decompiled Bun bytecode (489 lines)
├── modules/                             # 13 modular functional prompt blocks from claude.exe
│   ├── 00_identities.md
│   ├── 01_main_cli_intro.md
│   ├── 02_doing_tasks.md
│   ├── 03_executing_actions_with_care.md
│   ├── 04_using_tools.md
│   ├── 05_tone_and_style.md
│   ├── 06_delivering_work.md
│   ├── 07_corrections.md
│   ├── 08_output_styles.md
│   ├── 09_coordinator_mode.md           # Full 250-line coordinator mode specification
│   ├── 10_subagent_worker.md
│   ├── 11_surfaces_and_environments.md
│   └── 12_session_guidance_and_bg.md
├── bundled_skills/                      # 98 official runtime skills & schemas from Anthropic
│   ├── public/                          # docx, pdf, pptx, xlsx, frontend-design, product-self-knowledge
│   ├── examples/                        # deep-research, mcp-builder, computer-use, canvas-design, etc.
│   ├── dataviz/                         # palette, color-formula, scripts, and validation
│   ├── cowork-plugin/                   # component-schemas, example-plugins, mcp-servers
│   └── artifacts_reference/             # design, design-system, and slide specifications
└── raw/                                 # Raw byte dumps and XML/JSON tool schemas
    ├── claude_tools_schema.xml          # 166KB JSONSchema function signatures (<functions>)
    └── claude_system_prompt_full.txt    # Minified string tables from Bun bytecode
```

---

## 2. Key Artifacts

### Master Assembled System Prompt
[`assembled/full_system_prompt.md`](assembled/full_system_prompt.md) represents the end-to-end prompt presented to Claude Opus 5.5 / Sonnet 4.5 in production CLI sessions. It unifies:
1. **Tool Invocation Protocol**: Canonical `{antml:function_calls}` syntax and parameter conventions.
2. **Behavioral Guidelines (`<claude_behavior>`)**: Refusal boundaries, copyright safe-harbor, evenhandedness, and product identity.
3. **Agentic Operation (`<agentic_behavior>`)**: Unattended task execution, research synthesis, artifact generation, and progress checkpointing.
4. **Memory Subsystem (`<user_memory>`)**: Persistent user context handling and privacy boundaries.
5. **CLI Runtime Modules**: Interactive terminal conventions, safe action blast-radius controls, coordinator delegation (`Opi()`), and subagent worker execution (`Uvs()`).

### Official Bundled Skills
The `bundled_skills/` directory contains 98 production skill definitions and reference implementations extracted from live execution environments, covering multi-modal document creation, data visualization palettes, and autonomous plugin scaffolding.
