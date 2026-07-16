import urllib.request, json

BASE = "http://localhost:5173"
print("pipeline-status:", json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}/pipeline-status"), timeout=30).read()))
print("test-connection:", json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}/test-connection"), timeout=50).read()))

body = json.dumps({"question": "ping"}).encode()
r = urllib.request.Request(f"{BASE}/ask", data=body, headers={"Content-Type": "application/json"})
d = json.loads(urllib.request.urlopen(r, timeout=60).read())
print(f"ask: answer={d['answer'][:40]} model={d['model']} tokens={d['tokens']}")
