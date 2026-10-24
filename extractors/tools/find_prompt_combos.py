import os
import struct

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

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

words = struct.unpack_from("<16Q", data, raw_pcln)
nfunc = words[1]
func_names_base = raw_pcln + words[4]
pcln_offset = words[8]
func_tab = raw_pcln + pcln_offset

matches = []
for i in range(nfunc):
    entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
    info_ptr = raw_pcln + pcln_offset + func_info_off
    if info_ptr + 8 >= len(data): continue
    n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
    if 0 <= n_off and func_names_base + n_off < len(data):
        end = data.find(b"\x00", func_names_base + n_off)
        if end != -1:
            fname = data[func_names_base + n_off : end].decode("latin-1", errors="ignore")
            lower = fname.lower()
            if "promptcombination" in lower or "defaultprompt" in lower or "systemprompt" in lower:
                matches.append(fname)

print(f"Found {len(matches)} matching functions:")
for m in matches:
    print(" ", m)
