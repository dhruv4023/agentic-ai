from fastapi import APIRouter
from pydantic import BaseModel
from services.vector_search.rag_service import RagService

rag_service = RagService()

router = APIRouter()

class Question(BaseModel):
    query: str
    notebookId: int


@router.post("/ask")
async def note_created(req: Question):
    query = req.query
    notebookId = req.notebookId
    ans = await rag_service.ask(query, notebookId)
    return {"status": "success", "answer": ans}
