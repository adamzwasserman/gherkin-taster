"""
GitHub Git Provider Adapter
Implements GitProvider protocol for GitHub API
"""

from typing import Optional
import base64
from github import Github
from backend.facades.git_provider import GitProvider
from backend.config import get_settings


class GitHubAdapter(GitProvider):
    """GitHub API adapter implementing GitProvider protocol"""

    def __init__(self, api_token: Optional[str] = None):
        settings = get_settings()
        self.api_token = api_token or settings.github_api_token
        self.client = Github(self.api_token)

    async def get_file(self, repo: str, path: str, branch: str) -> str:
        """Fetch file content from GitHub repository"""
        repository = self.client.get_repo(repo)
        file_content = repository.get_contents(path, ref=branch)

        if isinstance(file_content, list):
            raise ValueError(f"Path {path} is a directory, not a file")

        # Decode base64 content
        return base64.b64decode(file_content.content).decode("utf-8")

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
        """Commit file changes to GitHub repository"""
        repository = self.client.get_repo(repo)

        # Try to get existing file
        try:
            existing_file = repository.get_contents(path, ref=branch)
            sha = existing_file.sha if not isinstance(existing_file, list) else None
        except Exception:
            sha = None

        # Create author input
        from github.InputGitAuthor import InputGitAuthor

        author = InputGitAuthor(author_name, author_email)

        # Update or create file
        if sha:
            # Update existing file
            result = repository.update_file(
                path=path,
                message=message,
                content=content,
                sha=sha,
                branch=branch,
                author=author,
            )
        else:
            # Create new file
            result = repository.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch,
                author=author,
            )

        return result["commit"].sha

    async def create_branch(
        self, repo: str, branch_name: str, from_branch: str
    ) -> None:
        """Create new branch from existing branch in GitHub"""
        repository = self.client.get_repo(repo)

        # Get source branch reference
        source_ref = repository.get_git_ref(f"heads/{from_branch}")
        source_sha = source_ref.object.sha

        # Create new branch
        repository.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_sha)
