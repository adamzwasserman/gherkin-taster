"""
Authentication Middleware
Validates Linear API tokens on each request
"""

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate Linear API token on each request"""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        public_paths = ["/health", "/", "/auth/login", "/auth/linear", "/auth/callback", "/auth/logout"]
        if request.url.path in public_paths or request.url.path.startswith("/static"):
            return await call_next(request)

        # Check for Linear token in cookies
        linear_token = request.cookies.get("linear_token")
        if not linear_token:
            # Redirect to login if no token
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/auth/login", status_code=303)

        # TODO: Validate token with Linear API
        # For now, trust the cookie
        response = await call_next(request)
        return response


def setup_auth_middleware(app: FastAPI) -> None:
    """Setup authentication middleware"""
    app.add_middleware(AuthMiddleware)
