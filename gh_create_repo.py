import json
import urllib.request
import urllib.error
import os

TOKEN = os.environ.get("GH_TOKEN")
REPO = "recycle-cleaner"

data = json.dumps({"name": REPO, "private": False}).encode()
req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "recycle-cleaner-bot",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())
        print("CREATED|" + body.get("html_url", ""))
except urllib.error.HTTPError as e:
    err = e.read().decode(errors="ignore")
    print("FAILED|" + str(e.code) + "|" + err)
