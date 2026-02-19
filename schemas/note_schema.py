from pydantic import BaseModel

class NoteCreatedEvent(BaseModel):
    noteId: int
    title: str
    note: str
    permanentLink: str
