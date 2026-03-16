from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import SETTING, LOG

API_KEY = SETTING.AI_SERVICE_KEY
API_SECRET = SETTING.AI_SERVICE_SECRET

class APIAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/inngest"):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        api_key = request.headers.get("x-api-key")
        api_secret = request.headers.get("x-api-secret")

        if api_key != API_KEY or api_secret != API_SECRET:
            LOG.error(f"Unauthorized access attempt form {request.client.host}")
            raise HTTPException(status_code=401, detail="Unauthorized")

        return await call_next(request)
