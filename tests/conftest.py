"""
Pytest Configuration and Fixtures
Shared test fixtures for Gherkin Taster
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.facades.issue_tracker import Issue, User, Comment
from backend.facades.git_provider import GitProvider
from backend.facades.issue_tracker import IssueTrackerProvider


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_issue():
    """Mock Linear issue"""
    return Issue(
        id="TEST-123",
        title="Implement user login feature",
        status="In Progress",
        assignee_id="user-abc-123",
        project_id="proj-xyz-789",
        custom_fields={"feature_file_path": "features/user_login.feature"},
    )


@pytest.fixture
def mock_user():
    """Mock Linear user"""
    return User(
        id="user-abc-123",
        email="developer@buckler.ai",
        name="Test Developer",
    )


@pytest.fixture
def mock_issue_tracker():
    """Mock issue tracker provider"""

    class MockIssueTracker:
        def __init__(self):
            self.issues = {}
            self.comments = []

        async def get_issue(self, issue_id: str) -> Issue:
            return self.issues.get(
                issue_id,
                Issue(
                    id=issue_id,
                    title="Test Issue",
                    status="In Progress",
                    assignee_id="user-123",
                    project_id="proj-123",
                    custom_fields={},
                ),
            )

        async def update_issue(self, issue_id: str, **kwargs) -> None:
            if issue_id in self.issues:
                # Update fields
                pass

        async def add_comment(self, issue_id: str, content: str) -> Comment:
            comment = Comment(
                id=f"comment-{len(self.comments)}",
                issue_id=issue_id,
                author_id="user-123",
                content=content,
                created_at="2025-01-01T00:00:00Z",
            )
            self.comments.append(comment)
            return comment

        async def get_users(self, team_id: str) -> list[User]:
            return [
                User(id="user-1", email="dev1@buckler.ai", name="Dev One"),
                User(id="user-2", email="dev2@buckler.ai", name="Dev Two"),
            ]

    return MockIssueTracker()


@pytest.fixture
def mock_git_provider():
    """Mock git provider"""

    class MockGitProvider:
        def __init__(self):
            self.files = {}
            self.commits = []
            self.branches = []

        async def get_file(self, repo: str, path: str, branch: str) -> str:
            key = f"{repo}:{branch}:{path}"
            return self.files.get(key, "")

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
            commit_sha = f"commit-{len(self.commits)}"
            self.commits.append(
                {
                    "sha": commit_sha,
                    "repo": repo,
                    "path": path,
                    "content": content,
                    "message": message,
                    "branch": branch,
                    "author_name": author_name,
                    "author_email": author_email,
                }
            )
            return commit_sha

        async def create_branch(
            self, repo: str, branch_name: str, from_branch: str
        ) -> None:
            self.branches.append(
                {"repo": repo, "name": branch_name, "from": from_branch}
            )

    return MockGitProvider()


@pytest.fixture
def sample_gherkin_valid():
    """Valid Gherkin feature file"""
    return """Feature: User Login
  As a registered user
  I want to log into the system
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter valid username "user@example.com"
    And I enter valid password "SecurePass123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message
"""


@pytest.fixture
def sample_gherkin_invalid():
    """Invalid Gherkin feature file"""
    return """Feature: Broken Feature
  This feature has syntax errors

  Scenario: Missing Given step
    When I do something
    Then something happens

  InvalidKeyword: This is not valid Gherkin
    Given this will cause a parse error
"""
