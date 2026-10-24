import os

with open("scratch/claude_prompts/cli_intro_251956604.txt", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

pos = 2217434
start = max(0, pos - 500)
end = min(len(code), pos + 30000)

snippet = code[start:end]

with open("scratch/claude_prompts/claude_system_prompt_full.txt", "w", encoding="utf-8") as out:
    out.write(snippet)

print(f"Written {len(snippet)} chars to scratch/claude_prompts/claude_system_prompt_full.txt")
