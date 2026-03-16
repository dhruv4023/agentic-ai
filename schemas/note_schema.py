from pydantic import BaseModel
from typing import TypedDict, List

class NoteCreatedEvent(BaseModel):
    noteId: int
    title: str
    description: str
    permanentLink: str

class NoteState(TypedDict):
    notes: List[dict]
