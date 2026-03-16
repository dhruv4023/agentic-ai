from fastapi import FastAPI
from config.settings import SETTING
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routes import events, rag
from fastapi import FastAPI
from inngest.fast_api import serve
from middleware.api_middleware import APIAuthMiddleware
from workflows.note_workflow import inngest_client, ai_enrichment
from fastapi.responses import JSONResponse
from fastapi import Request

origins = ["http://localhost:3000", "https://chatbothub.vercel.app"]

# origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app = FastAPI(debug=SETTING.DEBUG, title="Code Note AI Service")

serve(app=app, client=inngest_client, functions=[ai_enrichment])
app.add_middleware(SessionMiddleware, secret_key=SETTING.SESSION_SECRET)
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # You can replace '*' with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # or specific methods
    allow_headers=["Authorization", "Content-Type", "Accept"],  # or specific headers
)

app.include_router(events.router)
app.include_router(rag.router)
app.add_middleware(APIAuthMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "detail": str(exc),
        },
    )

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=SETTING.DEBUG)
