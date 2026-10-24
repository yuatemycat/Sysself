import os
import struct

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

# Locate pclntab
pcln_magics = [b"\xf1\xff\xff\xff\x00\x00", b"\xf0\xff\xff\xff\x00\x00"]
raw_pcln = None
for magic in pcln_magics:
    pos = 0
    while True:
        pos = data.find(magic, pos)
        if pos == -1: break
        nfunc = struct.unpack_from("<Q", data, pos + 8)[0]
        if 1000 < nfunc < 500000:
            raw_pcln = pos
            break
        pos += 1
    if raw_pcln: break

print(f"pclntab found at {raw_pcln:#x}")
words = struct.unpack_from("<16Q", data, raw_pcln)
nfunc = words[1]
func_names_base = raw_pcln + words[4]
pcln_offset = words[8]
func_tab = raw_pcln + pcln_offset

print(f"Total functions in Go binary: {nfunc}")

prompt_funcs = []
for i in range(nfunc):
    entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
    info_ptr = raw_pcln + pcln_offset + func_info_off
    if info_ptr + 8 >= len(data): continue
    n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
    if 0 <= n_off and func_names_base + n_off < len(data):
        end = data.find(b"\x00", func_names_base + n_off)
        if end != -1:
            fname = data[func_names_base + n_off : end].decode("latin-1", errors="ignore")
            # Filter for prompt, systeminstruction, identity, instructions
            lower = fname.lower()
            if any(k in lower for k in ["prompt", "systeminstruction", "identity", "guideline", "artifacts"]):
                prompt_funcs.append((fname, entry_off))

print(f"Found {len(prompt_funcs)} matching functions:")
for fname, off in prompt_funcs[:50]:
    print(f"  {fname}")

with open("scratch/prompt_funcs.txt", "w", encoding="utf-8") as f:
    for fname, off in prompt_funcs:
        f.write(f"{fname}\n")
