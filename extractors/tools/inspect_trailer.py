with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    f.seek(0, 2)
    size = f.tell()
    f.seek(-4096, 2)
    trailer = f.read(4096)

print("File size:", size)
print("Last 256 bytes:", trailer[-256:])
