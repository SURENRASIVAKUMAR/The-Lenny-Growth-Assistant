import urllib.request
import json

payload = {
    "message": "How should B2B SaaS companies structure pricing and avoid the per-seat trap?",
    "mode": "standard"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print("Status: 200 OK")
        print("Assistant Response:")
        print(result["message"]["content"][:300] + "...")
        print(f"Citations count: {len(result['message'].get('citations', []))}")
        if result.get("artifact"):
            print(f"Artifact title: {result['artifact']['title']}")
except Exception as e:
    print(f"Error: {e}")
