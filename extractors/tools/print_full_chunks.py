import urllib.request
import json

url = "http://127.0.0.1:8045/v1beta/models/gemini-4-argon:streamGenerateContent?alt=sse"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-736ad8956af54d4da0fa686c3f80fb16"
}
payload = {
    "contents": [
        {"role": "user", "parts": [{"text": "Run a powershell command to list files in C:\\"}]}
    ],
    "tools": [
        {
            "functionDeclarations": [
                {
                    "name": "run_command",
                    "description": "Run a powershell command",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "CommandLine": {"type": "STRING", "description": "The command line"}
                        },
                        "required": ["CommandLine"]
                    }
                }
            ]
        }
    ]
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    while True:
        line = resp.readline()
        if not line:
            break
        line_str = line.decode("utf-8", errors="ignore").strip()
        if line_str.startswith("data:"):
            data_val = line_str[5:].strip()
            print("FULL CHUNK:\n", data_val)
