import struct
from pathlib import Path

rec_path = Path(r"E:\02_Projects\Intra-farm\Optimumu\libg_17381_reconstructed.so")
with open(rec_path, "rb") as f:
    buf = f.read()

# Dynamic tags from earlier:
# DT_INIT_ARRAY val=0x14a6db8
# DT_INIT_ARRAYSZ val=0x12a8
# DT_INIT_ARRAYSZ / 8 = 0x12a8 / 8 = 4787 / 8 = 597 entries!

# Let's map virtual address 0x14a6db8 to file offset:
# PT_LOAD #2: off=0x013c1840 vaddr=0x013c5840 filesz=0x000e63f0 memsz=0x000e67c0
# 0x14a6db8 is inside PT_LOAD #2:
# file_offset = 0x14a6db8 - 0x013c5840 + 0x013c1840 = 0x14a6db8 - 0x4000 = 0x14a2db8.

init_array_vaddr = 0x14a6db8
init_array_offset = init_array_vaddr - 0x4000
init_array_sz = 0x12a8
num_entries = init_array_sz // 8

print(f"Reading DT_INIT_ARRAY at file offset 0x{init_array_offset:x}, size 0x{init_array_sz:x} ({num_entries} entries)...")

entries = []
for i in range(num_entries):
    val = struct.unpack_from("<Q", buf, init_array_offset + i*8)[0]
    entries.append(val)

print(f"First 10 init_array entries:")
for i in range(min(10, len(entries))):
    print(f"  [{i:3d}] 0x{entries[i]:x}")

# Find any entry ending in c40
matching = [(i, val) for i, val in enumerate(entries) if (val & 0xfff) == 0xc40]
print(f"\nEntries ending in 0xc40:")
for i, val in matching:
    print(f"  [{i:3d}] 0x{val:x} (offset: 0x{val:x})")

# Also find all entries ending in 0x*c40 or near c40
print(f"\nFirst 20 entries with their last 12 bits:")
for i in range(min(20, len(entries))):
    print(f"  [{i:3d}] 0x{entries[i]:x} (offset 0x{entries[i]:x})")

