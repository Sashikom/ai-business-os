from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import os
import logging

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/ai/") or request.method == "OPTIONS":
            return await call_next(request)
        return await call_next(request)
