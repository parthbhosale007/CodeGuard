import os
from groq import Groq
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_code(code: str):
    try: 
        prompt = f"""
You are a senior software engineer and security expert.

Analyze the following code and classify issues.

Return STRICT JSON:

{{
  "severity": "low | medium | high | critical",
  "issues": [],
  "security": [],
  "suggestions": []
}}

Rules:
- critical → security breach, secrets, major vulnerabilities
- high → serious bug or bad practice
- medium → moderate issue
- low → minor improvement

Code:
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