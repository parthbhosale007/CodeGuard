import os
from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code
from fastapi.middleware.cors import CORSMiddleware
import requests

def fetch_repo_code(repo_url):
    # Extract owner & repo
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner = parts[0]
    repo = parts[1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    files = requests.get(api_url).json()

    code = ""

    for file in files:
        if file["type"] == "file":
            if file["name"].endswith((".py", ".js", ".cpp")):
                raw = requests.get(file["download_url"]).text
                code += f"\n\nFile: {file['name']}\n{raw}"

    return code

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
    code = fetch_repo_code(req.repo_url)
    return analyze_code(code)