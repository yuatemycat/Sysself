import re

with open(r'C:\Users\X\.local\bin\claude.exe', 'rb') as f:
    data = f.read()

print("File size:", len(data))

# Let's search for occurrences of:
# 1. "You are Claude Code"
# 2. "You are an agent for Claude Code"
# 3. "orchestrates software engineering tasks across multiple workers"
# 4. "Executing actions with care"
# 5. "Doing tasks"

queries = [
    b"You are Claude Code",
    b"You are an agent for Claude Code",
    b"orchestrates software engineering tasks across multiple workers",
    b"# Executing actions with care",
    b"# Doing tasks",
    b"# Tone and style",
    b"# Delivering work",
    b"# Surface",
]

for q in queries:
    matches = [m.start() for m in re.finditer(re.escape(q), data)]
    print(f"\nQuery '{q.decode()}' found at offsets:")
    for m in matches:
        print(f"  {m} ({hex(m)})")
