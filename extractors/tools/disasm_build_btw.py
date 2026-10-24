#!/usr/bin/env python3
import capstone
import struct

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

raw_off = 0x2daf3a0
va_base = 0x142dafda0

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
chunk = data[raw_off:raw_off+600]
for ins in md.disasm(chunk, va_base):
    print(f"  0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
