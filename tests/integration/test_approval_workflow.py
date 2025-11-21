"""
Integration Tests: Approval Workflow
Tests for backend/workflows/approval_workflow.py
"""

import pytest
from backend.workflows.approval_workflow import approve_feature
from backend.facades.issue_tracker import Issue


@pytest.mark.asyncio
async def test_approve_feature_creates_branch(
    mock_issue, mock_issue_tracker, mock_git_provider, sample_gherkin_valid
):
    """Test approval workflow creates feature branch"""
    result = await approve_feature(
        issue=mock_issue,
        feature_content=sample_gherkin_valid,
        repo="buckler/test-repo",
        feature_file_path="features/user_login.feature",
        base_branch="main",
        author_name="Test User",
        author_email="test@buckler.ai",
        issue_tracker=mock_issue_tracker,
        git_provider=mock_git_provider,
    )

    assert len(mock_git_provider.branches) == 1
    assert mock_git_provider.branches[0]["name"] == "feature/test-123-gherkin-approval"
    assert mock_git_provider.branches[0]["from"] == "main"


@pytest.mark.asyncio
async def test_approve_feature_commits_file(
    mock_issue, mock_issue_tracker, mock_git_provider, sample_gherkin_valid
):
    """Test approval workflow commits feature file"""
    result = await approve_feature(
        issue=mock_issue,
        feature_content=sample_gherkin_valid,
        repo="buckler/test-repo",
        feature_file_path="features/user_login.feature",
        base_branch="main",
        author_name="Test User",
        author_email="test@buckler.ai",
        issue_tracker=mock_issue_tracker,
        git_provider=mock_git_provider,
    )

    assert len(mock_git_provider.commits) == 1
    commit = mock_git_provider.commits[0]
    assert commit["path"] == "features/user_login.feature"
    assert commit["content"] == sample_gherkin_valid
    assert commit["branch"] == "feature/test-123-gherkin-approval"
    assert "commit_sha" in result
    assert result["commit_sha"] == commit["sha"]


@pytest.mark.asyncio
async def test_approve_feature_adds_comment(
    mock_issue, mock_issue_tracker, mock_git_provider, sample_gherkin_valid
):
    """Test approval workflow adds comment to issue"""
    result = await approve_feature(
        issue=mock_issue,
        feature_content=sample_gherkin_valid,
        repo="buckler/test-repo",
        feature_file_path="features/user_login.feature",
        base_branch="main",
        author_name="Test User",
        author_email="test@buckler.ai",
        issue_tracker=mock_issue_tracker,
        git_provider=mock_git_provider,
    )

    assert len(mock_issue_tracker.comments) == 1
    comment = mock_issue_tracker.comments[0]
    assert "approved" in comment.content.lower()
    assert "feature/test-123-gherkin-approval" in comment.content


@pytest.mark.asyncio
async def test_approve_feature_generates_commit_message(
    mock_issue, mock_issue_tracker, mock_git_provider, sample_gherkin_valid
):
    """Test approval workflow generates semantic commit message"""
    result = await approve_feature(
        issue=mock_issue,
        feature_content=sample_gherkin_valid,
        repo="buckler/test-repo",
        feature_file_path="features/user_login.feature",
        base_branch="main",
        author_name="Test User",
        author_email="test@buckler.ai",
        issue_tracker=mock_issue_tracker,
        git_provider=mock_git_provider,
    )

    assert "commit_message" in result
    message = result["commit_message"]
    assert "feat:" in message.lower() or "feature" in message.lower()
    assert "User Login" in message or mock_issue.title in message
