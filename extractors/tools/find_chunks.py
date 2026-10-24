import struct

with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    data = f.read()

# Search for Bun magic or filenames
# In Bun standalone compile, files often start with a manifest or table of contents
# Let's search for "root/" or "chunk-"
import re

matches = [m.start() for m in re.finditer(b'chunk-[a-z0-9]+\\.js', data)]
print(f'Found {len(matches)} chunk references')
unique_chunks = set()
for m in matches[:50]:
    unique_chunks.add(data[m:m+20].decode('latin1', errors='ignore'))
print(f'Sample chunks: {list(unique_chunks)[:10]}')
