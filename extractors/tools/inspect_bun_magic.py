import struct

with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    data = f.read()

# Bun magic is 0x0a4ad2fa (\xfa\xd2J\n)
magic = b'\xfa\xd2\x4a\x0a'
pos = 0
magic_positions = []
while True:
    pos = data.find(magic, pos)
    if pos == -1:
        break
    magic_positions.append(pos)
    pos += 4

print("Magic positions:", [hex(p) for p in magic_positions])
for p in magic_positions:
    print(f"At {hex(p)}: {data[p:p+64]}")
