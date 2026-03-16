from inngest import Inngest, Concurrency, TriggerEvent
from services.github_service import fetch_code
from services.gemini_service import generate_ai
from services.spring_service import save_notes
from services.ai_pipeline_service import embed_notes
from schemas.note_schema import NoteState
from langgraph.graph import StateGraph


graph = StateGraph(NoteState)

graph.add_node("fetch", fetch_code)
graph.add_node("ai", generate_ai)
graph.add_node("save", save_notes)
graph.add_node("embed", embed_notes)

graph.set_entry_point("fetch")

graph.add_edge("fetch", "ai")
graph.add_edge("ai", "save")
graph.add_edge( "save", "embed")

agent = graph.compile()

inngest_client = Inngest(app_id="code-note-ai")
@inngest_client.create_function(
    fn_id="ai-note-enrichment",
    trigger=TriggerEvent(event="note/created"),
    concurrency=[Concurrency(limit=1)],
    retries=3
)
async def ai_enrichment(ctx):

    data = ctx.event.data

    state = {
        "notes": data["items"]
    }

    await agent.ainvoke(state)

    return {"status": "processed"}
