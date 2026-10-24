import os
import re

EXE_PATH = r"C:\Users\X\.local\bin\claude.exe"

with open(EXE_PATH, "rb") as f:
    data = f.read()

print("File loaded, length:", len(data))

# Search for the JavaScript bundle where prompt logic resides.
# We know the prompt logic is located in the text containing 'You are Claude Code, Anthropic\'s official CLI for Claude.'
# Specifically in the bundle around 249MB - 254MB.
pos = data.find(b"You are Claude Code, Anthropic's official CLI for Claude.")
print(f"First match: {pos} ({hex(pos)})")

# Let's find the boundaries of the JS chunk containing lin/Brr/Hrr/zrr
pos_brr = data.find(b"function Brr(){return`# Executing actions with care")
print(f"Brr match: {pos_brr} ({hex(pos_brr)})")

pos_opi = data.find(b"You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers.")
print(f"Opi match: {pos_opi} ({hex(pos_opi)})")

pos_subagent = data.find(b"You are an agent for Claude Code, Anthropic's official CLI for Claude.")
print(f"Subagent match: {pos_subagent} ({hex(pos_subagent)})")
