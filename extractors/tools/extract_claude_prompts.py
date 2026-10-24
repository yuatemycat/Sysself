import os

claude_path = r"C:\Users\X\.local\bin\claude.exe"

with open(claude_path, "rb") as f:
    data = f.read()

offsets = [
    ("cli_intro_130109416", 130109416),
    ("claude_code_131801568", 131801568),
    ("claude_code_249386424", 249386424),
    ("cli_intro_251956604", 251956604),
    ("claude_code_250980622", 250980622),
]

os.makedirs("scratch/claude_prompts", exist_ok=True)

for name, off in offsets:
    start = max(0, off - 1000)
    end = min(len(data), off + 8000)
    chunk = data[start:end]
    
    # Try to find string bounds (look for backticks, quotes, or null bytes)
    out_file = f"scratch/claude_prompts/{name}.txt"
    # Find printable ascii / utf-8 text around off
    p_start = off
    while p_start > 0 and data[p_start-1] >= 0x20 or data[p_start-1] in (0x09, 0x0a, 0x0d):
        p_start -= 1
    p_end = off
    while p_end < len(data) and data[p_end] >= 0x20 or data[p_end] in (0x09, 0x0a, 0x0d):
        p_end += 1
    
    text = data[p_start:p_end].decode("utf-8", errors="ignore")
    with open(out_file, "w", encoding="utf-8") as out_f:
        out_f.write(text)
    print(f"Extracted {name}: length {len(text)} chars -> {out_file}")

