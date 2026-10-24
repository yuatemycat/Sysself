import re

with open(r"C:\Users\X\.local\bin\claude.exe", "rb") as f:
    f.seek(250975000)
    data = f.read(15000).decode("utf-8", errors="ignore")

# Find occurrences of ht, Rn, jd in tool definitions
print("Near Opi definition:")
lines = data.split("\n")
for line in lines:
    if "Agent" in line or "SendMessage" in line or "StopAgent" in line or "Bash" in line or "Skill" in line:
        print(line[:160])
