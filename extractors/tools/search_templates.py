import os
import re

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

terms = [
    b"LINT.IfChange",
    b"LINT.ThenChange",
    b"pair programming with",
    b"USER to solve their coding task",
    b"Artifacts are special markdown",
    b"Follow these behavioral guidelines",
    b"Keep your responses concise",
    b"Slash commands are user-facing shortcuts",
    b"You are connected to a messaging system",
    b"Active Workspaces:",
    b"antigravity_identity",
    b"artifacts",
    b"guidelines",
    b"communication_style",
    b"slash_commands",
    b"messaging",
]

for term in terms:
    pos = 0
    matches = []
    while True:
        pos = data.find(term, pos)
        if pos == -1:
            break
        matches.append(pos)
        pos += len(term)
    print(f"Term '{term.decode('latin-1')}': {len(matches)} matches: {matches[:10]}")

