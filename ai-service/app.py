from fastapi import FastAPI
from pydantic import BaseModel
from reviewer import analyze_code

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.get("/")
def home():
    return {"message": "CodeGuard AI Service Running 🚀"}

@app.post("/review")
def review_code(req: CodeRequest):
    result = analyze_code(req.code)
    return result