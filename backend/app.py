"""
Gherkin Taster FastAPI Application
Stateless web application for business approval of AI-generated Gherkin specifications
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import get_settings
from backend.middleware.auth_middleware import setup_auth_middleware
from backend.routes import features, approval, navigation, auth

# Initialize settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    print(f"🚀 Gherkin Taster starting in {settings.environment} mode")
    print(f"📍 Linear org: {settings.linear_org}")
    print(f"📍 GitHub org: {settings.github_org}")

    yield

    # Shutdown
    print("👋 Gherkin Taster shutting down")


# Create FastAPI app
app = FastAPI(
    title="Gherkin Taster",
    description="Business approval system for AI-generated Gherkin feature specifications",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup middleware
setup_auth_middleware(app)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(features.router, prefix="/features", tags=["features"])
app.include_router(approval.router, prefix="/approval", tags=["approval"])
app.include_router(navigation.router, prefix="", tags=["navigation"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root redirect to login or features"""
    from fastapi.responses import RedirectResponse
    # TODO: Check if user has session cookie, redirect to /features if yes
    return RedirectResponse(url="/auth/login")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == "development" else False,
    )
