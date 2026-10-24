with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    f.seek(253410000)
    data = f.read(20000).decode("utf-8", errors="ignore")

idx = data.find("Prefer dedicated tools over")
if idx != -1:
    print(data[idx:idx+400])
