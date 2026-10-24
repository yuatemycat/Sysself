import os

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

off = 62032690
start = max(0, off - 1000)
end = min(len(data), off + 8000)

chunk = data[start:end]

# Extract all printable substrings of length >= 10
import string
printable_chars = set(bytes(string.printable, 'ascii'))

strings = []
cur = bytearray()
for b in chunk:
    if b in printable_chars and b not in (0x0b, 0x0c):
        cur.append(b)
    else:
        if len(cur) >= 15:
            try:
                strings.append(cur.decode('utf-8', errors='ignore'))
            except Exception:
                pass
        cur = bytearray()
if len(cur) >= 15:
    strings.append(cur.decode('utf-8', errors='ignore'))

with open("scratch/extracted_strings_around_62032690.txt", "w", encoding="utf-8") as f:
    for s in strings:
        f.write(s + "\n---\n")

print(f"Extracted {len(strings)} strings")
