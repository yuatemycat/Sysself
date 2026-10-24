"""Resolve git merge-file conflict markers in Proxymateur-Clean per-hunk.

choices[file] = list of 'clean' | 'main' | 'both' | 'both_main_first' | str (custom text)
"""
import re
import shutil
import sys

CLEAN = r'E:\02_Projects\Proxymateur-Clean'
MAIN = r'E:\02_Projects\Proxymateur'

AGY_H1 = (
    "$launcherFlags = @('--gateway-print-models', '--gateway-dry-run', '-px', '--px', '-native', '--native')\n"
    "$printModels = $args -contains '--gateway-print-models'\n"
    "$dryRun      = $args -contains '--gateway-dry-run'\n"
    "$proxyMode   = ($args -contains '-px') -or ($args -contains '--px')\n"
    "$nativeMode  = ($args -contains '-native') -or ($args -contains '--native')\n"
)
AGY_H3 = (
    "        $isArgonOnly = ($proxyCfg -and ($proxyCfg.gateway_routing_mode -eq 'argon_only')) -or ($modeOverride -eq 'argon_only')\n"
    "        $openaiModelIds = if (-not $isArgonOnly -and $proxyCfg.openai -and $proxyCfg.openai.enabled -and $proxyCfg.openai.routes) {\n"
    "            @($proxyCfg.openai.routes | ForEach-Object {\n"
    "                $mid = \"$($_.model_id)\".Trim()\n"
    "                if ($mid) { $mid; \"$mid-low\"; \"$mid-medium\"; \"$mid-high\" }\n"
    "            })\n"
)
AGY_H4 = (
    "        $code = $LASTEXITCODE\n"
    "        exit $code\n"
    "    } else {\n"
    "        Write-Host \"[agy] Warning: Proxymateur is not running or unreachable at $url. Falling back to native mode.\" -ForegroundColor Yellow\n"
)
OAI_H4 = (
    "        // 4. Auto-detect models with explicit openai/ prefix\n"
    "        let auto_detect = if requested.starts_with(\"openai/\") {\n"
    "            Some(requested.to_string())\n"
)
OAI_H6 = "    // Resolve API key: per-route -> global -> environment variable\n"
OAI_H7 = (
    "    // Resolve Base URL: per-route -> global\n"
    "    let base_url = route_base_url\n"
)

CHOICES = {
    'scripts/agy_gateway.ps1': [AGY_H1, 'main', AGY_H3, AGY_H4],
    'src-tauri/src/proxy/openai_upstream.rs': ['clean', 'clean', 'main', OAI_H4, 'main', OAI_H6, OAI_H7],
    'src-tauri/src/proxy/server.rs': ['main'],
    'src/components/settings/OpenAiUpstreamSettings.tsx': ['clean', 'clean'],
    'src/pages/Readme.tsx': ['main', 'both_main_first'],
}

pat = re.compile(r'<<<<<<< clean\n(.*?)=======\n(.*?)>>>>>>> main\n', re.S)

for rel, ch in CHOICES.items():
    path = CLEAN + '\\' + rel.replace('/', '\\')
    with open(path, 'r', encoding='utf-8', newline='') as fh:
        text = fh.read()
    nl = '\r\n' if '\r\n' in text else '\n'
    text = text.replace('\r\n', '\n')
    hunks = list(pat.finditer(text))
    if len(hunks) != len(ch):
        print(f'MISMATCH {rel}: {len(hunks)} hunks vs {len(ch)} choices')
        sys.exit(1)
    idx = iter(ch)

    def sub(m):
        c = next(idx)
        a, b = m.group(1), m.group(2)
        if c == 'clean':
            return a
        if c == 'main':
            return b
        if c == 'both_main_first':
            return b + a
        if c == 'both':
            return a + b
        return c

    out = pat.sub(sub, text)
    if nl == '\r\n':
        out = out.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(out)
    print('resolved', rel)

# Lab settings: take main's version wholesale (it is a superset of Clean's lab features).
shutil.copyfile(MAIN + r'\src\components\settings\AntigravityLabSettings.tsx',
                CLEAN + r'\src\components\settings\AntigravityLabSettings.tsx')
print('copied AntigravityLabSettings.tsx')
