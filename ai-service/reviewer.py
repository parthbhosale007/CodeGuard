import os
from groq import Groq
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_code(code: str):
    try: 
        prompt = f"""
You are an expert AI code reviewer specializing in security and code quality.

Analyze the following project code and return a STRICT JSON response.

IMPORTANT:
- Always return JSON
- Do NOT return plain text
- Even if no issues found, still return structured output

Format:
{{
  "severity": "low | medium | high | critical",
  "issues": ["..."],
  "security": ["..."],
  "suggestions": ["..."]
}}

Rules:
- If code is large, summarize key findings
- Focus on real risks (SQL injection, secrets, auth, etc.)
- If no major issues → severity = "low"
- NEVER return empty response
- NEVER say "no structured output"

CODE:
{code}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # ✅ updated
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content =  response.choices[0].message.content

        return json.loads(content)

    except Exception as e:
        return f"Error: {str(e)}"