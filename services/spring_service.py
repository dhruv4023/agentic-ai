import httpx
import time
import hashlib
import hmac
import base64

from config.settings import SETTING
from schemas.note_schema import NoteState


def generate_signature(path: str, timestamp: str):
    message = f"{path}|{timestamp}"

    digest = hmac.new(
        SETTING.AI_SERVICE_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode()


async def update_note(note_id: int, ai_data: dict):

    path = f"/ai/code-note/update/{note_id}"

    payload = {
        "id": note_id,
        "title": ai_data.get("title"),
        "description": ai_data.get("description"),
        "aiSummary": ai_data.get("summary"),
        "aiExplanation": ai_data.get("explanation"),
        "aiImprovements": ai_data.get("improvements"),
        "aiTags": ai_data.get("tags"),
    }
    for key in payload:
        if payload[key] is None:
            raise Exception("Invalid payload"+ str(payload))
        if key not in ["aiSummary", "aiExplanation", "aiImprovements", "aiTags", "id", "title", "description"]:
            raise Exception("Invalid payload key error"+ str(payload))


    timestamp = str(int(time.time() * 1000))
    # breakpoint()
    signature = generate_signature(path, timestamp)

    headers = {
        "Content-Type": "application/json",
        "X-AI-Service-Key": SETTING.AI_SERVICE_KEY,
        "X-Request-Time": timestamp,
        "X-AI-Signature": signature,
    }

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        res = await client.put(
            url=f"{SETTING.SPRING_API_BASE}{path}",
            json=payload
        )
        print(res.text)
        res.raise_for_status()


async def save_notes(state: NoteState):
    for note in state["notes"]:
        await update_note(note["id"], note["ai_result"])

    return state
