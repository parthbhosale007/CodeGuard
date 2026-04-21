# 🛡️ CodeGuard – AI-Powered CI/CD Code Review System

CodeGuard is an AI-driven code analysis platform that integrates with CI/CD pipelines to automatically review code changes, detect security risks, and enforce quality standards before deployment.

---

## 🚀 Live Demo
- 🌐 Frontend: https://code-guard-flame.vercel.app
- ⚙️ Backend API: https://codeguard-qid9.onrender.com

---

## 🧠 Features

### 🔍 AI Code Analysis
- Detects:
  - Security vulnerabilities (e.g., SQL Injection, hardcoded secrets)
  - Code smells
  - Poor practices
- Provides actionable suggestions

### 🔄 CI/CD Integration
- GitHub Actions pipeline
- Automatically analyzes code on:
  - Push
  - Pull Request
- Blocks merge if severity is **critical**

### 📂 Repository-Level Analysis
- Accepts GitHub repo URLs
- Recursively fetches project files using GitHub API
- Filters relevant source files
- Performs AI-based analysis

### 🌐 Interactive UI
- Code Analyzer (paste code)
- Repo Analyzer (analyze full GitHub repo)
- Clean SaaS-style dark UI

---

## 🏗️ Architecture
User → Frontend (Vercel)
→ FastAPI Backend (Render)
→ GitHub API (repo fetch)
→ AI Model (Groq/OpenAI)
→ Response → UI + CI decision


---

## ⚙️ Tech Stack

### Backend
- FastAPI
- Python
- Requests (GitHub API)
- AI Model (LLM via Groq/OpenAI)

### Frontend
- HTML, CSS, JavaScript
- Deployed on Vercel

### CI/CD
- GitHub Actions
- Automated code review pipeline

---

## 🔁 CI/CD Workflow

1. Developer pushes code
2. GitHub Action triggers
3. Code is sent to CodeGuard API
4. AI analyzes code
5. Pipeline decision:
   - ❌ Critical → Block merge
   - ⚠️ High → Warning
   - ✅ Low → Pass

---

## 🔐 Security Focus

- Detects:
  - Hardcoded credentials
  - Weak passwords
  - SQL injection risks
- Encourages:
  - Environment variables
  - Secure coding practices
  - Strong hashing methods

---

⭐ Impact

CodeGuard transforms traditional CI/CD pipelines by integrating AI-driven decision making, enabling smarter and safer deployments.


👨‍💻 Author
Parth Bhosale
B.Tech AI & Data Science
