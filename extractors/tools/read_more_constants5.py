with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    f.seek(247272367 + 14000)
    txt = f.read(4500).decode("utf-8", errors="ignore")

print(txt[:3000])
