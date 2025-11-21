"""
Delegation Workflow
Pure functions for delegating features to team members
"""

from typing import Optional
from backend.facades.issue_tracker import IssueTrackerProvider, Issue


async def delegate_feature(
    *,
    issue: Issue,
    assignee_id: str,
    delegator_name: str,
    comment: Optional[str] = None,
    issue_tracker: IssueTrackerProvider,
) -> dict:
    """
    Execute delegation workflow: reassign issue and add comment

    Args:
        issue: Linear issue metadata
        assignee_id: Linear user ID to assign to
        delegator_name: Name of person delegating
        comment: Optional delegation reason
        issue_tracker: Issue tracker provider (Linear)

    Returns:
        dict: {
            "issue_updated": bool,
            "assignee_id": str,
            "comment_id": str
        }
    """
    # Update issue assignee
    try:
        await issue_tracker.update_issue(issue.id, assignee_id=assignee_id)
        issue_updated = True
    except Exception:
        issue_updated = False

    # Build delegation comment
    comment_body = f"🔄 Feature delegated by {delegator_name}"
    if comment:
        comment_body += f"\n\n**Reason:** {comment}"

    # Add comment to issue
    created_comment = await issue_tracker.add_comment(issue.id, comment_body)

    return {
        "issue_updated": issue_updated,
        "assignee_id": assignee_id,
        "comment_id": created_comment.id,
    }


async def route_feature(
    *,
    issue: Issue,
    target_status: str,
    router_name: str,
    reason: Optional[str] = None,
    issue_tracker: IssueTrackerProvider,
) -> dict:
    """
    Execute routing workflow: change status and add routing comment

    Args:
        issue: Linear issue metadata
        target_status: New workflow state (e.g., "Technical Review", "Backlog")
        router_name: Name of person routing
        reason: Optional routing reason
        issue_tracker: Issue tracker provider (Linear)

    Returns:
        dict: {
            "issue_updated": bool,
            "new_status": str,
            "comment_id": str
        }
    """
    # Update issue status
    try:
        await issue_tracker.update_issue(issue.id, status=target_status)
        issue_updated = True
    except Exception:
        issue_updated = False

    # Build routing comment
    comment_body = f"↪️ Feature routed to **{target_status}** by {router_name}"
    if reason:
        comment_body += f"\n\n**Reason:** {reason}"

    # Add comment to issue
    created_comment = await issue_tracker.add_comment(issue.id, comment_body)

    return {
        "issue_updated": issue_updated,
        "new_status": target_status,
        "comment_id": created_comment.id,
    }
