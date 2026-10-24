import os
import re

with open("scratch/claude_prompts/cli_intro_251956604.txt", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Search for system prompt definitions in this massive bundle
keywords = [
    "You are an interactive CLI",
    "You are Claude Code",
    "Anthropic's official CLI",
    "Doing tasks",
    "Tone and style",
]

for kw in keywords:
    pos = 0
    matches = []
    while True:
        pos = code.find(kw, pos)
        if pos == -1: break
        matches.append(pos)
        pos += len(kw)
    print(f"Keyword '{kw}': {len(matches)} matches: {matches[:5]}")

# Let's inspect the first match of "You are an interactive CLI"
if matches:
    pos = code.find("You are an interactive CLI")
    snippet = code[max(0, pos-200):min(len(code), pos+4000)]
    with open("scratch/claude_prompts/main_cli_prompt_snippet.txt", "w", encoding="utf-8") as out:
        out.write(snippet)
    print(f"Written main prompt snippet around {pos} to scratch/claude_prompts/main_cli_prompt_snippet.txt")

