# Antigravity Runtime, CLI & Model Invariants

## 1. CLI Protobuf Parsing Safeguard (Leading Brackets Bug)
- **Invariant**: Never format prompts, injected file headers, task briefs, or tool inputs starting with a naked square bracket `[` at `line 1:1`.
- **Root Cause**: The Antigravity CLI (`agy`) and Antigravity 2.0 Go agent executor parse message envelopes using `protojson`. When the top-level string begins with `[`, the Go protobuf deserializer crashes with `proto: syntax error (line 1:1): unexpected token [` (expecting an object root `{`).
- **Remediation**:
  - Always prefix bracketed headers with plain text or Markdown (e.g., `Task: [TAG ...]` instead of `[TAG ...]`).
  - Wrap bracketed content in code fences (`` `[...]` `` or ` ```[...]``` `).

## 2. Model Selection & Agent Workflow Hierarchy
- **Flagship Reasoning / Architecture**:
  - Use `claude-opus-4-6-thinking` for deep architectural refactoring, complex bug diagnosis, and strategic planning.
  - SOTA coding model with full reasoning token capture and verified upstream stability.
- **Fast Tool Calling & Autonomous Execution**:
  - Use `gemini-3.8-flash-high` or `claude-sonnet-4-6`.
  - Zero-glitch tool execution, fast multi-turn responses, and robust schema compliance.
- **Unstable Model Guardrail**:
  - **Do NOT** select or route autonomous coding sessions to `gemini-3.1-pro-high` or `gemini-pro-agent`.
  - The upstream `gemini-pro-agent` checkpoint currently has mismatched function-calling schemas (hallucinating `filePath` instead of `AbsolutePath`) and frequently loops emitting fallback text `"task ready"` without firing tool calls.

## 3. High-Throughput Flash Routing (Tiered vs. Canary)
- **Canary Slowdown Avoidance**:
  - Google CloudCode internally routes unpinned Gemini 3.8 requests to `-n` canary nodes, which suffer an 88% throughput collapse (from ~648 tok/s down to ~79 tok/s).
  - In Antigravity Manager, `gemini-3.8-flash-high` is transparently mapped to `gemini-3.8-flash-tiered` to lock execution to Google's dedicated production cluster while maintaining maximum unconstrained reasoning depth (`thinkingBudget: -1`).
- **Frontier Aliases**:
  - `gemini-argon`, `gemini-4-argon`, and `gemini-omni-1.1-flash` are forward-compatible gateway aliases that route to `gemini-3.8-flash-tiered` until Google enables dedicated standalone endpoints.

## 4. Enterprise Gateway & Quota Operating Principles
- **Enterprise Mode Activation**:
  - When `AGY_LLM_GATEWAY_URL` (`http://127.0.0.1:8045`) and `AGY_LLM_GATEWAY_API_KEY` are present in User environment variables, Antigravity 2.0 and `agy` automatically operate in *Enterprise Gateway* mode without requiring Google OAuth login.
- **Quota Pooling**:
  - Client-side token paywalls and quota countdowns are disabled.
  - Rate limiting is managed upstream by Antigravity Manager's dynamic rotation across authorized Google accounts (with 5-hour rolling recovery windows and automated cooldowns).

## 5. Conversation Telemetry & Reasoning Trace Invariants
- **Session Telemetry Architecture**:
  - **Full Transcripts**: Located at `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript_full.jsonl` (NDJSON format containing step indices, token counts, timestamps, and model thought summaries).
  - **State Database**: Located at `<appDataDir>\conversations\<conversation-id>.db` (SQLite containing protobuf-serialized `steps`, `gen_metadata`, and `trajectory_metadata_blob`).
  - **Session Annotations & Locks**: `<appDataDir>\annotations\<conv-id>.pbtxt` (titles) and `<appDataDir>\presence\<conv-id>.lock`.
- **Reasoning Token Accounting & Thought Truncation**:
  - `output_tokens` reports total generation tokens (internal chain-of-thought reasoning tokens + user-visible response tokens).
  - The plaintext `thinking` field in logs and `step_payload` often stores only a condensed summary or an initial reasoning prefix, rather than the entire raw internal token sequence.
  - When a thinking trace ends abruptly mid-deliberation, token accounting (`output_tokens > len(content) + len(thinking)`) indicates the backend logger truncated or distilled the raw thought tokens before persistence.

