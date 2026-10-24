import os
import re

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

pattern = re.compile(rb'template__[a-zA-Z0-9_]+')
matches = set(pattern.findall(data))
print(f"Found {len(matches)} template__ keys:")
for m in sorted(matches):
    print(" ", m.decode("latin-1"))

pattern2 = re.compile(rb'"template__[^"]+"')
matches2 = set(pattern2.findall(data))
print(f"\nFound {len(matches2)} quoted template__ keys:")
for m in sorted(matches2):
    print(" ", m.decode("latin-1"))
