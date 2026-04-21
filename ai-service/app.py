import os
from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code
from fastapi.middleware.cors import CORSMiddleware
import requests

import requests

def fetch_repo_code(repo_url):
    import requests

    try:
        repo_url = repo_url.strip().replace("https://github.com/", "")
        parts = repo_url.split("/")

        owner = parts[0]
        repo = parts[1]

        code = ""

        def fetch_dir(path=""):
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            res = requests.get(api_url)

            if res.status_code != 200:
                return

            items = res.json()

            for item in items:
                if item["type"] == "file":
                    if item["name"].endswith((".py", ".js", ".cpp", ".ts", ".html", ".css", ".json")):
                        raw = requests.get(item["download_url"]).text
                        nonlocal code
                        code += f"\n\nFile: {item['path']}\n{raw[:2000]}"
                
                elif item["type"] == "dir":
                    fetch_dir(item["path"])

        fetch_dir()

        return code if code else "No valid code found"

    except Exception as e:
        return f"Error: {str(e)}"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now (we’ll tighten later)
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
        code = fetch_repo_code(req.repo_url)

        # If error string → return directly
        if code.startswith("Error") or code.startswith("GitHub") or code.startswith("Invalid"):
            return {"error": code}

        return analyze_code(code)

    except Exception as e:
        return {"error": str(e)}