"""
Approval Workflow
Pure functions for Gherkin feature approval process
"""

from typing import Optional
from backend.facades.issue_tracker import IssueTrackerProvider, Issue
from backend.facades.git_provider import GitProvider


async def approve_feature(
    *,
    issue: Issue,
    feature_content: str,
    repo: str,
    feature_file_path: str,
    base_branch: str,
    author_name: str,
    author_email: str,
    issue_tracker: IssueTrackerProvider,
    git_provider: GitProvider,
    llm_api_key: Optional[str] = None,
) -> dict:
    """
    Execute approval workflow: commit feature file and update issue status

    Args:
        issue: Linear issue metadata
        feature_content: Approved Gherkin feature file content
        repo: GitHub repository (e.g., "org/repo")
        feature_file_path: Path in repo (e.g., "features/user_login.feature")
        base_branch: Target branch (e.g., "main")
        author_name: Commit author name
        author_email: Commit author email
        issue_tracker: Issue tracker provider (Linear)
        git_provider: Git provider (GitHub)
        llm_api_key: Optional API key for LLM-generated commit message

    Returns:
        dict: {
            "commit_sha": str,
            "commit_message": str,
            "issue_updated": bool,
            "branch_name": str
        }
    """
    # Generate branch name from issue ID
    branch_name = f"feature/{issue.id.lower()}-gherkin-approval"

    # Create feature branch
    await git_provider.create_branch(
        repo=repo, branch_name=branch_name, from_branch=base_branch
    )

    # Generate commit message
    commit_message = await _generate_commit_message(
        issue=issue,
        feature_content=feature_content,
        llm_api_key=llm_api_key,
    )

    # Commit feature file to branch
    commit_sha = await git_provider.commit_file(
        repo=repo,
        path=feature_file_path,
        content=feature_content,
        message=commit_message,
        branch=branch_name,
        author_name=author_name,
        author_email=author_email,
    )

    # Update Linear issue status to approved
    try:
        await issue_tracker.update_issue(issue.id, status="Approved")
        issue_updated = True
    except Exception:
        issue_updated = False

    # Add comment with commit info
    await issue_tracker.add_comment(
        issue.id,
        f"✅ Gherkin feature approved and committed\n\n"
        f"**Branch:** `{branch_name}`\n"
        f"**Commit:** `{commit_sha[:8]}`\n"
        f"**File:** `{feature_file_path}`",
    )

    return {
        "commit_sha": commit_sha,
        "commit_message": commit_message,
        "issue_updated": issue_updated,
        "branch_name": branch_name,
    }


async def _generate_commit_message(
    *,
    issue: Issue,
    feature_content: str,
    llm_api_key: Optional[str] = None,
) -> str:
    """
    Generate commit message for feature approval

    Args:
        issue: Linear issue metadata
        feature_content: Gherkin feature file content
        llm_api_key: Optional API key for LLM-generated message

    Returns:
        str: Commit message
    """
    if llm_api_key:
        # TODO: Call LLM API to generate semantic commit message
        # For now, use template-based message
        pass

    # Extract feature name from first line
    lines = feature_content.split("\n")
    feature_line = next((line for line in lines if line.strip().startswith("Feature:")), None)
    feature_name = feature_line.split("Feature:", 1)[1].strip() if feature_line else issue.title

    return f"feat: Add Gherkin specification for {feature_name}\n\nApproved feature specification for {issue.id}: {issue.title}"
