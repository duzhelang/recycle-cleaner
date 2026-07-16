import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path

TOKEN = os.environ.get("GH_TOKEN")
OWNER = "duzhelang"
REPO = "recycle-cleaner"
API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent


def curl(method, url, body=None):
    cmd = ["curl.exe", "-sS", "-X", method, url, "-H", f"Authorization: Bearer {TOKEN}", "-H", "Accept: application/vnd.github+json", "-H", "User-Agent: recycle-cleaner-sync"]
    if body is not None:
        payload = json.dumps(body)
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        tmp.write(payload)
        tmp.flush()
        tmp.close()
        cmd += ["-d", f"@{tmp.name}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def resolve_branch():
    repo = curl("GET", f"{API}/repos/{OWNER}/{REPO}")
    return repo.get("default_branch") or "main"


def git_files():
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    raw = out.split(b"\x00")
    result = []
    for item in raw:
        if not item:
            continue
        if item.startswith(b"\"") and item.endswith(b"\""):
            item = item[1:-1].decode("unicode_escape").encode("raw_unicode_escape")
            result.append(item.decode("utf-8"))
        else:
            result.append(item.decode("utf-8"))
    return result


def create_blob(path):
    content = base64.b64encode((ROOT / path).read_bytes()).decode("ascii")
    res = curl("POST", f"{API}/repos/{OWNER}/{REPO}/git/blobs", {"content": content, "encoding": "base64"})
    if "sha" not in res:
        raise RuntimeError("Blob create failed: " + str(res))
    return {"path": path, "mode": "100644", "type": "blob", "sha": res["sha"]}


def main():
    if not TOKEN:
        raise SystemExit("GH_TOKEN missing")

    branch = resolve_branch()
    files = git_files()
    if not files:
        raise SystemExit("No tracked files")

    tree_items = [create_blob(p) for p in files]
    tree = curl("POST", f"{API}/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_items})

    try:
        ref = curl("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}")
        parent_sha = ref["object"]["sha"]
    except Exception:
        parent_sha = None

    commit_body = {"message": "docs: sync readme and download docs", "tree": tree["sha"]}
    if parent_sha:
        commit_body["parents"] = [parent_sha]

    commit = curl("POST", f"{API}/repos/{OWNER}/{REPO}/git/commits", commit_body)
    if parent_sha:
        curl("PATCH", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}", {"sha": commit["sha"], "force": False})
    else:
        curl("POST", f"{API}/repos/{OWNER}/{REPO}/git/refs", {"ref": f"refs/heads/{branch}", "sha": commit["sha"]})

    print("SYNCED|https://github.com/" + OWNER + "/" + REPO)


if __name__ == "__main__":
    main()
