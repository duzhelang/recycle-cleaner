import base64
import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

TOKEN = os.environ.get("GH_TOKEN")
OWNER = "duzhelang"
REPO = "recycle-cleaner"
API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent


def api(method, url, body=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "recycle-cleaner-docs-sync",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="ignore")
        raise RuntimeError(f"GitHub API {e.code}: {err}") from e


def resolve_branch():
    repo = api("GET", f"{API}/repos/{OWNER}/{REPO}")
    return repo.get("default_branch") or "main"


def git_files():
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def create_blob(path):
    content = base64.b64encode((ROOT / path).read_bytes()).decode("ascii")
    res = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/blobs", {"content": content, "encoding": "base64"})
    return {"path": path, "mode": "100644", "type": "blob", "sha": res["sha"]}


def main():
    if not TOKEN:
        raise SystemExit("GH_TOKEN missing")

    branch = resolve_branch()
    files = git_files()
    if not files:
        raise SystemExit("No tracked files")

    tree_items = [create_blob(p) for p in files]
    tree = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_items})

    try:
        ref = api("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}")
        parent_sha = ref["object"]["sha"]
    except Exception:
        parent_sha = None

    commit_body = {"message": "docs: sync readme and download docs", "tree": tree["sha"]}
    if parent_sha:
        commit_body["parents"] = [parent_sha]

    commit = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/commits", commit_body)
    if parent_sha:
        api("PATCH", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}", {"sha": commit["sha"], "force": False})
    else:
        api("POST", f"{API}/repos/{OWNER}/{REPO}/git/refs", {"ref": f"refs/heads/{branch}", "sha": commit["sha"]})

    print("SYNCED|https://github.com/" + OWNER + "/" + REPO)


if __name__ == "__main__":
    main()
