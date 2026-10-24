#!/usr/bin/env python3
import os

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

prefixes = [
    b"third_party/jetski/cli/store",
    b"third_party/jetski/cli/model",
    b"third_party/jetski/cli/backend",
    b"third_party/jetski/cli/commands",
]

found = []
for p in prefixes:
    pos = 0
    while True:
        idx = data.find(p, pos)
        if idx == -1:
            break
        # Read null-terminated string
        end = data.find(b"\x00", idx)
        if end != -1 and end - idx < 200:
            sym = data[idx:end].decode("latin-1", errors="ignore")
            if "btw" in sym.lower():
                found.append(sym)
        pos = idx + len(p)

for item in sorted(list(set(found))):
    print(item)
