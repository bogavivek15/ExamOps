import urllib.request
import json

endpoints = [
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/docs",
    "/api/openapi.json",
    "/api/redoc",
]

print("=" * 60)
print("FASTAPI DOCUMENTATION & ENDPOINT VERIFICATION")
print("=" * 60)

for ep in endpoints:
    url = f"http://127.0.0.1:8000{ep}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        content_type = resp.headers.get("Content-Type", "")
        content_len = len(resp.read())
        print(f"  [PASS] {ep:<20} -> HTTP {resp.status} ({content_type.split(';')[0]}, {content_len} bytes)")
    except urllib.error.HTTPError as e:
        print(f"  [FAIL] {ep:<20} -> HTTP {e.code} ({e.reason})")
    except Exception as e:
        print(f"  [ERROR] {ep:<20} -> {e}")

# Inspect openapi.json routes
print("\n--- REGISTERED OPENAPI ROUTES AUDIT ---")
resp = urllib.request.urlopen("http://127.0.0.1:8000/openapi.json")
schema = json.loads(resp.read().decode("utf-8"))
paths = schema.get("paths", {})
print(f"Total API Paths Registered: {len(paths)}")
tag_counts = {}
for path, methods in sorted(paths.items()):
    for method, op in methods.items():
        tags = op.get("tags", ["Untagged"])
        for t in tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
        summary = op.get("summary") or op.get("description") or ""
        # print first 15 paths
        if list(paths.keys()).index(path) < 10:
            print(f"  {method.upper():<6} {path:<40} [{tags[0]}]")

if len(paths) > 10:
    print(f"  ... and {len(paths) - 10} more endpoints.")

print("\n--- ROUTE CATEGORIES (TAGS) ---")
for t, cnt in sorted(tag_counts.items()):
    print(f"  Tag: {t:<25} Endpoints: {cnt}")

