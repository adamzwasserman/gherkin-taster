"""
Feature Routes
HTMX endpoints for feature list, view, and edit
"""

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

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


@router.get("/new", response_class=HTMLResponse)
async def new_feature_form(request: Request):
    """Show new request form"""
    # TODO: Fetch projects and team members from Linear
    return templates.TemplateResponse(
        "features/new.html",
        {
            "request": request,
            "projects": [],  # Placeholder
            "team_members": [],  # Placeholder
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


@router.post("/create")
async def create_feature(
    request: Request,
    request_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    project_id: str = Form(""),
    assignee_id: str = Form(""),
    priority: int = Form(3),
    video: Optional[UploadFile] = File(None),
    audio: str = Form(""),
    screen_video: str = Form(""),
):
    """Create new request in Linear and trigger AI analysis"""
    from backend.config import get_settings

    settings = get_settings()

    # Get user's Linear token from session
    linear_token = request.cookies.get("linear_token")
    if not linear_token:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Map request type to Linear label
    label_map = {
        "bug": "bug",
        "enhancement": "enhancement",
        "feature": "feature"
    }
    labels = [label_map.get(request_type, "feature")]

    # TODO: Use Linear MCP to create issue
    # For now, build the data structure
    issue_data = {
        "title": title,
        "description": description,
        "team": settings.linear_team,
        "priority": priority,
        "labels": labels,
    }

    if project_id:
        issue_data["project"] = project_id

    if assignee_id:
        issue_data["assignee"] = assignee_id

    # TODO: Create issue via Linear API/MCP
    # TODO: If video provided: upload to storage and attach to issue
    # TODO: If audio provided: decode base64, upload to storage, attach to issue
    # TODO: Add comment to issue with multimedia attachments
    # TODO: Trigger AI analysis pipeline (transcribe video/audio, generate Gherkin)
    # TODO: Store generated Gherkin in GitHub
    # TODO: Update Linear issue with GitHub file path

    # For now, redirect to list
    # After Linear integration: redirect to /features/{issue_id}
    return RedirectResponse(url="/features", status_code=303)


@router.post("/{issue_id}/validate")
async def validate_feature(issue_id: str, content: str):
    """Validate Gherkin syntax (HTMX partial)"""
    # TODO: Implement Gherkin validation
    return {"valid": True, "errors": []}
