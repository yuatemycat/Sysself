import os
import struct

pristine_path = r"C:\Users\X\AppData\Local\agy\bin\agy.exe.bak_v143_pristine"
with open(pristine_path, "rb") as f:
    data = f.read()

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

ENTRY_SIZE = 48 # 0x30 bytes: name(16) + data(16) + hash(16)

os.makedirs("scratch/extracted_templates", exist_ok=True)

# Scan from 0x4345a28 to 0x4345e60
entries = []
for pos in range(0x4345a28, 0x4345ea0, ENTRY_SIZE):
    n_va, n_len = struct.unpack_from("<QQ", data, pos)
    d_va, d_len = struct.unpack_from("<QQ", data, pos + 16)
    n_raw = va_to_raw(n_va)
    d_raw = va_to_raw(d_va)
    if n_raw and 0 < n_len < 200:
        name = data[n_raw:n_raw+n_len].decode("latin-1", errors="ignore")
        content = ""
        if d_raw and 0 <= d_len < 2000000:
            content = data[d_raw:d_raw+d_len].decode("utf-8", errors="ignore")
        
        # Subdirectory entries have d_len == 0 or no .tmpl
        is_file = name.endswith(".tmpl")
        clean_name = name.replace("google3/third_party/jetski/prompt/template_provider/templates/", "").replace("/", "__")
        if is_file:
            out_file = f"scratch/extracted_templates/{clean_name}"
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(content)
            print(f"File [{pos:#010x}]: {name} -> {out_file} ({d_len} bytes)")
            entries.append((clean_name, d_len, content))
        else:
            print(f"Dir  [{pos:#010x}]: {name}")

print(f"\nExtracted {len(entries)} template files successfully!")
