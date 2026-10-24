with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    f.seek(253406087 - 3000)
    data = f.read(3000).decode("utf-8", errors="ignore")

idx = data.find("B4n")
if idx != -1:
    print("Found B4n in preceding:")
    print(data[max(0, idx-50):idx+500])
else:
    print("B4n not in immediately preceding 3000 bytes")
