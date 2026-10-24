#!/usr/bin/env python3
"""
Live Wire System Prompt Capture & Extractor
===========================================
Extracts the true, unabridged, server-side system prompts, behavioral instructions,
tool schemas, and bundled runtime skills for Claude Code and the Claude Agent SDK.

Supported Extraction Modes:
1. `--file <path>`: Parse an existing wire capture (e.g. `message.txt`, JSON request, or transcript).
2. `--auto`: Auto-discover local session captures across downloads, session caches, and proxy dumps.
3. `--listen [port]`: Launch a zero-dependency transparent loopback proxy (default: 8082).
   When Claude CLI runs with `ANTHROPIC_BASE_URL=http://127.0.0.1:8082`, it intercepts
   the outbound `/v1/messages` request, extracts the live multi-hundred-line system prompt,
   saves it to Sysself, and forwards seamlessly to Anthropic API.
4. `--assemble`: Combine wire captures with client-side binary modules into `full_system_prompt.md`.
"""

import argparse
import glob
import http.server
import json
import os
import re
import shutil
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSSELF_CLAUDE_DIR = os.path.join(BASE_DIR, "prompts", "claude_code")
ASSEMBLED_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "assembled")
MODULES_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "modules")
BUNDLED_SKILLS_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "bundled_skills")
RAW_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "raw")


def find_candidate_wire_files():
    """Scans local directories for wire captures and transcripts."""
    candidates = [
        r"E:\Downloads\message.txt",
        os.path.expanduser(r"~\Downloads\message.txt"),
    ]
    # Scan recent logs
    user_home = os.path.expanduser("~")
    log_patterns = [
        os.path.join(user_home, ".claude", "logs", "*.log"),
        os.path.join(user_home, ".claude", "sessions", "*", "*.json"),
        os.path.join(r"E:\02_Projects", "Proxymateur-Clean", "logs", "*.log"),
    ]
    for pat in log_patterns:
        candidates.extend(glob.glob(pat))

    valid = [p for p in candidates if os.path.isfile(p) and os.path.getsize(p) > 1024]
    return valid


def parse_wire_text(text: str):
    """
    Parses a wire capture text or JSON payload.
    Extracts:
      - instructions_block: The raw behavioral prompt (<claude_behavior>, <agentic_behavior>, etc.)
      - functions_block: Tool signatures and JSONSchemas
      - preamble: Function calling convention notes
      - on_demand_skills: List of (virtual_path, content)
    """
    instructions_block = ""
    functions_block = ""
    preamble = ""
    on_demand_skills = []

    # Check if raw JSON request (e.g. POST /v1/messages)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            # Extract system parameter
            sys_val = data.get("system")
            if isinstance(sys_val, list):
                instructions_block = "\n\n".join([item.get("text", "") for item in sys_val if isinstance(item, dict)])
            elif isinstance(sys_val, str):
                instructions_block = sys_val
            
            # Extract tools
            tools = data.get("tools", [])
            if tools:
                functions_block = json.dumps(tools, indent=2)
            
            return instructions_block, functions_block, preamble, on_demand_skills
    except Exception:
        pass

    # Marker-based transcript parsing (e.g. message.txt format)
    markers = list(re.finditer(r"^--- \[.*?\] ---$", text, re.MULTILINE))
    if markers:
        sys_start = markers[0].end()
        sys_end = markers[1].start() if len(markers) > 1 else len(text)
        raw_sys_block = text[sys_start:sys_end].strip()

        func_idx = raw_sys_block.find("<functions>")
        func_end_idx = raw_sys_block.find("</functions>")

        if func_idx != -1 and func_end_idx != -1:
            preamble = raw_sys_block[:func_idx].strip()
            functions_block = raw_sys_block[func_idx:func_end_idx + len("</functions>")].strip()
            instructions_block = raw_sys_block[func_end_idx + len("</functions>"):].strip()
        else:
            instructions_block = raw_sys_block
    else:
        # Fallback: scan for <claude_behavior> or main identity
        if "<claude_behavior>" in text:
            idx = text.find("<claude_behavior>")
            instructions_block = text[idx:].strip()
        else:
            instructions_block = text.strip()

    # Extract on-demand bundled skill files if present
    pattern = re.compile(r"^--- \[on-demand file:\s*(.*?)\] ---\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        raw_path = m.group(1).strip()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # Check if another general marker precedes
        marker_pat = re.compile(r"^--- \[.*?\] ---$", re.MULTILINE)
        next_marker = marker_pat.search(text, m.end())
        if next_marker and next_marker.start() < end_idx:
            end_idx = next_marker.start()
        
        content = text[m.end():end_idx].strip()
        on_demand_skills.append((raw_path, content))

    return instructions_block, functions_block, preamble, on_demand_skills


def save_extracted_wire_data(instructions: str, functions: str, preamble: str, skills: list):
    """Saves extracted wire prompt, tools, skills, and assembles the master prompt."""
    os.makedirs(ASSEMBLED_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(BUNDLED_SKILLS_DIR, exist_ok=True)

    # 1. Save Wire Prompt
    wire_path = os.path.join(ASSEMBLED_DIR, "claude_agent_sdk_wire_prompt.md")
    with open(wire_path, "w", encoding="utf-8") as f:
        f.write("# Claude Agent SDK & Anthropic Wire System Prompt (Captured from Live Session)\n\n")
        f.write(instructions)
    print(f"[OK] Wrote wire system prompt: {wire_path} ({len(instructions.splitlines())} lines)")

    # 2. Save Tools Schema
    if functions:
        ext = ".xml" if functions.startswith("<") else ".json"
        tools_path = os.path.join(RAW_DIR, f"claude_tools_schema{ext}")
        with open(tools_path, "w", encoding="utf-8") as f:
            f.write(functions)
        print(f"[OK] Wrote tool definitions: {tools_path} ({len(functions)} bytes)")

    # 3. Save Bundled Skills
    if skills:
        saved_skills = 0
        for raw_path, content in skills:
            clean_path = raw_path
            if "bundled-skills/" in clean_path:
                clean_path = clean_path.split("bundled-skills/")[-1]
                parts = clean_path.split("/")
                if len(parts) > 2:
                    clean_path = "/".join(parts[2:])
            elif "/mnt/skills/" in clean_path:
                clean_path = clean_path.split("/mnt/skills/")[-1]
            elif "~/.claude/skills/" in clean_path:
                clean_path = clean_path.split("~/.claude/skills/")[-1]
            if " (" in clean_path:
                clean_path = clean_path.split(" (")[0]
            clean_path = clean_path.replace("\\", "/").strip("/")

            # Normalize raw artifact reference names
            if "Artifact type file" in clean_path:
                if "design-system" in clean_path:
                    clean_path = "artifacts_reference/design_system_skill.md"
                elif "design" in clean_path:
                    clean_path = "artifacts_reference/design_skill.md"
                elif "slides" in clean_path:
                    clean_path = "artifacts_reference/slides_skill.md"
                elif "artifact-type" in clean_path:
                    clean_path = "artifacts_reference/artifact_type_assets"
                else:
                    clean_path = "artifacts_reference/artifact_spec.md"

            dest_path = os.path.join(BUNDLED_SKILLS_DIR, clean_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "w", encoding="utf-8") as sf:
                sf.write(content)
            saved_skills += 1
        print(f"[OK] Extracted {saved_skills} bundled skills into {BUNDLED_SKILLS_DIR}")

    # 4. Assemble Master Prompt
    assemble_master_prompt(instructions, preamble)


def assemble_master_prompt(wire_instructions: str, preamble: str = ""):
    """Assembles the master prompt combining wire instructions and decompiled CLI modules."""
    cli_modules = [
        "00_identities.md",
        "01_main_cli_intro.md",
        "02_doing_tasks.md",
        "03_executing_actions_with_care.md",
        "04_using_tools.md",
        "05_tone_and_style.md",
        "06_delivering_work.md",
        "07_corrections.md",
        "08_output_styles.md",
        "09_coordinator_mode.md",
        "10_subagent_worker.md",
        "11_surfaces_and_environments.md",
        "12_session_guidance_and_bg.md",
    ]

    cli_parts = []
    for m in cli_modules:
        p = os.path.join(MODULES_DIR, m)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as mf:
                cli_parts.append(mf.read().strip())

    cli_standalone = "\n\n---\n\n".join(cli_parts)

    cli_runtime_path = os.path.join(ASSEMBLED_DIR, "claude_code_cli_runtime_prompt.md")
    with open(cli_runtime_path, "w", encoding="utf-8") as f:
        f.write("# Claude Code CLI Standalone Runtime Prompt (Decompiled v2.1.304+)\n\n")
        f.write(cli_standalone)
    print(f"[OK] Wrote CLI runtime prompt: {cli_runtime_path} ({len(cli_standalone.splitlines())} lines)")

    master_path = os.path.join(ASSEMBLED_DIR, "full_system_prompt.md")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write("# Claude Code & Agent SDK Master Assembled System Prompt\n\n")
        f.write("> [!NOTE]\n")
        f.write("> Unabridged master assembled system prompt uniting official Anthropic Agent SDK wire\n")
        f.write("> behavioral guidelines (890+ lines) with decompiled client-side CLI execution modules (490+ lines).\n\n")
        if preamble:
            f.write("## Section 1: Function Calling Protocol & Tool Invocation\n\n")
            f.write(preamble + "\n\n")
            f.write("*(Full tool JSONSchema definitions preserved in `prompts/claude_code/raw/claude_tools_schema.xml`)*\n\n")
        f.write("## Section 2: Core Identity & Behavioral System Instructions\n\n")
        f.write(wire_instructions + "\n\n")
        f.write("## Section 3: Claude Code CLI Decompiled Runtime Modules\n\n")
        f.write(cli_standalone + "\n")

    lines = len(open(master_path, "r", encoding="utf-8").readlines())
    print(f"[OK] Wrote Master Assembled System Prompt: {master_path} ({lines} lines)")


class TransparentPromptSniffer(http.server.BaseHTTPRequestHandler):
    """
    Transparent loopback proxy for catching outbound Anthropic API requests in flight.
    Intercepts POST /v1/messages, writes out system prompt, and forwards to api.anthropic.com.
    """
    upstream_host = "https://api.anthropic.com"

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8", errors="ignore"))
            print(f"\n[*] Intercepted live request: {self.path} ({len(body)} bytes)")
            
            # Extract system prompt
            if "system" in payload:
                sys_content = payload["system"]
                if isinstance(sys_content, list):
                    text_dump = "\n\n".join([item.get("text", "") for item in sys_content if isinstance(item, dict)])
                else:
                    text_dump = str(sys_content)
                
                print(f"[+] Found live system prompt! ({len(text_dump.splitlines())} lines, {len(text_dump)} chars)")
                
                # Save immediately
                tools_block = json.dumps(payload.get("tools", []), indent=2) if "tools" in payload else ""
                save_extracted_wire_data(text_dump, tools_block, "", [])
        except Exception as e:
            print(f"[-] Error inspecting request payload: {e}")

        # Forward request to upstream
        target_url = f"{self.upstream_host}{self.path}"
        req = urllib.request.Request(target_url, data=body, method="POST")
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"):
                req.add_header(k, v)

        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for hk, hv in resp.headers.items():
                    if hk.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(hk, hv)
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as he:
            err_body = he.read()
            self.send_response(he.code)
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as ex:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {ex}".encode("utf-8"))


def run_proxy_listener(port: int = 8082):
    print(f"==================================================")
    print(f"  Sysself Live Transparent Prompt Interceptor     ")
    print(f"==================================================")
    print(f"[*] Listening on: http://127.0.0.1:{port}")
    print(f"[*] To intercept live prompts from Claude Code CLI, run:")
    print(f"    $env:ANTHROPIC_BASE_URL='http://127.0.0.1:{port}'")
    print(f"    claude")
    print(f"[*] Press Ctrl+C to terminate listener.")
    server = http.server.HTTPServer(("127.0.0.1", port), TransparentPromptSniffer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Proxy listener stopped.")


def main():
    parser = argparse.ArgumentParser(description="Extract actual unabridged wire system prompts & bundled skills.")
    parser.add_argument("--file", "-f", help="Path to wire capture, message dump, or JSON log file.")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto-discover wire dumps in Downloads/logs.")
    parser.add_argument("--listen", "-l", type=int, nargs="?", const=8082, help="Start live HTTP transparent interceptor.")
    parser.add_argument("--assemble", action="store_true", help="Re-assemble master full_system_prompt.md from existing files.")

    args = parser.parse_args()

    if args.listen:
        run_proxy_listener(args.listen)
        return

    target_file = args.file

    if args.auto or not target_file:
        candidates = find_candidate_wire_files()
        if candidates:
            target_file = candidates[0]
            print(f"[*] Auto-discovered wire capture: {target_file}")
        else:
            if not args.assemble:
                print("[-] No wire capture file found. Specify via --file <path> or use --listen.", file=sys.stderr)
                sys.exit(1)

    if target_file and os.path.isfile(target_file):
        print(f"[*] Reading wire capture from: {target_file} ({os.path.getsize(target_file)} bytes)...")
        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        inst, funcs, preamble, skills = parse_wire_text(text)
        print(f"[*] Parsed {len(inst.splitlines())} lines of behavioral instructions, {len(skills)} bundled skills.")
        save_extracted_wire_data(inst, funcs, preamble, skills)
    elif args.assemble:
        wire_path = os.path.join(ASSEMBLED_DIR, "claude_agent_sdk_wire_prompt.md")
        if os.path.isfile(wire_path):
            with open(wire_path, "r", encoding="utf-8") as wf:
                inst = wf.read().strip()
            assemble_master_prompt(inst)
        else:
            print("[-] Cannot assemble: claude_agent_sdk_wire_prompt.md does not exist.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
