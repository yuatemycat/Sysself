# Developer Environment & Toolchain Invariants

## 1. Developer Tool Location
- All developer tools, build toolchains, runtimes, SDKs, and binary analysis frameworks must be installed or placed inside `E:\03_Devops`.
- Avoid installing dev tools to default user profile locations (`C:\Users\<user>\AppData\...`), `Program Files`, or temporary directories unless specifically requested.

## 2. Environment Variables & PATH Management
- Whenever installing or configuring a tool:
  - Add its executable directory (e.g. `<tool>\bin` or `<tool>\Scripts`) to the persistent User `PATH` environment variable (`[Environment]::SetEnvironmentVariable('Path', ..., 'User')`).
  - **PATH Precedence Invariant**: Always ensure `E:\03_Devops` tool paths appear **before** `C:\Users\<user>\AppData\Local\Microsoft\WindowsApps` in the User `PATH` to prevent Windows execution alias shims from shadowing real binaries (such as `python.exe`).
  - Set relevant environment variables permanently at the User level (e.g. `JAVA_HOME`, `GHIDRA_INSTALL_DIR`).
  - **Storage-Redirection Invariant (Drive C:\ Exhaustion Prevention)**:
    - In addition to tool installation paths, always permanently set user-level cache and data redirection variables to prevent build tools and runtimes from filling `C:\Users\<user>\`:
      - `ANDROID_AVD_HOME` -> `E:\03_Devops\AndroidSdk\avd` (prevents QEMU/Android emulators from placing 40+ GB virtual disks on `C:`)
      - `GRADLE_USER_HOME` -> `E:\03_Devops\.gradle` (prevents Gradle from dumping 10-20+ GB jar/wrapper caches onto `C:`)
      - `RUSTUP_HOME` -> `E:\03_Devops\Rustup` & `CARGO_HOME` -> `E:\03_Devops\Cargo`
      - `PUB_CACHE` -> `E:\03_Devops\flutter\pub-cache`
    - **NTFS Directory Junction Safeguard**: For tools or IDEs that hardcode `%USERPROFILE%\.<tool>` and ignore environment variables, maintain an NTFS Directory Junction (`mklink /J` or `New-Item -ItemType Junction`) on `C:\` pointing to the respective directory in `E:\03_Devops\`.
  - Update `E:\03_Devops\env.ps1` and `E:\03_Devops\env.bat` so the portable environment activator scripts remain fully synchronized.

## 3. Project Workspace & Storage Invariants
- All codebases, application repositories, and active development projects must be located within `E:\02_Projects` (e.g. `E:\02_Projects\<repo-name>`).
- **Partition Space Warning (`D:\`)**: Drive `D:\` is a small (2.4 GB) FAT32 utility partition. Never clone codebases, download large dependencies, or execute native builds on `D:\`.
- When user prompts refer to "Project" or "Projects" without specifying an explicit drive or path, resolve to `E:\02_Projects`.
- **Windows CrossDevice / Phone Link Suppression**:
  - Windows 11 Cross Device Experience mirrors phone photos and downloads to `C:\Users\<user>\CrossDevice`, consuming tens of gigabytes.
  - Maintain policy flags disabling Phone Link and Mobile Devices (`EnablePhoneLink = 0`, `EnableMmx = 0` under `HKCU\Software\Policies\Microsoft\Windows\System` and `HKLM\...`), and keep `PhoneSvc` disabled. Never re-enable phone sync or recreate `CrossDevice` on drive `C:\`.
- **Rust & Native Build Artifact Hygiene (`E:\02_Projects`)**:
  - Multi-crate and Tauri projects accumulate massive intermediate compilation outputs (`target/` folders frequently exceed 40-50 GB per project).
  - When conducting disk audits or project maintenance, purge or run `cargo clean` / `flutter clean` on non-active build directories to prevent disk starvation.

## 4. Code Delivery (>10 Lines in Files) & Context Compaction Hygiene
- **Code Delivery Invariant (>10 Lines Must Be in Files)**:
  - Whenever providing, generating, or executing code snippets, scripts, patches, or Colab cells **longer than 10 lines**, **NEVER** dump them only inline in chat or inside inline shell strings (`python -c "..."` or `powershell -Command "..."`).
  - Always write code >10 lines to a concrete file and provide a clickable Markdown file link:
    - **Temporary / One-off code** (diagnostic probes, benchmark scripts, Colab cells, temporary patches): Write to `scratch/` in the active workspace.
    - **Permanent / Reusable code** (project features, deployment scripts, persistent patches): Write directly to the canonical project directory (`scripts/`, `src/`, etc.).
  - In chat responses, show only a brief 1–3 line usage command and link to the created file.
- **Task Log & Context Window Hygiene (Preventing Unwanted Auto-Compaction)**:
  - **NEVER** call `view_file` or `Read` on entire `.system_generated/tasks/*.log` files without line bounds (`StartLine`/`EndLine`), as repeated full-log reads rapidly burn 100K+ tokens and trigger back-to-back auto-compactions.
  - Prefer the `agy-context-guard` MCP tool (`tail_task_log`) or bounded tail reads (last 30–50 lines) when inspecting background task progress.
  - Use `code-review-graph` MCP tools (`semantic_search_nodes_tool`, `get_review_context_tool`, `query_graph_tool`) first before reading whole source files.
  - Pin critical session variables via `pin_session_state` or `memory` MCP so they survive `/compact` cycles with zero loss.
- **Multi-Repo Code Knowledge Graph (CRG) & Episodic Memory Hygiene**:
  - **Freshness Invariant**: Before conducting architectural reviews, impact queries, or multi-file edits in any `E:\02_Projects` repo, check graph status (`list_graph_stats_tool`). If `head_matches_build` is `false` or unbuilt, run incremental update (`build_or_update_graph_tool`).
  - **Registry Synchronization**: Ensure any active repository in `E:\02_Projects` is registered in `$env:USERPROFILE\.code-review-graph\registry.json`.

## 5. Hugging Face Hub & Cloud ML Pipeline Invariants
- **Ambient Token Authentication Invariant**:
  - Always set `os.environ["HF_TOKEN"]` and call `huggingface_hub.login(token=..., add_to_git_credential=False)` at the very top of scripts before invoking any `from_pretrained()`, `load_dataset()`, or `Trainer`.
- **Zero-Disk Duplicate Serialization**:
  - Never call `model.push_to_hub()`. Always save locally with `save_pretrained()` and stream directly via `HfApi().upload_folder()`.
- **Storage Target Invariant**:
  - In Colab/Vertex AI, always write models and caches to `/content`, never to root `/` or relative `./` paths where disk space is capped at ~14 GB.
