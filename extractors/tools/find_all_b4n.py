with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    data = f.read()

import re
matches = [m.start() for m in re.finditer(b"B4n", data)]
print(f"Matches for B4n: {len(matches)}")
for m in matches[:10]:
    print(f"At {m} ({hex(m)}): {data[max(0, m-40):m+60]}")
