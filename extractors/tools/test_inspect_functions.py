with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    # Read chunk around Brr
    f.seek(253410000)
    chunk = f.read(50000).decode("utf-8", errors="ignore")

# Find Hrr
idx_hrr = chunk.find("function Hrr()")
if idx_hrr != -1:
    print("Hrr snippet:")
    print(chunk[idx_hrr:idx_hrr+800])
    print("=" * 60)

# Find Nrr
idx_nrr = chunk.find("function Nrr(")
if idx_nrr != -1:
    print("Nrr snippet:")
    print(chunk[idx_nrr:idx_nrr+800])
    print("=" * 60)

# Find Output Styles
idx_style = chunk.find('Proactive:{name:"Proactive"')
if idx_style != -1:
    print("Output style snippet:")
    print(chunk[idx_style:idx_style+800])
    print("=" * 60)
