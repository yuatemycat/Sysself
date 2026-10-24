import re

with open('scratch/claude_prompts/cli_intro_251956604.txt', 'r', encoding='utf-8', errors='ignore') as f:
    bundle = f.read()

targets = ['ht', 'Rn', 'jd', 'ko', 'yu', 'Qe', 'ct', 'We', 'Pt', 'fo', 'Ir', 'dn', 'Jk', 'SA', 'mWe', 'Yt', 'B4n', 'ein', 'E8e', 'b1s', 'S1s', 'r1s', 'Rrr', 'w8e']

for var in targets:
    # search var = "..." or var = '...'
    m = re.findall(r'\b' + re.escape(var) + r'\s*=\s*["\']([^"\']+)["\']', bundle)
    if m:
        print(f'{var} = "{m[0]}"')
    else:
        # maybe search declarations like var var="..."; or let var="...";
        m2 = re.findall(r'(?:var|let|const)\s+' + re.escape(var) + r'\s*=\s*`([^`]+)`', bundle)
        if m2:
            print(f'{var} = `{m2[0][:60]}...`')
        else:
            print(f'{var} = NOT FOUND')
