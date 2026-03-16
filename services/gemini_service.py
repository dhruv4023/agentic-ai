import json
from google import genai
from config.settings import SETTING
from services.vector_search.rag_service import RagService
from schemas.note_schema import NoteState


rag_service = RagService()
client = genai.Client(api_key=SETTING.GEMINI_API_KEY)

# for i in client.models.list():
#     print(i.name)

def fallback_response():
    return {
        "title": "Failed to generate.",
        "description": "Failed to generate.",
        "summary": "Failed to generate.",
        "explanation": "",
        "improvements": "",
        "tags": []
    }

async def generate_ai_output(title, note, code, notebookId):
    q = f"{title or ''} {note or ''}".strip()

    context = False

    if q:
        print("Querying vector search")
        context = await rag_service.get_context(q, notebookId)
    # return {
    #     "title": title,
    #     "description": note,
    #     "summary": "test",
    #     "explanation": "test",
    #     "improvements": "test",
    #     "tags": ["test"]
    # }
    prompt = f"""
Return ONLY valid JSON:

{{
  "title": "...",
  "description": "...",
  "summary": "...",
  "explanation": "...",
  "improvements": "...",
  "tags": ["tag1"]
}}

{"Use the following context:\n" + context if context and len(context.strip()) > 50 else "No external context available. Use your own knowledge."}

{"Title: " + title if title else ""}
{"Description: " + note if note else ""}
Code: {code}
"""
    response = client.models.generate_content(
        model="gemma-3-1b-it",
        contents=prompt
    )

    try:
        return extract_json(response.text)
    except:
        return fallback_response()
        

def extract_json(text: str):
    if "```" in text:
        text = text.split("```")[1]
        text = text.replace("json", "", 1).strip()
    return json.loads(text)


async def generate_ai(state: NoteState):
    for note in state["notes"]:
        note["ai_result"] = await generate_ai_output(note.get("title"), note.get("description"), note["github_content"], note["notebookId"])
    return state
