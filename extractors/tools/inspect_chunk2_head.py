with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    f.seek(249386424 - 1000)
    pre = f.read(1000)
    # search backwards for "//" or "chunk-" or null bytes
    print("Preceding 1000 bytes ending at 249386424:")
    print(repr(pre[-300:]))
