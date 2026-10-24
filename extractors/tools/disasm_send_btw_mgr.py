#!/usr/bin/env python3
import capstone
import struct

agy_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe"
with open(agy_path, "rb") as f:
    data = f.read()

# SendBtwQuestion was at 0x1430be420, Raw offset: 0x30bda20
raw_off = 0x30bda20
va_base = 0x1430be420

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
chunk = data[raw_off:raw_off+500]
for ins in md.disasm(chunk, va_base):
    print(f"  0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
