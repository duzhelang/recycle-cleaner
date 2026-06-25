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


def resolve_branch():
    try:
        repo = api("GET", f"{API}/repos/{OWNER}/{REPO}")
        return repo.get("default_branch") or "main"
    except Exception:
        return "main"


def current_sha(branch):
    try:
        refs = api("GET", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}")
        return refs["object"]["sha"], True
    except Exception:
        return None, False


def get_tree_sha(commit_sha):
    commit = api("GET", f"{API}/repos/{OWNER}/{REPO}/git/commits/{commit_sha}")
    return commit["tree"]["sha"]


def upload_file(remote_path: str, local_path: Path):
    if not local_path.exists():
        raise FileNotFoundError(local_path)

    branch = resolve_branch()
    sha, exists = current_sha(branch)
    if not exists:
        raise RuntimeError("Target branch missing")

    file_content = base64.b64encode(local_path.read_bytes()).decode("ascii")
    message = f"release: add {remote_path}"
    payload = {"message": message, "content": file_content, "branch": branch}

    if exists:
        try:
            existing = api("GET", f"{API}/repos/{OWNER}/{REPO}/contents/{remote_path}", )
            payload["sha"] = existing["sha"]
        except Exception:
            pass

    api("PUT", f"{API}/repos/{OWNER}/{REPO}/contents/{remote_path}", payload)


if __name__ == "__main__":
    remote = "release/RecycleCleaner_Setup.exe"
    local = ROOT / "installer" / "Output" / "RecycleCleaner_Setup.exe"
    upload_file(remote, local)
    print("UPLOADED|" + remote)
