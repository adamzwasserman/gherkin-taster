"""
Linear Issue Tracker Adapter
Implements IssueTrackerProvider protocol for Linear API
"""

from typing import Optional
from linear import LinearClient
from backend.facades.issue_tracker import IssueTrackerProvider, Issue, User, Comment
from backend.config import get_settings


class LinearAdapter(IssueTrackerProvider):
    """Linear API adapter implementing IssueTrackerProvider protocol"""

    def __init__(self, api_token: Optional[str] = None):
        settings = get_settings()
        self.api_token = api_token or settings.linear_api_token
        self.client = LinearClient(self.api_token)

    async def get_issue(self, issue_id: str) -> Issue:
        """Fetch issue metadata from Linear"""
        issue = await self.client.issue(issue_id)

        # Extract custom field for feature file path
        custom_fields = {}
        for field in issue.custom_fields or []:
            custom_fields[field.name] = field.value

        return Issue(
            id=issue.identifier,
            title=issue.title,
            status=issue.state.name,
            assignee_id=issue.assignee.id if issue.assignee else None,
            project_id=issue.project.id if issue.project else "",
            custom_fields=custom_fields,
        )

    async def update_issue(
        self,
        issue_id: str,
        *,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> None:
        """Update issue fields in Linear"""
        issue = await self.client.issue(issue_id)

        update_params = {}

        if status is not None:
            # Find workflow state by name
            states = await self.client.workflow_states()
            matching_state = next((s for s in states if s.name == status), None)
            if matching_state:
                update_params["state_id"] = matching_state.id

        if assignee_id is not None:
            update_params["assignee_id"] = assignee_id

        if update_params:
            await issue.update(**update_params)

    async def add_comment(self, issue_id: str, content: str) -> Comment:
        """Add comment to Linear issue"""
        issue = await self.client.issue(issue_id)
        comment = await issue.create_comment(body=content)

        return Comment(
            id=comment.id,
            issue_id=issue_id,
            author_id=comment.user.id,
            content=comment.body,
            created_at=comment.created_at.isoformat(),
        )

    async def get_users(self, team_id: str) -> list[User]:
        """Get team members from Linear for delegation"""
        team = await self.client.team(team_id)
        members = await team.members()

        return [
            User(id=member.id, email=member.email, name=member.name)
            for member in members
        ]
