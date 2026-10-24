#!/usr/bin/env python3
import re

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

matches = re.findall(b'[a-zA-Z0-9_/.]*Btw[a-zA-Z0-9_/.]*|[a-zA-Z0-9_/.]*btw[a-zA-Z0-9_/.]*', data)
unique = sorted(list(set(matches)))
for u in unique:
    try:
        s = u.decode('utf-8')
        if any(c in s for c in ['commands', 'ui', 'cortex', 'slash', 'session', 'btw']):
            print(s)
    except Exception:
        pass
