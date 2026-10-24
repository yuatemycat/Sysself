# Engineering Rulesets & Workspace Invariants

Authoritative operational rulesets governing developer workstations, background automation, and multi-agent coordination.

## Rules Catalog

| Rule File | Scope | Key Invariants Enforced |
|---|---|---|
| [`developer-environment-and-toolchain-invariants.md`](file:///E:/02_Projects/Sysself/rules/developer-environment-and-toolchain-invariants.md) | Workstation Invariants | `E:\03_Devops` tool location, user PATH precedence, storage redirection (`ANDROID_AVD_HOME`, `GRADLE_USER_HOME`, `RUSTUP_HOME`, `CARGO_HOME`, `PUB_CACHE`), >10 line code delivery, bounded task logs |
| [`android-runtime-and-emulator-invariants.md`](file:///E:/02_Projects/Sysself/rules/android-runtime-and-emulator-invariants.md) | Android & QEMU | Headless emulator lifecycle, SwiftShader indirect GPU, persistent ADB daemon, cold boot cache hygiene |
| [`antigravity-runtime-and-model-invariants.md`](file:///E:/02_Projects/Sysself/rules/antigravity-runtime-and-model-invariants.md) | AGY & Models | Model tier resolution, Proxymateur proxy gateway routing, token DB protection, SQLite repair |
| [`claude-code-and-promon-automation.md`](file:///E:/02_Projects/Sysself/rules/claude-code-and-promon-automation.md) | Claude CLI | Session ledger auditing, Opus 4.8 / 5.5 model verification, Promon SHIELD bypass protocols |
| [`context-and-code-delivery-invariants.md`](file:///E:/02_Projects/Sysself/rules/context-and-code-delivery-invariants.md) | Agent Hygiene | Token exhaustion prevention, bounded tail reads (`tail_task_log`), MCP CRG code-graph lookup |
| [`cross-tool-session-handoff.md`](file:///E:/02_Projects/Sysself/rules/cross-tool-session-handoff.md) | Inter-Agent Handoff | Clean context handoff between Claude Code, Gemini CLI, and Antigravity |
| [`huggingface-hub-invariants.md`](file:///E:/02_Projects/Sysself/rules/huggingface-hub-invariants.md) | Cloud ML | Ambient token login, zero-disk duplicate serialization (`save_pretrained` + `HfApi`), `/content` target |
| [`mobile-store-listing-invariants.md`](file:///E:/02_Projects/Sysself/rules/mobile-store-listing-invariants.md) | App Distribution | Privacy policy, metadata synchronization, asset packing |
| [`powershell-execution.md`](file:///E:/02_Projects/Sysself/rules/powershell-execution.md) | Shell Security | Windows PowerShell 5.1 quoting, argument splatting, error action preferences |
| [`windows-background-automation.md`](file:///E:/02_Projects/Sysself/rules/windows-background-automation.md) | Background Tasks | Detached child process survival, no hanging stdio pipes, process tree management |
