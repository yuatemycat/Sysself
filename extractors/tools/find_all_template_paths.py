import os
import re

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

prefix = b"google3/third_party/jetski/prompt/template_provider/templates/"
pos = 0
matches = []
while True:
    pos = data.find(prefix, pos)
    if pos == -1: break
    # Find end of string (null byte or whitespace)
    end = pos
    while end < len(data) and data[end] > 0x20:
        end += 1
    file_path = data[pos:end].decode("latin-1", errors="ignore")
    matches.append((pos, file_path))
    pos += len(prefix)

print(f"Found {len(matches)} template paths:")
seen = set()
unique_matches = []
for p, fp in matches:
    if fp not in seen:
        seen.add(fp)
        unique_matches.append((p, fp))
        print(f"  [{p:#010x}] {fp}")

with open("scratch/all_template_paths.txt", "w", encoding="utf-8") as f:
    for p, fp in unique_matches:
        f.write(f"{p:#010x}: {fp}\n")
