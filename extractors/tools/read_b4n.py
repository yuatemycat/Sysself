with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    f.seek(247272367)
    txt = f.read(5000).decode("utf-8", errors="ignore")

print(txt[:3000])
