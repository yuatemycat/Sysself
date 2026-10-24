import os

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

matches = {
    "identity_62032870": 62032870,
    "pair_prog_61811625": 61811625,
    "pair_prog_61906786": 61906786,
    "pair_prog_61940305": 61940305,
    "artifacts_63489789": 63489789,
    "guidelines_62000857": 62000857,
    "concise_62718793": 62718793,
    "slash_commands_61980395": 61980395,
    "messaging_61955654": 61955654,
    "workspaces_60031459": 60031459,
    "data_concise_171853507": 171853507,
}

for name, off in matches.items():
    # Expand backwards and forwards to find boundaries of text
    # Let's find how far UTF-8 / printable text extends
    start = off
    while start > 0 and (data[start-1] >= 0x20 or data[start-1] in (0x09, 0x0a, 0x0d)):
        start -= 1
    end = off
    while end < len(data) and (data[end] >= 0x20 or data[end] in (0x09, 0x0a, 0x0d)):
        end += 1
    
    content = data[start:end].decode('utf-8', errors='ignore')
    out_path = f"scratch/{name}.txt"
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(content)
    print(f"Extracted {name}: length {len(content)} chars -> {out_path}")
