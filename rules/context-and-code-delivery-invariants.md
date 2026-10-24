# Context Compaction, Task Log Hygiene & Code Delivery Invariants

## 4. Code Delivery (>10 Lines in Files) & Context Compaction Hygiene
- **Code Delivery Invariant (>10 Lines Must Be in Files)**:
  - Whenever providing, generating, or executing code snippets, scripts, patches, or Colab cells **longer than 10 lines**, **NEVER** dump them only inline in chat or inside inline shell strings (`python -c "..."` or `powershell -Command "..."`).
  - Always write code >10 lines to a concrete file and provide a clickable Markdown file link:
    - **Temporary / One-off code** (diagnostic probes, benchmark scripts, Colab cells, temporary patches): Write to `scratch/` in the active workspace (or `<appDataDir>\brain\<conversation-id>\scratch\`).
    - **Permanent / Reusable code** (project features, deployment scripts, persistent patches): Write directly to the canonical project directory (`scripts/`, `src/`, etc.).
  - In chat responses, show only a brief 1–3 line usage command and link to the created file.
- **Task Log & Context Window Hygiene (Preventing Unwanted Auto-Compaction)**:
  - **NEVER** call `view_file` or `Read` on entire `.system_generated/tasks/*.log` files without line bounds (`StartLine`/`EndLine`), as repeated full-log reads rapidly burn 100K+ tokens and trigger back-to-back auto-compactions.
  - Prefer the `agy-context-guard` MCP tool (`tail_task_log`) or bounded tail reads (last 30–50 lines) when inspecting background task progress.
  - Use `code-review-graph` MCP tools (`semantic_search_nodes_tool`, `get_review_context_tool`, `query_graph_tool`) first before reading whole source files.
  - Pin critical session variables (live tunnel URLs, benchmark `tok/s`, hardware states) via `pin_session_state` (`agy-context-guard` MCP) or `memory` MCP so they survive `/compact` cycles with zero loss.
