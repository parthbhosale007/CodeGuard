import os
from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code
from fastapi.middleware.cors import CORSMiddleware
from schemas import fetch_repo_code





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