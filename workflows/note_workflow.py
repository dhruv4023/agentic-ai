from inngest import Inngest, Concurrency, TriggerEvent
from services.github_service import fetch_github_content
from services.gemini_service import generate_ai_output
from services.spring_service import update_note

inngest_client = Inngest(app_id="code-note-ai")

@inngest_client.create_function(
    fn_id="ai-note-enrichment",
    trigger=TriggerEvent(event="note/created"),
    concurrency=[Concurrency(limit=1)],
    retries=3
)
async def ai_enrichment(ctx):

    data = ctx.event.data

    note_id = data["noteId"]
    title = data["title"]
    note = data["note"]
    permalink = data["permanentLink"]

    github_content = await fetch_github_content(permalink)
    ai_result = await generate_ai_output(title, note, github_content)
    # ai_result = {
    #     "summary": "AI Summary",
    #     "explanation": "AI Explanation",
    #     "improvements": "AI Improvements",
    #     "tags": ["python", "java"]
    # }

    await update_note(note_id, ai_result)

    return {"status": "completed"}
