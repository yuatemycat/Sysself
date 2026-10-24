#!/usr/bin/env python3
import capstone
import struct

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

pcln_magic = b"\xf1\xff\xff\xff\x00\x00"
pos = data.find(pcln_magic)
words = struct.unpack_from("<16Q", data, pos)
func_names_base = pos + words[4]
pcln_offset = words[8]
func_tab = pos + pcln_offset
nfunc = words[1]

e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
opt_hdr_offset = e_lfanew + 24
image_base = struct.unpack_from("<Q", data, opt_hdr_offset + 24)[0]
text_base = image_base + 0x1000

num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
opt_hdr_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
sec_tbl_offset = opt_hdr_offset + opt_hdr_size
sections = []
for i in range(num_sections):
    sec = data[sec_tbl_offset + i*40 : sec_tbl_offset + (i+1)*40]
    vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
    sections.append({"va": image_base + vaddr, "vsize": vsize, "raw": raw_ptr, "raw_size": raw_size})

def va_to_raw(va):
    for s in sections:
        if s["va"] <= va < s["va"] + s["vsize"]:
            return s["raw"] + (va - s["va"])
    return None

target_va = None
for i in range(nfunc):
    entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
    info_ptr = pos + pcln_offset + func_info_off
    n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
    end = data.find(b"\x00", func_names_base + n_off)
    fname = data[func_names_base + n_off:end].decode("latin-1", errors="ignore")
    if fname.endswith("SendSideQuestion"):
        target_va = text_base + entry_off
        break

print("SendSideQuestion VA:", hex(target_va) if target_va else "none")
raw_off = va_to_raw(target_va)
print("Raw off:", hex(raw_off))

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
chunk = data[raw_off:raw_off+400]
for ins in md.disasm(chunk, target_va):
    print(f"  0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
