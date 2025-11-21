"""
Feature Routes
HTMX endpoints for feature list, view, and edit
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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
    feature = {
        "issue_id": issue_id,
        "title": "Demo Feature",
        "status": "In Progress",
    }
    return templates.TemplateResponse(
        "features/editor.html",
        {
            "request": request,
            "feature": feature,
            "feature_content": "# Placeholder Gherkin content",
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_feature_form(request: Request):
    """Show new requirement form"""
    # TODO: Fetch projects from Linear for dropdown
    return templates.TemplateResponse(
        "features/new.html",
        {
            "request": request,
            "projects": [],  # Placeholder
        },
    )


@router.post("/create")
async def create_feature(
    content: str = Form(...),
):
    """Create new requirement in Linear from Gherkin content"""
    # TODO: Implement workflow to:
    # 1. Parse Gherkin to extract feature name (use as issue title)
    # 2. Create issue in Linear with Gherkin content as description
    # 3. Store feature file path in custom field
    # 4. Return issue ID and redirect to editor

    # For now, just redirect back to list
    return RedirectResponse(url="/features", status_code=303)


@router.post("/{issue_id}/validate")
async def validate_feature(issue_id: str, content: str):
    """Validate Gherkin syntax (HTMX partial)"""
    # TODO: Implement Gherkin validation
    return {"valid": True, "errors": []}
