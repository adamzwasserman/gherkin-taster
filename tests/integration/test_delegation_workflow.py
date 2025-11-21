"""
Integration Tests: Delegation Workflow
Tests for backend/workflows/delegation_workflow.py
"""

import pytest
from backend.workflows.delegation_workflow import delegate_feature, route_feature


@pytest.mark.asyncio
async def test_delegate_feature_updates_assignee(mock_issue, mock_issue_tracker):
    """Test delegation workflow updates issue assignee"""
    result = await delegate_feature(
        issue=mock_issue,
        assignee_id="user-new-123",
        delegator_name="Manager",
        comment="Delegating to specialist",
        issue_tracker=mock_issue_tracker,
    )

    assert result["issue_updated"] is True
    assert result["assignee_id"] == "user-new-123"


@pytest.mark.asyncio
async def test_delegate_feature_adds_comment(mock_issue, mock_issue_tracker):
    """Test delegation workflow adds delegation comment"""
    result = await delegate_feature(
        issue=mock_issue,
        assignee_id="user-new-123",
        delegator_name="Manager",
        comment="Requires domain expertise",
        issue_tracker=mock_issue_tracker,
    )

    assert len(mock_issue_tracker.comments) == 1
    comment = mock_issue_tracker.comments[0]
    assert "delegated" in comment.content.lower()
    assert "Manager" in comment.content
    assert "Requires domain expertise" in comment.content


@pytest.mark.asyncio
async def test_delegate_feature_without_comment(mock_issue, mock_issue_tracker):
    """Test delegation workflow works without optional comment"""
    result = await delegate_feature(
        issue=mock_issue,
        assignee_id="user-new-123",
        delegator_name="Manager",
        issue_tracker=mock_issue_tracker,
    )

    assert result["issue_updated"] is True
    assert len(mock_issue_tracker.comments) == 1


@pytest.mark.asyncio
async def test_route_feature_updates_status(mock_issue, mock_issue_tracker):
    """Test routing workflow updates issue status"""
    result = await route_feature(
        issue=mock_issue,
        target_status="Technical Review",
        router_name="Product Owner",
        reason="Needs technical validation",
        issue_tracker=mock_issue_tracker,
    )

    assert result["issue_updated"] is True
    assert result["new_status"] == "Technical Review"


@pytest.mark.asyncio
async def test_route_feature_adds_comment(mock_issue, mock_issue_tracker):
    """Test routing workflow adds routing comment"""
    result = await route_feature(
        issue=mock_issue,
        target_status="Backlog",
        router_name="Product Owner",
        reason="Not ready for implementation",
        issue_tracker=mock_issue_tracker,
    )

    assert len(mock_issue_tracker.comments) == 1
    comment = mock_issue_tracker.comments[0]
    assert "routed" in comment.content.lower()
    assert "Backlog" in comment.content
    assert "Product Owner" in comment.content
    assert "Not ready for implementation" in comment.content


@pytest.mark.asyncio
async def test_route_feature_without_reason(mock_issue, mock_issue_tracker):
    """Test routing workflow works without optional reason"""
    result = await route_feature(
        issue=mock_issue,
        target_status="In Progress",
        router_name="Tech Lead",
        issue_tracker=mock_issue_tracker,
    )

    assert result["issue_updated"] is True
    assert len(mock_issue_tracker.comments) == 1
