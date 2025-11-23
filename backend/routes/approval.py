"""
Approval Routes
HTMX endpoints for approve, delegate, route actions
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.post("/{issue_id}/approve")
async def approve_feature(issue_id: str):
    """Approve feature and commit to Git"""
    # TODO: Implement approval workflow
    return {"status": "approved", "commit_sha": "placeholder"}


@router.post("/{issue_id}/delegate")
async def delegate_feature(issue_id: str, delegate_to_user_id: str, comment: str):
    """Delegate feature review to another user"""
    # TODO: Implement delegation workflow
    return {"status": "delegated", "assignee": delegate_to_user_id}


@router.post("/{issue_id}/route")
async def route_for_input(issue_id: str, route_to_user_id: str, comment: str):
    """Route feature to another user for input"""
    # TODO: Implement routing workflow
    return {"status": "routed", "assignee": route_to_user_id}


@router.get("/{issue_id}/validate", response_class=HTMLResponse)
async def validate_gherkin(request: Request, issue_id: str):
    """Validate Gherkin syntax (HTMX partial)"""
    # TODO: Implement actual Gherkin validation
    return """
    <div class="mt-4">
        <div class="rounded-md bg-green-50 p-4">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-green-800">Gherkin syntax is valid</p>
                </div>
            </div>
        </div>
    </div>
    """


@router.get("/{issue_id}/delegate-form", response_class=HTMLResponse)
async def get_delegate_form(request: Request, issue_id: str):
    """Get delegation modal form (HTMX partial)"""
    # TODO: Fetch actual team members from Linear
    return """
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Delegate Feature</h3>
        <form hx-post="/approval/{issue_id}/delegate" hx-swap="none">
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Delegate to:
                </label>
                <select name="delegate_to_user_id" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="">Select team member...</option>
                </select>
            </div>
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Comment:
                </label>
                <textarea name="comment" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" data-close-modal class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                    Delegate
                </button>
            </div>
        </form>
    </div>
    """
