import urllib.request
import json

payload = {
    "message": "What is the fundamental law of retention according to Elena Verna?",
    "mode": "standard"
}
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/chat",
    data=data,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        print("HTTP STATUS:", resp.status)
        print("SESSION ID:", body.get("session_id"))
        print("PROVIDER USED:", body.get("provider_used"))
        print("CITATIONS COUNT:", len(body.get("citations", [])))
        print("FIRST CITATION:", body.get("citations", [])[0]["source_title"] if body.get("citations") else None)
        print("ARTIFACT GENERATED:", body.get("artifact", {}).get("title") if body.get("artifact") else None)
        print("WARNING:", body.get("warning"))
except Exception as e:
    print("FAILED:", e)
