#!/usr/bin/env python3
"""
Sysself Universal Live Wire System Prompt Capture & Extractor
============================================================
Extracts the true, unabridged, server-side system prompts, behavioral instructions,
tool schemas, and bundled runtime skills for Claude Code (Anthropic API) and
Antigravity 2.0 (Google DeepMind / Vertex AI / Gemini internal API).

Supported Extraction Modes:
1. `--file <path>`: Parse an existing wire capture (e.g. `message.txt`, JSON request, or transcript).
2. `--auto`: Auto-discover local session captures across downloads, session caches, and proxy dumps.
3. `--listen [port]`: Launch a zero-dependency transparent loopback proxy (default: 8082).
   - Intercepts Anthropic `/v1/messages` (Claude Code)
   - Intercepts Google `/v1internal:*` & `*:generateContent` (Antigravity / Gemini)
   - Extracts live multi-hundred-line system prompts and forwards requests upstream seamlessly.
4. `--assemble`: Combine wire captures with client-side binary modules into full assembled prompts.
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

# Claude Paths
SYSSELF_CLAUDE_DIR = os.path.join(BASE_DIR, "prompts", "claude_code")
CLAUDE_ASSEMBLED_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "assembled")
CLAUDE_MODULES_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "modules")
CLAUDE_BUNDLED_SKILLS_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "bundled_skills")
CLAUDE_RAW_DIR = os.path.join(SYSSELF_CLAUDE_DIR, "raw")

# Antigravity Paths
SYSSELF_AGY_DIR = os.path.join(BASE_DIR, "prompts", "antigravity")
AGY_ASSEMBLED_DIR = os.path.join(SYSSELF_AGY_DIR, "assembled")
AGY_TEMPLATES_DIR = os.path.join(SYSSELF_AGY_DIR, "templates")


def find_candidate_wire_files():
    """Scans local directories for wire captures and transcripts."""
    candidates = [
        r"E:\Downloads\message.txt",
        os.path.expanduser(r"~\Downloads\message.txt"),
    ]
    user_home = os.path.expanduser("~")
    log_patterns = [
        os.path.join(user_home, ".claude", "logs", "*.log"),
        os.path.join(user_home, ".claude", "sessions", "*", "*.json"),
        os.path.join(user_home, ".gemini", "antigravity-cli", "brain", "*", ".system_generated", "logs", "transcript*.jsonl"),
        os.path.join(r"E:\02_Projects", "Proxymateur-Clean", "logs", "*.log"),
    ]
    for pat in log_patterns:
        candidates.extend(glob.glob(pat))

    valid = [p for p in candidates if os.path.isfile(p) and os.path.getsize(p) > 1024]
    return valid


def parse_wire_text(text: str):
    """
    Parses a wire capture text or JSON payload.
    Detects whether payload is Claude (Anthropic) or Antigravity (Gemini/Google).
    """
    # 1. Check if raw JSON request
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            # Check for Gemini / Vertex style systemInstruction
            sys_inst = data.get("systemInstruction") or data.get("system_instruction")
            if sys_inst:
                parts = sys_inst.get("parts", [])
                agy_text = "\n\n".join([p.get("text", "") for p in parts if isinstance(p, dict)])
                return "agy", agy_text, "", "", []

            # Check for Claude / Anthropic style system parameter
            sys_val = data.get("system")
            if sys_val:
                if isinstance(sys_val, list):
                    claude_text = "\n\n".join([item.get("text", "") for item in sys_val if isinstance(item, dict)])
                else:
                    claude_text = str(sys_val)
                tools_block = json.dumps(data.get("tools", []), indent=2) if "tools" in data else ""
                return "claude", claude_text, tools_block, "", []
    except Exception:
        pass

    # 2. Check for Marker-based transcript parsing (e.g. message.txt format)
    if "--- [system prompt] ---" in text or "<claude_behavior>" in text or "{antml:function_calls}" in text:
        instructions_block = ""
        functions_block = ""
        preamble = ""
        on_demand_skills = []

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
            if "<claude_behavior>" in text:
                idx = text.find("<claude_behavior>")
                instructions_block = text[idx:].strip()
            else:
                instructions_block = text.strip()

        # Extract on-demand bundled skills
        pattern = re.compile(r"^--- \[on-demand file:\s*(.*?)\] ---\s*$", re.MULTILINE)
        matches = list(pattern.finditer(text))
        for i, m in enumerate(matches):
            raw_path = m.group(1).strip()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            marker_pat = re.compile(r"^--- \[.*?\] ---$", re.MULTILINE)
            next_marker = marker_pat.search(text, m.end())
            if next_marker and next_marker.start() < end_idx:
                end_idx = next_marker.start()
            content = text[m.end():end_idx].strip()
            on_demand_skills.append((raw_path, content))

        return "claude", instructions_block, functions_block, preamble, on_demand_skills

    # 3. Check for Antigravity markers
    if "<identity>" in text and "Antigravity" in text:
        return "agy", text.strip(), "", "", []

    # Default fallback to claude
    return "claude", text.strip(), "", "", []


def save_extracted_claude_data(instructions: str, functions: str, preamble: str, skills: list):
    """Saves extracted Claude wire prompt, tools, skills, and assembles the master prompt."""
    os.makedirs(CLAUDE_ASSEMBLED_DIR, exist_ok=True)
    os.makedirs(CLAUDE_RAW_DIR, exist_ok=True)
    os.makedirs(CLAUDE_BUNDLED_SKILLS_DIR, exist_ok=True)

    wire_path = os.path.join(CLAUDE_ASSEMBLED_DIR, "claude_agent_sdk_wire_prompt.md")
    with open(wire_path, "w", encoding="utf-8") as f:
        f.write("# Claude Agent SDK & Anthropic Wire System Prompt (Captured from Live Session)\n\n")
        f.write(instructions)
    print(f"[OK] Wrote Claude wire system prompt: {wire_path} ({len(instructions.splitlines())} lines)")

    if functions:
        ext = ".xml" if functions.startswith("<") else ".json"
        tools_path = os.path.join(CLAUDE_RAW_DIR, f"claude_tools_schema{ext}")
        with open(tools_path, "w", encoding="utf-8") as f:
            f.write(functions)
        print(f"[OK] Wrote tool definitions: {tools_path} ({len(functions)} bytes)")

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

            dest_path = os.path.join(CLAUDE_BUNDLED_SKILLS_DIR, clean_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "w", encoding="utf-8") as sf:
                sf.write(content)
            saved_skills += 1
        print(f"[OK] Extracted {saved_skills} bundled skills into {CLAUDE_BUNDLED_SKILLS_DIR}")

    assemble_claude_master_prompt(instructions, preamble)


def assemble_claude_master_prompt(wire_instructions: str, preamble: str = ""):
    cli_modules = [
        "00_identities.md", "01_main_cli_intro.md", "02_doing_tasks.md",
        "03_executing_actions_with_care.md", "04_using_tools.md", "05_tone_and_style.md",
        "06_delivering_work.md", "07_corrections.md", "08_output_styles.md",
        "09_coordinator_mode.md", "10_subagent_worker.md", "11_surfaces_and_environments.md",
        "12_session_guidance_and_bg.md",
    ]

    cli_parts = []
    for m in cli_modules:
        p = os.path.join(CLAUDE_MODULES_DIR, m)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as mf:
                cli_parts.append(mf.read().strip())

    cli_standalone = "\n\n---\n\n".join(cli_parts)

    cli_runtime_path = os.path.join(CLAUDE_ASSEMBLED_DIR, "claude_code_cli_runtime_prompt.md")
    with open(cli_runtime_path, "w", encoding="utf-8") as f:
        f.write("# Claude Code CLI Standalone Runtime Prompt (Decompiled v2.1.304+)\n\n")
        f.write(cli_standalone)

    master_path = os.path.join(CLAUDE_ASSEMBLED_DIR, "full_system_prompt.md")
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
    print(f"[OK] Wrote Claude Master Assembled Prompt: {master_path} ({lines} lines)")


def save_extracted_agy_data(instructions: str):
    """Saves extracted Antigravity wire prompt and master assembled prompt."""
    os.makedirs(AGY_ASSEMBLED_DIR, exist_ok=True)

    wire_path = os.path.join(AGY_ASSEMBLED_DIR, "antigravity_wire_system_prompt.md")
    with open(wire_path, "w", encoding="utf-8") as f:
        f.write("# Antigravity 2.0 Wire System Prompt (Captured from Live Vertex/Gemini Request)\n\n")
        f.write("```markdown\n")
        f.write(instructions)
        f.write("\n```\n")
    print(f"[OK] Wrote Antigravity wire system prompt: {wire_path} ({len(instructions.splitlines())} lines)")

    master_path = os.path.join(AGY_ASSEMBLED_DIR, "full_system_prompt.md")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write("# Antigravity 2.0 Official Master System Prompt (Unabridged Production Wire Specification)\n\n")
        f.write("> [!NOTE]\n")
        f.write("> True, complete assembled system prompt utilized in production by Google DeepMind's\n")
        f.write("> Advanced Agentic Coding engine (Antigravity 2.0 / Jetski).\n\n")
        f.write("```markdown\n")
        f.write(instructions)
        f.write("\n```\n")

    lines = len(open(master_path, "r", encoding="utf-8").readlines())
    print(f"[OK] Wrote Antigravity Master Prompt: {master_path} ({lines} lines)")


class UniversalPromptSniffer(http.server.BaseHTTPRequestHandler):
    """
    Transparent loopback proxy for catching outbound Anthropic and Gemini API requests in flight.
    """
    anthropic_upstream = "https://api.anthropic.com"
    gemini_upstream = "https://generativelanguage.googleapis.com"

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Detect endpoint
        is_gemini = "generateContent" in self.path or "v1internal" in self.path or "models" in self.path
        upstream_base = self.gemini_upstream if is_gemini else self.anthropic_upstream

        try:
            payload = json.loads(body.decode("utf-8", errors="ignore"))
            print(f"\n[*] Intercepted live request: {self.path} ({len(body)} bytes, target={'Gemini' if is_gemini else 'Anthropic'})")

            if is_gemini:
                sys_inst = payload.get("systemInstruction") or payload.get("system_instruction")
                if sys_inst:
                    parts = sys_inst.get("parts", [])
                    agy_dump = "\n\n".join([p.get("text", "") for p in parts if isinstance(p, dict)])
                    print(f"[+] Found live Antigravity system prompt! ({len(agy_dump.splitlines())} lines)")
                    save_extracted_agy_data(agy_dump)
            else:
                if "system" in payload:
                    sys_content = payload["system"]
                    text_dump = "\n\n".join([item.get("text", "") for item in sys_content if isinstance(item, dict)]) if isinstance(sys_content, list) else str(sys_content)
                    print(f"[+] Found live Claude system prompt! ({len(text_dump.splitlines())} lines)")
                    tools_block = json.dumps(payload.get("tools", []), indent=2) if "tools" in payload else ""
                    save_extracted_claude_data(text_dump, tools_block, "", [])
        except Exception as e:
            print(f"[-] Error inspecting payload: {e}")

        # Forward upstream
        target_url = f"{upstream_base}{self.path}"
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
    print(f"  Sysself Universal Live Prompt Interceptor      ")
    print(f"==================================================")
    print(f"[*] Listening on: http://127.0.0.1:{port}")
    print(f"[*] Intercepts both Claude Code & Antigravity (Gemini) API traffic.")
    print(f"[*] Usage with Claude Code CLI:")
    print(f"    $env:ANTHROPIC_BASE_URL='http://127.0.0.1:{port}' ; claude")
    print(f"[*] Usage with Antigravity / Gemini CLI:")
    print(f"    $env:GEMINI_API_ENDPOINT='http://127.0.0.1:{port}' ; agy")
    print(f"[*] Press Ctrl+C to terminate listener.")
    server = http.server.HTTPServer(("127.0.0.1", port), UniversalPromptSniffer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Proxy listener stopped.")


def main():
    parser = argparse.ArgumentParser(description="Extract actual unabridged wire system prompts for Claude & Antigravity.")
    parser.add_argument("--file", "-f", help="Path to wire capture, message dump, or JSON log file.")
    parser.add_argument("--target", "-t", choices=["claude", "agy", "gemini", "auto"], default="auto", help="Target prompt system.")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto-discover wire dumps in Downloads/logs.")
    parser.add_argument("--listen", "-l", type=int, nargs="?", const=8082, help="Start live HTTP transparent interceptor.")
    parser.add_argument("--assemble", action="store_true", help="Re-assemble master prompt files.")

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

        ptype, inst, funcs, preamble, skills = parse_wire_text(text)
        print(f"[*] Detected payload type: {ptype.upper()} ({len(inst.splitlines())} lines)")

        if ptype in ("agy", "gemini"):
            save_extracted_agy_data(inst)
        else:
            save_extracted_claude_data(inst, funcs, preamble, skills)


if __name__ == "__main__":
    main()
