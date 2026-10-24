import os

claude_path = r"C:\Users\X\.local\bin\claude.exe"

with open(claude_path, "rb") as f:
    data = f.read()

keywords = [
    b"You are Claude Code",
    b"Anthropic's official CLI",
    b"You are an interactive CLI",
    b"Claude Agent SDK",
    b"x-anthropic-billing-header",
    b"You are a Claude agent",
    b"CLAUDE_CODE",
    b"CLAUDE.md",
    b"claude-code",
    b"system-prompt",
    b"systemPrompt",
]

for kw in keywords:
    pos = 0
    matches = []
    while True:
        pos = data.find(kw, pos)
        if pos == -1: break
        matches.append(pos)
        pos += len(kw)
    print(f"Keyword '{kw.decode('latin-1')}': {len(matches)} matches: {matches[:5]}")
