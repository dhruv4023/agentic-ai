import json
from google import genai
from config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# for i in client.models.list():
#     print(i.name)

async def generate_ai_output(title, note, code):

    prompt = f"""
Return ONLY valid JSON:

{{
  "summary": "...",
  "explanation": "...",
  "improvements": "...",
  "tags": ["tag1"]
}}

Title: {title}
Note: {note}
Code: {code}
"""
    
    response = client.models.generate_content(
        # model="gemini-2.0-flash",
        model="gemma-3-1b-it",
        contents=prompt
    )

    try:        
        return extract_json(response.text)
    except:
        return {
            "summary": "Failed to generate.",
            "explanation": "",
            "improvements": "",
            "tags": []
        }

def extract_json(text: str):
    if "```" in text:
        text = text.split("```")[1]  # get inside block
        text = text.replace("json", "", 1).strip()
    return json.loads(text)
