from pathlib import Path

p1 = Path(r"E:\02_Projects\Intra-farm\scratch\libg_17381_reconstructed.so")
p2 = Path(r"E:\02_Projects\Intra-farm\Optimumu\libg_17381_reconstructed.so")

with open(p1, "rb") as f:
    b1 = f.read()

with open(p2, "rb") as f:
    b2 = f.read()

print(f"p1 size: {len(b1):,}")
print(f"p2 size: {len(b2):,}")
print(f"p1 == p2? {b1 == b2}")

offset = 0x15f5fb0
print(f"b1 at 0x{offset:x}: {b1[offset:offset+16].hex()}")
print(f"b2 at 0x{offset:x}: {b2[offset:offset+16].hex()}")

# Let's also check dynamic section for DT_INIT
# DT_INIT tag is 12 (0xc)
e_dyn_off = 0x015fca68
e_dyn_sz = 0x260
print("\nDynamic tags:")
import struct
for i in range(0, e_dyn_sz, 16):
    d_tag, d_val = struct.unpack_from("<qq", b1, e_dyn_off + i)
    if d_tag == 0:
        break
    tag_names = {1: "DT_NEEDED", 4: "DT_HASH", 5: "DT_STRTAB", 6: "DT_SYMTAB", 10: "DT_STRSZ", 11: "DT_SYMENT", 12: "DT_INIT", 13: "DT_FINI", 14: "DT_SONAME", 25: "DT_INIT_ARRAY", 26: "DT_FINI_ARRAY", 27: "DT_INIT_ARRAYSZ", 28: "DT_FINI_ARRAYSZ"}
    name = tag_names.get(d_tag, f"0x{d_tag:x}")
    if d_tag in (12, 13, 25, 26, 27, 28):
        print(f"  {name:16s} val=0x{d_val:x}")
