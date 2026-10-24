import os
import struct

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

# PE info
e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
opt_hdr_offset = e_lfanew + 24
image_base = struct.unpack_from("<Q", data, opt_hdr_offset + 24)[0]
num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
opt_hdr_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
sec_tbl = opt_hdr_offset + opt_hdr_size

def raw_to_va(raw):
    for i in range(num_sections):
        sec = data[sec_tbl + i*40 : sec_tbl + (i+1)*40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        if raw_ptr <= raw < raw_ptr + raw_size:
            return image_base + vaddr + (raw - raw_ptr)
    return None

def va_to_raw(va):
    for i in range(num_sections):
        sec = data[sec_tbl + i*40 : sec_tbl + (i+1)*40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        if image_base + vaddr <= va < image_base + vaddr + vsize:
            return raw_ptr + (va - (image_base + vaddr))
    return None

# Known template filenames
known_templates = [
    "identity.tmpl",
    "artifacts.tmpl",
    "guidelines.tmpl",
    "communication_style.tmpl",
    "slash_commands.tmpl",
    "skills.tmpl",
    "plugins.tmpl",
    "persistent_context.tmpl",
    "conversation_transcript.tmpl",
    "function_call.tmpl",
    "ephemeral_message.tmpl",
    "async_termination_rule.tmpl",
]

# For each known template, let's find its name string in data, and then find references to it
results = {}

for tmpl in known_templates:
    b_tmpl = tmpl.encode("utf-8")
    # find where b_tmpl appears
    pos = 0
    tmpl_offsets = []
    while True:
        pos = data.find(b_tmpl, pos)
        if pos == -1: break
        tmpl_offsets.append(pos)
        pos += len(b_tmpl)
    
    print(f"\n=== Searching for {tmpl} (found {len(tmpl_offsets)} occurrences) ===")
    for raw_pos in tmpl_offsets:
        # Check if this occurrence is part of a longer path
        # In embed.FS, the name might be "system_prompts/identity.tmpl" or "templates/system_prompts/identity.tmpl"
        # Let's find string start (backwards)
        s_start = raw_pos
        while s_start > 0 and data[s_start-1] >= 0x20 and chr(data[s_start-1]) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_/-.":
            s_start -= 1
        s_end = raw_pos + len(b_tmpl)
        full_name = data[s_start:s_end].decode("latin-1")
        name_len = len(full_name)
        name_va = raw_to_va(s_start)
        
        # Now search for Go string header (name_va, name_len)
        pat = struct.pack("<QQ", name_va, name_len)
        hdr_pos = 0
        while True:
            hdr_pos = data.find(pat, hdr_pos)
            if hdr_pos == -1: break
            # In embed.file struct:
            # type file struct { name string; data string; hash [16]byte } (or embed.file layout)
            # hdr_pos is offset of (name_va, name_len)
            # data string should be right after: (data_va, data_len) at hdr_pos + 16
            data_va, data_len = struct.unpack_from("<QQ", data, hdr_pos + 16)
            data_raw = va_to_raw(data_va)
            if data_raw and 0 < data_len < 1000000 and data_raw + data_len <= len(data):
                content = data[data_raw:data_raw+data_len].decode("utf-8", errors="ignore")
                # Check if it looks like a template
                if any(k in content for k in ["{{", "You are", "Antigravity", "Artifact", "guidelines", "concise"]):
                    print(f"FOUND MATCH for {tmpl} via {full_name} (data_len={data_len})!")
                    results[full_name] = content
                    break
            hdr_pos += 8

print(f"\nTotal extracted templates: {len(results)}")
os.makedirs("scratch/extracted_templates", exist_ok=True)
for name, content in results.items():
    clean_name = name.replace("/", "_").replace("\\", "_")
    out_file = f"scratch/extracted_templates/{clean_name}"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {out_file} ({len(content)} chars)")

