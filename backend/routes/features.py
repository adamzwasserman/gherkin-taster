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
async def list_features(request: Request, team: str = None):
    """List all features assigned to current user"""
    import httpx

    # Get user's Linear token
    linear_token = request.cookies.get("linear_token")
    if not linear_token:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Fetch teams first
    async with httpx.AsyncClient() as client:
        teams_response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query {
                        teams(first: 50) {
                            nodes {
                                id
                                name
                                key
                            }
                        }
                    }
                """
            },
        )
        teams_data = teams_response.json()

    teams = teams_data.get("data", {}).get("teams", {}).get("nodes", [])

    # Fetch issues assigned to current user from Linear
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query {
                        viewer {
                            assignedIssues(first: 50) {
                                nodes {
                                    id
                                    identifier
                                    title
                                    description
                                    state {
                                        name
                                    }
                                    priority
                                    createdAt
                                    updatedAt
                                    team {
                                        id
                                        name
                                        key
                                    }
                                }
                            }
                        }
                    }
                """
            },
        )
        data = response.json()

    issues = data.get("data", {}).get("viewer", {}).get("assignedIssues", {}).get("nodes", [])

    # Filter by team if specified
    if team:
        issues = [issue for issue in issues if issue.get("team", {}).get("id") == team]

    # Transform Linear issues to features format
    features = [
        {
            "issue_id": issue["identifier"],
            "title": issue["title"],
            "status": issue["state"]["name"],
            "priority": issue["priority"],
            "updated_at": issue["updatedAt"],
            "has_gherkin": "```yaml" in (issue.get("description") or "") or "## Gherkin Specification" in (issue.get("description") or ""),
        }
        for issue in issues
    ]

    return templates.TemplateResponse(
        "features/list.html",
        {
            "request": request,
            "features": features,
            "teams": teams,
            "selected_team": team,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_feature_form(request: Request):
    """Show new request form"""
    import httpx

    # Get user's Linear token
    linear_token = request.cookies.get("linear_token")
    if not linear_token:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Fetch teams, projects and team members from Linear
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query {
                        teams(first: 50) {
                            nodes {
                                id
                                name
                                key
                            }
                        }
                        projects(first: 50) {
                            nodes {
                                id
                                name
                            }
                        }
                        users(first: 50) {
                            nodes {
                                id
                                name
                                email
                            }
                        }
                    }
                """
            },
        )
        data = response.json()

    teams = data.get("data", {}).get("teams", {}).get("nodes", [])
    projects = data.get("data", {}).get("projects", {}).get("nodes", [])
    team_members = data.get("data", {}).get("users", {}).get("nodes", [])

    print(f"Loaded: {len(teams)} teams, {len(projects)} projects, {len(team_members)} users")

    return templates.TemplateResponse(
        "features/new.html",
        {
            "request": request,
            "teams": teams,
            "projects": projects,
            "team_members": team_members,
        },
    )


@router.get("/{issue_id}", response_class=HTMLResponse)
async def view_feature(request: Request, issue_id: str):
    """View and edit a specific feature"""
    import httpx
    import re

    # Get user's Linear token
    linear_token = request.cookies.get("linear_token")
    if not linear_token:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Fetch issue from Linear with full metadata
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query Issue($id: String!) {
                        issue(id: $id) {
                            id
                            identifier
                            title
                            description
                            state {
                                name
                            }
                            priority
                            team {
                                id
                                name
                                key
                            }
                            project {
                                id
                                name
                            }
                            assignee {
                                id
                                name
                                email
                            }
                            attachments {
                                nodes {
                                    id
                                    title
                                    url
                                    metadata
                                }
                            }
                        }
                    }
                """,
                "variables": {"id": issue_id},
            },
        )
        data = response.json()

    issue = data.get("data", {}).get("issue")

    if not issue:
        return RedirectResponse(url="/features", status_code=303)

    # Extract content from description
    description = issue.get("description") or ""
    gherkin_content = ""
    request_type = ""
    priority_text = ""
    ai_analysis = None

    # Extract Gherkin YAML
    if "```yaml" in description:
        start = description.find("```yaml") + 7
        end = description.find("```", start)
        if end > start:
            gherkin_content = description[start:end].strip()

    # Extract AI Analysis section
    if "## AI Analysis" in description:
        import yaml
        analysis_start = description.find("## AI Analysis") + len("## AI Analysis")
        analysis_end = description.find("## Gherkin Specification", analysis_start)
        if analysis_end == -1:
            analysis_end = len(description)

        analysis_text = description[analysis_start:analysis_end].strip()

        # Try to parse YAML from analysis
        if "```yaml" in analysis_text:
            yaml_start = analysis_text.find("```yaml") + 7
            yaml_end = analysis_text.find("```", yaml_start)
            if yaml_end > yaml_start:
                try:
                    analysis_yaml = yaml.safe_load(analysis_text[yaml_start:yaml_end])
                    if "analysis" in analysis_yaml:
                        ai_analysis = analysis_yaml["analysis"]
                except:
                    pass

    # Extract request metadata
    if "Request Type**:" in description:
        match = re.search(r"Request Type\*\*:\s*(\w+)", description)
        if match:
            request_type = match.group(1)

    if "Priority**:" in description:
        match = re.search(r"Priority\*\*:\s*(\d+)", description)
        if match:
            priority_map = {
                "0": "Urgent",
                "1": "High",
                "2": "Medium",
                "3": "Low",
                "4": "None"
            }
            priority_text = priority_map.get(match.group(1), "Unknown")

    # Extract plain description (before metadata section)
    plain_description = description
    if "## Request Metadata" in description:
        plain_description = description.split("## Request Metadata")[0].strip()

    # Get attachments from issue
    attachments = issue.get("attachments", {}).get("nodes", [])
    screen_video_url = None
    audio_url = None

    for attachment in attachments:
        title = attachment.get("title", "").lower()
        if "screen" in title and "recording" in title:
            screen_video_url = attachment.get("url")
        elif "audio" in title and "recording" in title:
            audio_url = attachment.get("url")

    feature = {
        "issue_id": issue["identifier"],
        "linear_id": issue["id"],
        "title": issue["title"],
        "status": issue["state"]["name"],
        "description": plain_description,
        "request_type": request_type,
        "priority_text": priority_text,
        "priority": issue.get("priority", 0),
        "team": issue.get("team"),
        "project": issue.get("project"),
        "assignee": issue.get("assignee"),
        "has_video": bool(screen_video_url),
        "has_audio": bool(audio_url),
        "screen_video_url": screen_video_url,
        "audio_url": audio_url,
        "attachments": attachments,
        "ai_analysis": ai_analysis,
    }

    return templates.TemplateResponse(
        "features/editor.html",
        {
            "request": request,
            "feature": feature,
            "feature_content": gherkin_content or "# No Gherkin content yet",
        },
    )


@router.post("/create")
async def create_feature(
    request: Request,
    request_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    team_id: str = Form(...),
    project_id: str = Form(""),
    assignee_id: str = Form(""),
    priority: int = Form(3),
    video: Optional[UploadFile] = File(None),
    audio: str = Form(""),
    screen_video: str = Form(""),
):
    """Create new request in Linear and trigger AI analysis"""
    import httpx
    from backend.config import get_settings
    from backend.services.gemini_service import GeminiService

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

    # Analyze video with Gemini if provided
    gherkin_content = None
    analysis_summary = None

    print(f"Screen video provided: {bool(screen_video)}")
    print(f"Gemini API key configured: {bool(settings.gemini_api_key)}")

    if screen_video and settings.gemini_api_key:
        print(f"Starting Gemini analysis for video of length: {len(screen_video)}")
        try:
            gemini_service = GeminiService()
            result = await gemini_service.analyze_video_and_generate_gherkin(
                video_base64=screen_video,
                title=title,
                description=description,
                request_type=request_type,
            )
            gherkin_content = result["gherkin_yaml"]
            analysis_summary = result["raw_response"]
            print(f"Gemini analysis completed successfully")
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            import traceback
            traceback.print_exc()
            # Continue without AI analysis
    else:
        if not screen_video:
            print("No screen video provided")
        if not settings.gemini_api_key:
            print("No Gemini API key configured")

    # Use the team ID provided by the user
    print(f"Using selected team ID: {team_id}")

    # Get current user ID if no assignee specified
    if not assignee_id:
        async with httpx.AsyncClient() as client:
            user_response = await client.post(
                "https://api.linear.app/graphql",
                headers={"Authorization": f"Bearer {linear_token}"},
                json={
                    "query": "{ viewer { id name } }"
                },
            )
            user_data = user_response.json()

        current_user = user_data.get("data", {}).get("viewer", {})
        assignee_id = current_user.get("id")
        print(f"No assignee specified, assigning to creator: {current_user.get('name')} ({assignee_id})")

    # Create Linear issue with Gherkin in description
    # NOTE: Do NOT store base64 video in description - too large for Linear API
    issue_description = f"{description}\n\n"

    # Store metadata for regeneration
    issue_description += f"## Request Metadata\n\n"
    issue_description += f"- **Request Type**: {request_type}\n"
    issue_description += f"- **Priority**: {priority}\n"

    # Note about recordings (we'll add attachment upload later)
    if screen_video or audio:
        issue_description += f"\n**Note**: Screen/audio recordings captured but not yet attached (feature coming soon)\n\n"

    if analysis_summary:
        issue_description += f"\n## AI Analysis\n\n{analysis_summary}\n\n"

    if gherkin_content:
        issue_description += f"## Gherkin Specification\n\n```yaml\n{gherkin_content}\n```"

    async with httpx.AsyncClient() as client:
        mutation = """
            mutation IssueCreate($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    success
                    issue {
                        id
                        identifier
                        url
                    }
                }
            }
        """

        variables = {
            "input": {
                "title": title,
                "description": issue_description,
                "priority": priority,
                "teamId": team_id,
                "assigneeId": assignee_id,
                "labelIds": [],  # TODO: Map label names to IDs
            }
        }

        if project_id:
            variables["input"]["projectId"] = project_id

        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={"query": mutation, "variables": variables},
        )

        result = response.json()

    # Check if response is valid
    if result is None:
        print(f"ERROR: Linear API returned None - likely request too large")
        print(f"Video size: {len(screen_video) if screen_video else 0} bytes")
        return RedirectResponse(url="/features?error=request_too_large", status_code=303)

    print(f"Linear API response: {result}")

    # Check if issue was created successfully
    if result and result.get("data", {}).get("issueCreate", {}).get("success"):
        issue_identifier = result["data"]["issueCreate"]["issue"]["identifier"]
        issue_id = result["data"]["issueCreate"]["issue"]["id"]
        print(f"Successfully created issue: {issue_identifier}")

        # Upload video/audio as attachments if provided
        from backend.services.linear_file_service import LinearFileService
        linear_file_service = LinearFileService(linear_token)

        if screen_video:
            print(f"Uploading screen recording...")
            video_url = await linear_file_service.upload_file(
                file_data=screen_video,
                filename=f"{issue_identifier}_screen_recording.webm",
                content_type="video/webm",
            )
            if video_url:
                await linear_file_service.attach_to_issue(
                    issue_id=issue_id,
                    asset_url=video_url,
                    title="Screen Recording",
                )

        if audio:
            print(f"Uploading audio recording...")
            audio_url = await linear_file_service.upload_file(
                file_data=audio,
                filename=f"{issue_identifier}_audio_recording.webm",
                content_type="audio/webm",
            )
            if audio_url:
                await linear_file_service.attach_to_issue(
                    issue_id=issue_id,
                    asset_url=audio_url,
                    title="Audio Recording",
                )

        return RedirectResponse(url=f"/features/{issue_identifier}", status_code=303)
    else:
        print(f"Failed to create issue: {result}")
        # Check for errors
        if result and "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
        return RedirectResponse(url="/features?error=creation_failed", status_code=303)


@router.get("/{issue_id}/preview", response_class=HTMLResponse)
async def preview_gherkin(request: Request, issue_id: str):
    """Render Gherkin preview (HTMX partial)"""
    import httpx
    import yaml

    linear_token = request.cookies.get("linear_token")
    if not linear_token:
        return "<p class='text-red-600'>Not authenticated</p>"

    # Fetch issue to get Gherkin content
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query Issue($id: String!) {
                        issue(id: $id) {
                            description
                        }
                    }
                """,
                "variables": {"id": issue_id},
            },
        )
        data = response.json()

    issue = data.get("data", {}).get("issue")
    if not issue:
        return "<p class='text-red-600'>Issue not found</p>"

    description = issue.get("description") or ""

    # Extract Gherkin YAML
    gherkin_yaml = None
    if "```yaml" in description:
        start = description.find("```yaml") + 7
        end = description.find("```", start)
        if end > start:
            try:
                gherkin_yaml = yaml.safe_load(description[start:end].strip())
            except:
                return "<p class='text-red-600'>Invalid YAML in Gherkin</p>"

    if not gherkin_yaml or "feature" not in gherkin_yaml:
        return "<p class='text-gray-500 text-sm'>No Gherkin specification found</p>"

    # Render Gherkin as formatted HTML
    feature = gherkin_yaml["feature"]
    html = f"<div class='space-y-4'>"
    html += f"<div><span class='font-bold text-lg text-indigo-700'>Feature:</span> <span class='text-gray-900'>{feature.get('title', 'Untitled')}</span></div>"

    if feature.get("description"):
        html += f"<p class='text-sm text-gray-700 ml-4'>{feature['description']}</p>"

    for scenario in feature.get("scenarios", []):
        html += f"<div class='mt-4 p-4 bg-gray-50 rounded-lg'>"
        html += f"<div class='font-semibold text-indigo-600'>Scenario: {scenario.get('scenario', 'Untitled')}</div>"

        for given in scenario.get("given", []):
            html += f"<div class='ml-4 mt-2 text-sm'><span class='font-medium text-green-700'>Given</span> {given}</div>"

        for when in scenario.get("when", []):
            html += f"<div class='ml-4 mt-1 text-sm'><span class='font-medium text-blue-700'>When</span> {when}</div>"

        for then in scenario.get("then", []):
            html += f"<div class='ml-4 mt-1 text-sm'><span class='font-medium text-purple-700'>Then</span> {then}</div>"

        html += "</div>"

    html += "</div>"
    return html


@router.post("/{issue_id}/regenerate")
async def regenerate_gherkin(request: Request, issue_id: str):
    """Regenerate Gherkin from saved video/audio"""
    import httpx
    import re
    from backend.config import get_settings
    from backend.services.gemini_service import GeminiService

    settings = get_settings()
    linear_token = request.cookies.get("linear_token")

    if not linear_token:
        return {"error": "Not authenticated"}

    # Fetch issue to get saved video/audio from attachments
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {linear_token}"},
            json={
                "query": """
                    query Issue($id: String!) {
                        issue(id: $id) {
                            id
                            identifier
                            title
                            description
                            attachments {
                                nodes {
                                    id
                                    title
                                    url
                                }
                            }
                        }
                    }
                """,
                "variables": {"id": issue_id},
            },
        )
        data = response.json()

    issue = data.get("data", {}).get("issue")
    if not issue:
        return {"error": "Issue not found"}

    description = issue.get("description") or ""

    # Get video URL from attachments
    attachments = issue.get("attachments", {}).get("nodes", [])
    screen_video_url = None

    for attachment in attachments:
        title = attachment.get("title", "").lower()
        if "screen" in title and "recording" in title:
            screen_video_url = attachment.get("url")
            break

    if not screen_video_url:
        return {"error": "No screen recording attachment found"}

    # Extract request type
    request_type = "feature"
    if "Request Type**:" in description:
        match = re.search(r"Request Type\*\*:\s*(\w+)", description)
        if match:
            request_type = match.group(1)

    # Extract plain description
    plain_description = description
    if "## Request Metadata" in description:
        plain_description = description.split("## Request Metadata")[0].strip()

    # Download video from Linear storage (requires authentication)
    async with httpx.AsyncClient() as client:
        video_response = await client.get(
            screen_video_url,
            headers={"Authorization": f"Bearer {linear_token}"},
            follow_redirects=True
        )
        if video_response.status_code != 200:
            print(f"Failed to download video: {video_response.status_code} - {video_response.text}")
            return {"error": f"Failed to download video from Linear storage: {video_response.status_code}"}

        # Convert to base64 for Gemini
        import base64
        video_base64 = base64.b64encode(video_response.content).decode('utf-8')
        print(f"Downloaded video: {len(video_response.content)} bytes")

    # Regenerate with Gemini
    if not settings.gemini_api_key:
        return {"error": "Gemini API key not configured"}

    try:
        gemini_service = GeminiService()
        result = await gemini_service.analyze_video_and_generate_gherkin(
            video_base64=video_base64,
            title=issue["title"],
            description=plain_description,
            request_type=request_type,
        )

        # Update issue description with new Gherkin
        new_description = plain_description + "\n\n"
        new_description += f"## Request Metadata\n\n"
        new_description += f"- **Request Type**: {request_type}\n"
        new_description += f"\n## AI Analysis\n\n{result['raw_response']}\n\n"
        new_description += f"## Gherkin Specification\n\n```yaml\n{result['gherkin_yaml']}\n```"

        # Update Linear issue
        async with httpx.AsyncClient() as client:
            update_response = await client.post(
                "https://api.linear.app/graphql",
                headers={"Authorization": f"Bearer {linear_token}"},
                json={
                    "query": """
                        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
                            issueUpdate(id: $id, input: $input) {
                                success
                                issue {
                                    id
                                }
                            }
                        }
                    """,
                    "variables": {
                        "id": issue["id"],
                        "input": {"description": new_description}
                    },
                },
            )

        return {"success": True, "message": "Gherkin regenerated successfully"}

    except Exception as e:
        print(f"Regeneration failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Regeneration failed: {str(e)}"}


@router.post("/{issue_id}/validate")
async def validate_feature(issue_id: str, content: str):
    """Validate Gherkin syntax (HTMX partial)"""
    # TODO: Implement Gherkin validation
    return {"valid": True, "errors": []}
