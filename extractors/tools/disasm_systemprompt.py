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

target_funcs = [
    "google3/third_party/jetski/cortex/core/systemprompt/systemprompt.Construct",
    "google3/third_party/jetski/cortex/core/systemprompt/systemprompt.Build",
    "google3/third_party/jetski/cortex/core/systemprompt/systemprompt.init",
]

e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
opt_hdr_offset = e_lfanew + 24
image_base = struct.unpack_from("<Q", data, opt_hdr_offset + 24)[0]
num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
opt_hdr_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
sec_tbl = opt_hdr_offset + opt_hdr_size

def va_to_raw(va):
    for i in range(num_sections):
        sec = data[sec_tbl + i*40 : sec_tbl + (i+1)*40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        if image_base + vaddr <= va < image_base + vaddr + vsize:
            return raw_ptr + (va - (image_base + vaddr))
    return None

import capstone
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

for tf in target_funcs:
    for i in range(nfunc):
        entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
        info_ptr = raw_pcln + pcln_offset + func_info_off
        if info_ptr + 8 >= len(data): continue
        n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
        if 0 <= n_off and func_names_base + n_off < len(data):
            end = data.find(b"\x00", func_names_base + n_off)
            if end != -1:
                fname = data[func_names_base + n_off : end].decode("latin-1", errors="ignore")
                if fname == tf:
                    func_va = 0x140001000 + entry_off
                    func_raw = va_to_raw(func_va)
                    print(f"\nDisassembling {tf} at {func_va:#x}:")
                    code = data[func_raw:func_raw+1024]
                    for insn in md.disasm(code, func_va):
                        if insn.mnemonic == 'lea' and 'rip' in insn.op_str:
                            m = insn.op_str.split('+')
                            if len(m) == 2:
                                disp = int(m[1].rstrip(']').strip(), 16)
                                ref_va = insn.address + insn.size + disp
                                ref_raw = va_to_raw(ref_va)
                                if ref_raw and 0 <= ref_raw < len(data):
                                    s_end = ref_raw
                                    while s_end < len(data) and 0x20 <= data[s_end] <= 0x7e:
                                        s_end += 1
                                    if s_end - ref_raw >= 3:
                                        s = data[ref_raw:s_end].decode('latin-1')
                                        print(f"  {insn.address:#x}: LEA -> {ref_va:#x}: {s[:60]}")
                    break
