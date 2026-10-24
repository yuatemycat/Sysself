import os
import struct

claude_path = r"C:\Users\X\.local\bin\claude.exe"

# Section .bun: Raw [0x072f4e00 - 0x117a2200] (164.68 MB)
bun_raw_start = 0x072f4e00
bun_raw_size = 0x117a2200 - bun_raw_start

print(f".bun section: {bun_raw_start:#x} to {bun_raw_start+bun_raw_size:#x} ({bun_raw_size} bytes)")

with open(claude_path, "rb") as f:
    f.seek(bun_raw_start)
    header = f.read(1024)

print("First 128 bytes of .bun section:")
print(header[:128])

# Check magic
# Bun standalone format usually starts with a magic or ends with a trailer at the end of the section
with open(claude_path, "rb") as f:
    f.seek(bun_raw_start + bun_raw_size - 1024)
    trailer = f.read(1024)

print("Last 128 bytes of .bun section:")
print(trailer[-128:])

