"""
Feature Routes
HTMX endpoints for feature list, view, and edit
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_features(request: Request):
    """List all features assigned to current user"""
    # TODO: Implement workflow to fetch features from Linear
    return templates.TemplateResponse(
        "features/list.html",
        {
            "request": request,
            "features": [],  # Placeholder
        },
    )


@router.get("/{issue_id}", response_class=HTMLResponse)
async def view_feature(request: Request, issue_id: str):
    """View and edit a specific feature"""
    # TODO: Implement workflow to fetch feature from GitHub
    return templates.TemplateResponse(
        "features/editor.html",
        {
            "request": request,
            "issue_id": issue_id,
            "content": "# Placeholder Gherkin content",
        },
    )


@router.post("/{issue_id}/validate")
async def validate_feature(issue_id: str, content: str):
    """Validate Gherkin syntax (HTMX partial)"""
    # TODO: Implement Gherkin validation
    return {"valid": True, "errors": []}
