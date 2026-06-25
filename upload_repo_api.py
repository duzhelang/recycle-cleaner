import json
import os
import base64
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

TOKEN = os.environ.get("GH_TOKEN")
OWNER = "duzhelang"
REPO = "recycle-cleaner"
def resolve_default_branch():
    try:
        repo = api("GET", f"{API}/repos/{OWNER}/{REPO}")
        return repo.get("default_branch") or "main"
    except Exception:
        return "main"


BRANCH = resolve_default_branch()
ROOT = Path(__file__).resolve().parent
API = "https://api.github.com"


def api(method, url, body=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "recycle-cleaner-uploader",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="ignore")
        raise RuntimeError(f"GitHub API {e.code}: {err}") from e


def git_files():
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def create_blob(path: str):
    full = ROOT / path
    if not full.exists():
        raise FileNotFoundError(path)
    content = base64.b64encode(full.read_bytes()).decode("ascii")
    payload = {"content": content, "encoding": "base64"}
    res = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/blobs", payload)
    if "sha" not in res:
        raise RuntimeError("Blob create failed: " + str(res))
    return {"path": path, "mode": "100644", "type": "blob", "sha": res["sha"]}


def get_ref_sha():
    try:
        res = api("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
        return res["object"]["sha"]
    except Exception:
        return None


def ensure_default_branch():
    try:
        api("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
        return True
    except Exception:
        return False


def seed_initial_commit_if_empty():
    if ensure_default_branch():
        return
    api("PUT", f"{API}/repos/{OWNER}/{REPO}/contents/README.md", {
        "message": "chore: init repository",
        "content": base64.b64encode(b"# recycle-cleaner\n").decode("ascii"),
    })


def main():
    if not TOKEN:
        raise SystemExit("GH_TOKEN missing")

    files = git_files()
    if not files:
        raise SystemExit("No tracked files")

    seed_initial_commit_if_empty()

    tree_items = [create_blob(p) for p in files]
    tree = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_items})
    tree_sha = tree["sha"]

    parent_sha = get_ref_sha()
    commit_body = {
        "message": "feat: push repository contents via GitHub API",
        "tree": tree_sha,
    }
    if parent_sha:
        commit_body["parents"] = [parent_sha]

    commit = api("POST", f"{API}/repos/{OWNER}/{REPO}/git/commits", commit_body)
    commit_sha = commit["sha"]

    if parent_sha:
        api("PATCH", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", {"sha": commit_sha, "force": False})
    else:
        api("POST", f"{API}/repos/{OWNER}/{REPO}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": commit_sha})

    print("UPLOADED|https://github.com/" + OWNER + "/" + REPO)


if __name__ == "__main__":
    main()
