"""
Issue Tracker Provider Protocol
Defines interface for issue tracking systems (Linear, Jira, GitHub Issues)
"""

from typing import Protocol, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    """Issue metadata"""
    id: str
    title: str
    status: str
    assignee_id: Optional[str]
    project_id: str
    custom_fields: dict[str, any]


@dataclass(frozen=True)
class User:
    """User metadata"""
    id: str
    email: str
    name: str


@dataclass(frozen=True)
class Comment:
    """Comment metadata"""
    id: str
    issue_id: str
    author_id: str
    content: str
    created_at: str


class IssueTrackerProvider(Protocol):
    """Protocol for issue tracker integrations"""

    async def get_issue(self, issue_id: str) -> Issue:
        """Fetch issue metadata"""
        ...

    async def update_issue(
        self,
        issue_id: str,
        *,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> None:
        """Update issue fields"""
        ...

    async def add_comment(self, issue_id: str, content: str) -> Comment:
        """Add comment to issue"""
        ...

    async def get_users(self, team_id: str) -> list[User]:
        """Get team members for delegation"""
        ...
