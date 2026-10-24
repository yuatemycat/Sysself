#!/usr/bin/env python3
"""
Official Antigravity CLI (agy.exe) System Prompt & Template Extractor
=====================================================================
Extracts embedded Go template files (`embed.FS`) directly from `agy.exe`
without running the executable or interrupting active agent sessions.

Layout Details:
- Go 1.16+ embed.FS file table entry (48 bytes):
    Offset 0:  name string  (name_ptr: uint64, name_len: uint64)
    Offset 16: data string  (data_ptr: uint64, data_len: uint64)
    Offset 32: hash         ([16]byte)
- Template directory prefix:
    `google3/third_party/jetski/prompt/template_provider/templates/`
"""

import argparse
import glob
import os
import struct
import sys


def parse_pe_sections(data: bytes):
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError("Invalid PE file (no MZ magic)")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if e_lfanew + 24 > len(data) or data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise ValueError("Invalid PE header")
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_hdr_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    opt_hdr_offset = e_lfanew + 24
    image_base = struct.unpack_from("<Q", data, opt_hdr_offset + 24)[0]
    sec_tbl = opt_hdr_offset + opt_hdr_size

    sections = []
    for i in range(num_sections):
        sec = data[sec_tbl + i * 40: sec_tbl + (i + 1) * 40]
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", sec, 8)
        sections.append({
            "va": image_base + vaddr,
            "vsize": vsize,
            "raw_ptr": raw_ptr,
            "raw_size": raw_size,
        })

    def va_to_raw(va: int):
        for s in sections:
            if s["va"] <= va < s["va"] + s["vsize"]:
                return s["raw_ptr"] + (va - s["va"])
        return None

    def raw_to_va(raw: int):
        for s in sections:
            if s["raw_ptr"] <= raw < s["raw_ptr"] + s["raw_size"]:
                return s["va"] + (raw - s["raw_ptr"])
        return None

    return va_to_raw, raw_to_va


def find_default_agy_binary():
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\X\AppData\Local")
    bin_dir = os.path.join(local_app_data, "agy", "bin")

    # Prefer latest pristine backup if available to ensure zero in-memory modification
    pristine_backups = sorted(
        glob.glob(os.path.join(bin_dir, "agy.exe.bak*pristine")),
        key=os.path.getmtime,
        reverse=True
    )
    if pristine_backups and os.path.exists(pristine_backups[0]):
        return pristine_backups[0]

    canonical = os.path.join(bin_dir, "agy.exe")
    if os.path.exists(canonical):
        return canonical
    return None


def extract_templates(exe_path: str, output_dir: str):
    print(f"[*] Reading binary: {exe_path}")
    with open(exe_path, "rb") as f:
        data = f.read()

    va_to_raw, raw_to_va = parse_pe_sections(data)

    target_needle = b"google3/third_party/jetski/prompt/template_provider/templates/system_prompts/identity.tmpl"
    raw_needle = data.find(target_needle)
    if raw_needle == -1:
        raise RuntimeError("Could not find identity.tmpl path string in binary.")

    va_needle = raw_to_va(raw_needle)
    if va_needle is None:
        raise RuntimeError("Could not compute VA for identity.tmpl path string.")

    pat_hdr = struct.pack("<QQ", va_needle, len(target_needle))
    hdr_pos = data.find(pat_hdr)
    if hdr_pos == -1:
        raise RuntimeError("Could not find embed.file struct referencing identity.tmpl.")

    ENTRY_SIZE = 48  # 16 (name string) + 16 (data string) + 16 (hash)

    # Scan backwards to locate the beginning of the embed.FS table
    start_pos = hdr_pos
    while True:
        prev = start_pos - ENTRY_SIZE
        if prev < 0:
            break
        n_va, n_len = struct.unpack_from("<QQ", data, prev)
        n_raw = va_to_raw(n_va)
        if n_raw and 0 < n_len < 200:
            name = data[n_raw:n_raw + n_len].decode("latin-1", errors="ignore")
            if "templates/" in name:
                start_pos = prev
                continue
        break

    os.makedirs(output_dir, exist_ok=True)
    templates = []

    cur = start_pos
    prefix = "google3/third_party/jetski/prompt/template_provider/templates/"

    while cur + ENTRY_SIZE <= len(data):
        n_va, n_len = struct.unpack_from("<QQ", data, cur)
        d_va, d_len = struct.unpack_from("<QQ", data, cur + 16)
        n_raw = va_to_raw(n_va)
        d_raw = va_to_raw(d_va)

        if not n_raw or not (0 < n_len < 200):
            break

        name = data[n_raw:n_raw + n_len].decode("latin-1", errors="ignore")
        if "templates/" not in name:
            break

        content = ""
        if d_raw and 0 <= d_len < 10_000_000 and d_raw + d_len <= len(data):
            content = data[d_raw:d_raw + d_len].decode("utf-8", errors="ignore")

        is_file = name.endswith(".tmpl")
        clean_rel = name.replace(prefix, "")
        clean_filename = clean_rel.replace("/", "__")

        if is_file:
            out_path = os.path.join(output_dir, clean_filename)
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(content)
            templates.append({
                "original_path": name,
                "relative_name": clean_rel,
                "clean_filename": clean_filename,
                "size_bytes": d_len,
                "file_path": out_path,
            })
            print(f"  [+] Extracted: {clean_rel:60s} ({d_len:6d} bytes)")

        cur += ENTRY_SIZE

    print(f"\n[+] Successfully extracted {len(templates)} templates to: {output_dir}")
    return templates


def main():
    parser = argparse.ArgumentParser(description="Extract embedded system prompt templates from official agy.exe")
    parser.add_argument("--bin", help="Path to agy.exe or pristine backup (auto-detected if omitted)")
    parser.add_argument("--out", default="templates/official_cli", help="Output directory for extracted templates")
    args = parser.parse_args()

    target_bin = args.bin or find_default_agy_binary()
    if not target_bin or not os.path.exists(target_bin):
        print("[-] Error: agy.exe binary not found. Specify with --bin <path>", file=sys.stderr)
        sys.exit(1)

    extract_templates(target_bin, args.out)


if __name__ == "__main__":
    main()
