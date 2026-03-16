from services.vector_search.embedding_service import EmbeddingService

embedding_service = EmbeddingService()


async def embed_notes(state):

    for note in state["notes"]:

        ai = note["ai_result"]

        text = f"""
Title: {note['title']}

User Note:
{note['description']}

Summary:
{ai['summary']}

Explanation:
{ai['explanation']}

Improvements:
{ai['improvements']}

Tags:
{' '.join(ai['tags'])}
"""

        embedding_service.generate_and_store(
            text=text,
            metadata={
                "noteId": note["id"],
                "notebookId": note["notebookId"],
            }
        )

    return state