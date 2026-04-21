import os
from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.get("/")
def home():
    return {"message": "CodeGuard API Running 🚀"}

@app.post("/review")
def review_code(req: CodeRequest):
    return analyze_code(req.code)