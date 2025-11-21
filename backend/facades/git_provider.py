"""
Git Provider Protocol
Defines interface for Git hosting providers (GitHub, GitLab, Bitbucket)
"""

from typing import Protocol


class GitProvider(Protocol):
    """Protocol for Git provider integrations"""

    async def get_file(self, repo: str, path: str, branch: str) -> str:
        """Fetch file content from branch"""
        ...

    async def commit_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        *,
        author_name: str,
        author_email: str,
    ) -> str:
        """Commit file changes, return commit SHA"""
        ...

    async def create_branch(self, repo: str, branch_name: str, from_branch: str) -> None:
        """Create new branch from existing branch"""
        ...
