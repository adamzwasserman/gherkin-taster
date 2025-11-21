"""
Authentication Middleware
Validates Linear API tokens on each request
"""

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate Linear API token on each request"""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check and static files
        if request.url.path in ["/health", "/"] or request.url.path.startswith("/static"):
            return await call_next(request)

        # TODO: Implement Linear token validation
        # For now, pass through
        response = await call_next(request)
        return response


def setup_auth_middleware(app: FastAPI) -> None:
    """Setup authentication middleware"""
    app.add_middleware(AuthMiddleware)
