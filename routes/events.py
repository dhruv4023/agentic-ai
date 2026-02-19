from fastapi import APIRouter
from schemas.note_schema import NoteCreatedEvent
from workflows.note_workflow import inngest_client

router = APIRouter()

@router.post("/events/note-created")
async def note_created(event: NoteCreatedEvent):
    await inngest_client.send({
        "name": "note/created",
        "data": event.dict()
    })
    return {"status": "queued"}
