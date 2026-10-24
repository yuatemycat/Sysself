# AGENTS.md - Multi-Agent Operating Invariants

## Core Principles
1. **Tool Precedence & Paths**: Dev tools reside in `E:\03_Devops`. Projects reside in `E:\02_Projects`.
2. **Code Delivery Invariant**: Any script or patch >10 lines must be saved to a file, never dumped inline.
3. **Context Window Hygiene**: Never view large task logs without line bounds. Bounded tail reads only (`StartLine`/`EndLine`).
4. **Prompt Parity**: System prompts in `prompts/` are reference ground truths decompiled from official releases.
