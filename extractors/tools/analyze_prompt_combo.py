import os
import struct

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

# Let's search for "getNamedPromptCombination" in pclntab to get its VA and raw offset
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

target_func = "google3/third_party/jetski/cortex/mixins/mixins.getNamedPromptCombination"
target_off = None
for i in range(nfunc):
    entry_off, func_info_off = struct.unpack_from("<II", data, func_tab + i * 8)
    info_ptr = raw_pcln + pcln_offset + func_info_off
    if info_ptr + 8 >= len(data): continue
    n_off = struct.unpack_from("<i", data, info_ptr + 4)[0]
    if 0 <= n_off and func_names_base + n_off < len(data):
        end = data.find(b"\x00", func_names_base + n_off)
        if end != -1:
            fname = data[func_names_base + n_off : end].decode("latin-1", errors="ignore")
            if fname == target_func:
                target_off = entry_off
                break

print(f"Function {target_func}: entry_off={target_off:#x}")

# Let's find its VA and raw offset
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

def raw_to_va(raw):
    for i in range(num_sections):
        sec = data[sec_tbl + i*40 : sec_tbl + (i+1)*40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        if raw_ptr <= raw < raw_ptr + raw_size:
            return image_base + vaddr + (raw - raw_ptr)
    return None

func_va = 0x140001000 + target_off
func_raw = va_to_raw(func_va)
print(f"func_va: {func_va:#x}, func_raw: {func_raw:#x}")

# Disassemble or search for string references inside this function
import capstone
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

# Read 4096 bytes of function code
code = data[func_raw:func_raw+4096]
strings_referenced = []
for insn in md.disasm(code, func_va):
    # Check for LEA reg, [rip + disp]
    if insn.mnemonic == 'lea' and 'rip' in insn.op_str:
        # Calculate target VA
        parts = insn.op_str.split(',')
        target = insn.address + insn.size
        # extract disp
        m = insn.op_str.split('+')
        if len(m) == 2:
            disp = int(m[1].rstrip(']').strip(), 16)
            ref_va = target + disp
            ref_raw = va_to_raw(ref_va)
            if ref_raw and 0 <= ref_raw < len(data):
                # Check if points to printable string
                s_end = ref_raw
                while s_end < len(data) and 0x20 <= data[s_end] <= 0x7e:
                    s_end += 1
                if s_end - ref_raw >= 3:
                    s = data[ref_raw:s_end].decode('latin-1')
                    strings_referenced.append((insn.address, ref_va, s))

print(f"Strings referenced in getNamedPromptCombination ({len(strings_referenced)}):")
for addr, va, s in strings_referenced:
    print(f"  {addr:#x} -> {va:#x}: {s}")

