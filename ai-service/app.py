import os
from urllib.parse import urlparse

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from reviewer import analyze_code


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_github_url(url: str) -> tuple[str, str]:
    """Return (owner, repo) from a GitHub URL or 'owner/repo' shorthand."""
    url = url.strip().rstrip("/")
    if url.startswith("http"):
        path = urlparse(url).path.strip("/")
    else:
        path = url
    # Drop any sub-path like /tree/main or /blob/main/...
    parts = path.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid GitHub URL: {url!r}")
    return parts[0], parts[1]


def fetch_repo_code(repo_url: str, max_depth: int = 3, max_files: int = 60) -> str:
    """
    Recursively fetch source files from a public GitHub repository.

    Returns a single string with each file's path and first 2 000 chars,
    or an error/status string if something goes wrong.
    """
    SUPPORTED_EXTENSIONS = (
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".java", ".cpp", ".c", ".cs",
        ".html", ".css", ".json",
        ".go", ".rs", ".php",
    )
    SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}

    try:
        owner, repo = parse_github_url(repo_url)
    except ValueError as exc:
        return f"Invalid URL: {exc}"

    github_token = os.getenv("GITHUB_TOKEN", "")
    headers = {
        "User-Agent": "CodeGuard-App",
        "Accept": "application/vnd.github.v3+json",
        **({"Authorization": f"token {github_token}"} if github_token else {}),
    }

    collected: list[str] = []
    file_count = 0

    def fetch_dir(path: str = "", depth: int = 0) -> None:
        nonlocal file_count

        if depth > max_depth:
            return
        if file_count >= max_files:
            return

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        res = requests.get(api_url, headers=headers, timeout=10)

        if res.status_code == 403:
            rate_info = res.json().get("message", "")
            print(f"GitHub 403 at '{path}': {rate_info}")
            if "rate limit" in rate_info.lower():
                print("Tip: set the GITHUB_TOKEN env variable to raise your limit.")
            return

        if res.status_code == 404:
            print(f"GitHub 404 — repo or path not found: {path!r}")
            return

        if res.status_code != 200:
            print(f"GitHub API error {res.status_code} at path {path!r}")
            return

        items = res.json()
        if not isinstance(items, list):
            print(f"Unexpected GitHub response at '{path}':", items)
            return

        for item in items:
            if file_count >= max_files:
                break

            item_path: str = item.get("path", "")
            item_name: str = item.get("name", "")
            item_type: str = item.get("type", "")

            # Skip unwanted directories
            if any(skip in item_path.lower().split("/") for skip in SKIP_DIRS):
                continue

            if item_type == "file":
                if not item_name.endswith(SUPPORTED_EXTENSIONS):
                    continue

                download_url = item.get("download_url")
                if not download_url:
                    continue

                raw_res = requests.get(download_url, headers=headers, timeout=10)
                if raw_res.status_code != 200:
                    print(f"Could not download {item_path} ({raw_res.status_code})")
                    continue

                collected.append(f"\n\n# File: {item_path}\n{raw_res.text[:2000]}")
                file_count += 1

            elif item_type == "dir":
                fetch_dir(item_path, depth + 1)

    fetch_dir()

    if not collected:
        return "No valid code found"

    return "".join(collected)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


class RepoRequest(BaseModel):
    repo_url: str


@app.get("/")
def home():
    return {"message": "CodeGuard API Running 🚀"}


@app.post("/review")
def review_code(req: CodeRequest):
    return analyze_code(req.code)


@app.post("/review-repo")
def review_repo(req: RepoRequest):
    try:
        owner, repo = parse_github_url(req.repo_url)
    except ValueError as exc:
        return {"error": str(exc)}

    code = fetch_repo_code(req.repo_url)

    if code.startswith("Invalid URL") or code.startswith("No valid"):
        return {"error": code}

    if len(code.strip()) < 50:
        return {
            "severity": "low",
            "issues": ["No code fetched from repository"],
            "security": ["Unable to analyze repository contents"],
            "suggestions": ["Ensure the repository is public and contains supported file types"],
        }

    return analyze_code(code)