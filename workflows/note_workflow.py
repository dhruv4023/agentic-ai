from inngest import Inngest, Concurrency, TriggerEvent
from services.github_service import fetch_github_content
from services.gemini_service import generate_ai_output
from services.spring_service import update_note


from langgraph.graph import StateGraph
from typing import TypedDict, List

class NoteState(TypedDict):
    notes: List[dict]

async def fetch_code(state: NoteState):

    for note in state["notes"]:
        note["github_content"] = await fetch_github_content(
            note["permanentLink"]
        )

    return state


async def generate_ai(state: NoteState):
    for note in state["notes"]:
        note["ai_result"] = await generate_ai_output(note["title"], note["note"], note["github_content"])

        # note["ai_result"] = {
        #     "summary": "This is a summary",
        #     "explanation": "This is an explanation",
        #     "improvements": "This is improvements",
        #     "tags": ["tag1", "tag2"]
        # }

    return state

async def save_notes(state: NoteState):

    for note in state["notes"]:
        await update_note(note["id"], note["ai_result"])

    return state


graph = StateGraph(NoteState)

graph.add_node("fetch", fetch_code)
graph.add_node("ai", generate_ai)
graph.add_node("save", save_notes)

graph.set_entry_point("fetch")

graph.add_edge("fetch", "ai")
graph.add_edge("ai", "save")

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
