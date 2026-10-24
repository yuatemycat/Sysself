#!/usr/bin/env python3
import capstone
import struct

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

# Find pclntab to get StartSideQuestion function entry
pcln_magic = b"\xf1\xff\xff\xff\x00\x00"
pos = data.find(pcln_magic)
words = struct.unpack_from("<16Q", data, pos)
func_names_base = pos + words[4]
pcln_offset = words[8]
func_tab = pos + pcln_offset
nfunc = words[1]

# PE text base
e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
opt_hdr_offset = e_lfanew + 24
image_base = struct.unpack_from("<Q", data, opt_hdr_offset + 24)[0]
text_base = image_base + 0x1000

target_va = None
for i in range(nfunc):
    entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
    info_ptr = pos + pcln_offset + func_info_off
    n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
    end = data.find(b"\x00", func_names_base + n_off)
    fname = data[func_names_base + n_off:end].decode("latin-1", errors="ignore")
    if fname.endswith("StartSideQuestion"):
        target_va = text_base + entry_off
        print(f"Found {fname} at VA 0x{target_va:x}")
        break

if target_va:
    # Convert VA to file offset
    # read section headers
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_hdr_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_tbl_offset = opt_hdr_offset + opt_hdr_size
    raw_off = None
    for i in range(num_sections):
        sec = data[sec_tbl_offset + i*40 : sec_tbl_offset + (i+1)*40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        va = image_base + vaddr
        if va <= target_va < va + vsize:
            raw_off = raw_ptr + (target_va - va)
            break
    print(f"File offset: 0x{raw_off:x}")
    # Disassemble 50 instructions
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    chunk = data[raw_off:raw_off+300]
    for ins in md.disasm(chunk, target_va):
        print(f"  0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
