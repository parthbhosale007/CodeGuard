import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fallback error response — always returns a valid dict, never a plain string
def _error_response(reason: str) -> dict:
    return {
        "severity": "low",
        "issues": [f"Analysis could not be completed: {reason}"],
        "security": [],
        "suggestions": ["Please try again or check your API configuration."]
    }


def analyze_code(code: str) -> dict:
    try:
        prompt = f"""
You are an expert AI code reviewer specializing in security and code quality.

Analyze the following project code and return a STRICT JSON response.

IMPORTANT:
- Always return JSON and nothing else
- Do NOT wrap in markdown code fences
- Do NOT return plain text or explanations
- Even if no issues found, still return structured JSON

Format:
{{
  "severity": "low | medium | high | critical",
  "issues": ["..."],
  "security": ["..."],
  "suggestions": ["..."]
}}

Rules:
- If code is large, summarize key findings
- Focus on real risks (SQL injection, hardcoded secrets, auth bypass, etc.)
- If no major issues → severity = "low"
- NEVER return empty arrays for all three fields
- NEVER say "no structured output"
- Return ONLY the raw JSON object, no preamble

CODE:
{code}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",   # ✅ valid Groq-hosted model
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,           # lower = more deterministic JSON output
            max_tokens=1024,
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if the model wraps in ```json ... ```
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        content = content.strip()

        parsed = json.loads(content)

        # Validate expected keys exist — fill missing ones so frontend never breaks
        return {
            "severity": parsed.get("severity", "low"),
            "issues":      parsed.get("issues", []),
            "security":    parsed.get("security", []),
            "suggestions": parsed.get("suggestions", []),
        }

    except json.JSONDecodeError as e:
        print(f"[reviewer] JSON parse error: {e}\nRaw content: {content!r}")
        return _error_response("AI returned non-JSON output")

    except Exception as e:
        print(f"[reviewer] Unexpected error: {e}")
        return _error_response(str(e))