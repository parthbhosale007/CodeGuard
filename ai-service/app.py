import os
from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code
from fastapi.middleware.cors import CORSMiddleware
import requests

import requests

def fetch_repo_code(repo_url):
    try:
        # ✅ Clean URL
        repo_url = repo_url.strip().replace("https://github.com/", "")
        parts = repo_url.split("/")

        if len(parts) < 2:
            return "Invalid GitHub URL"

        owner = parts[0]
        repo = parts[1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        response = requests.get(api_url)

        # ✅ Handle GitHub errors
        if response.status_code != 200:
            return f"GitHub API error: {response.status_code}"

        files = response.json()

        # ✅ Ensure it's a list
        if not isinstance(files, list):
            return "Unexpected GitHub response"

        code = ""

        for file in files:
            if file.get("type") == "file":
                if file["name"].endswith((".py", ".js", ".cpp")):
                    raw_res = requests.get(file["download_url"])

                    if raw_res.status_code == 200:
                        code += f"\n\nFile: {file['name']}\n{raw_res.text}"

        return code if code else "No valid code files found"

    except Exception as e:
        return f"Error fetching repo: {str(e)}"

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