import os
import struct
import capstone

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

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

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
func_va = 0x142197ae0
func_raw = va_to_raw(func_va)
code = data[func_raw:func_raw+0x500]

found_sections = []
for insn in md.disasm(code, func_va):
    if insn.mnemonic == 'lea' and 'rip' in insn.op_str:
        op = insn.op_str
        inside = op[op.find('[')+1 : op.find(']')]
        parts = [p.strip() for p in inside.split('+')]
        if len(parts) == 2 and parts[0] == 'rip':
            disp = int(parts[1], 16)
            ref_va = insn.address + insn.size + disp
            ref_raw = va_to_raw(ref_va)
            if ref_raw and 0 <= ref_raw < len(data):
                s_end = ref_raw
                while s_end < len(data) and 0x20 <= data[s_end] <= 0x7e:
                    s_end += 1
                if s_end - ref_raw >= 2:
                    s = data[ref_raw:s_end].decode("latin-1")
                    found_sections.append((insn.address, ref_va, s))

print(f"Discovered {len(found_sections)} registered section strings in systemprompt.init:")
for addr, va, s in found_sections:
    print(f"  {addr:#x} -> {s[:40]}")
