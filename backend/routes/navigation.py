"""
Navigation Routes
Project/issue browser using Linear API data
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/projects", response_class=HTMLResponse)
async def list_projects(request: Request):
    """List Linear projects"""
    # TODO: Fetch from Linear API
    return templates.TemplateResponse(
        "navigation/projects.html",
        {
            "request": request,
            "projects": [],
        },
    )


@router.get("/projects/{project_id}/issues", response_class=HTMLResponse)
async def list_issues(request: Request, project_id: str):
    """List issues in a project"""
    # TODO: Fetch from Linear API
    return templates.TemplateResponse(
        "navigation/issues.html",
        {
            "request": request,
            "project_id": project_id,
            "issues": [],
        },
    )
