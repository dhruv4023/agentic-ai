import httpx
import time
import hashlib
import hmac
import base64

from config.settings import settings


def generate_signature(path: str, timestamp: str):
    message = f"{path}|{timestamp}"

    digest = hmac.new(
        settings.AI_SERVICE_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode()


async def update_note(note_id: int, ai_data: dict):

    path = f"/ai/code-note/update/{note_id}"

    payload = {
        "id": note_id,
        "aiSummary": ai_data.get("summary"),
        "aiExplanation": ai_data.get("explanation"),
        "aiImprovements": ai_data.get("improvements"),
        "aiTags": ai_data.get("tags"),
    }
    for key in payload:
        if payload[key] is None:
            raise Exception("Invalid payload")
        if key not in ["aiSummary", "aiExplanation", "aiImprovements", "aiTags", "id"]:
            raise Exception("Invalid payload key error")


    timestamp = str(int(time.time() * 1000))
    # breakpoint()
    signature = generate_signature(path, timestamp)

    headers = {
        "Content-Type": "application/json",
        "X-AI-Service-Key": settings.AI_SERVICE_KEY,
        "X-Request-Time": timestamp,
        "X-AI-Signature": signature,
    }

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        res = await client.put(
            url=f"{settings.SPRING_API_BASE}{path}",
            json=payload
        )
        print(res.text)
        res.raise_for_status()

