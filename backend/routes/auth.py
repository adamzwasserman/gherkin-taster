"""
Authentication Routes
Linear OAuth flow
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from backend.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/linear")
async def linear_oauth_redirect():
    """Redirect to Linear OAuth"""
    settings = get_settings()

    # TODO: Get these from Linear OAuth app settings
    client_id = settings.linear_oauth_client_id
    redirect_uri = "http://localhost:8030/auth/callback"

    # Linear OAuth authorization URL
    auth_url = (
        f"https://linear.app/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=read,write"
    )

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def linear_oauth_callback(request: Request, code: str):
    """Handle Linear OAuth callback"""
    settings = get_settings()

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/oauth/token",
            json={
                "client_id": settings.linear_oauth_client_id,
                "client_secret": settings.linear_oauth_client_secret,
                "code": code,
                "redirect_uri": "http://localhost:8030/auth/callback",
                "grant_type": "authorization_code",
            },
        )
        token_data = response.json()

    access_token = token_data.get("access_token")

    if not access_token:
        return RedirectResponse(url="/auth/login?error=failed")

    # Get user info from Linear
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "query": "{ viewer { id name email } }",
            },
        )
        user_data = response.json()

    viewer = user_data.get("data", {}).get("viewer", {})

    # Store token in session (Redis)
    # TODO: Store in Redis with user ID as key
    # For now, store in cookie (not secure for production)
    response = RedirectResponse(url="/features", status_code=303)
    response.set_cookie(
        key="linear_token",
        value=access_token,
        httponly=True,
        max_age=2592000,  # 30 days
        secure=False,  # Set True in production with HTTPS
    )
    response.set_cookie(
        key="user_id", value=viewer.get("id", ""), httponly=True, max_age=2592000
    )
    response.set_cookie(
        key="user_name", value=viewer.get("name", ""), httponly=True, max_age=2592000
    )

    return response


@router.get("/logout")
async def logout():
    """Logout and clear session"""
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("linear_token")
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    return response
