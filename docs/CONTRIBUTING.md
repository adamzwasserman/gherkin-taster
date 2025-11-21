# Contributing to Gherkin Taster

Thank you for your interest in contributing to Gherkin Taster! This document provides guidelines and instructions for contributors.

## Development Setup

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- uv package manager
- Git

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/buckler/gherkin-taster.git
   cd gherkin-taster
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your Linear and GitHub tokens
   ```

4. Start development services:
   ```bash
   docker-compose up
   ```

5. Run tests:
   ```bash
   uv run pytest
   ```

## Architecture Principles

Gherkin Taster follows these core principles:

### 1. Pure Functions

All business logic is implemented as pure functions with explicit dependencies:

```python
# Good: Pure function with dependencies passed in
async def approve_feature(
    *,
    issue: Issue,
    feature_content: str,
    issue_tracker: IssueTrackerProvider,
    git_provider: GitProvider
) -> dict:
    # Function logic here
    pass

# Bad: Function with hidden dependencies
async def approve_feature(issue_id: str, content: str):
    linear = Linear()  # Hidden dependency
    github = GitHub()  # Hidden dependency
    # Function logic here
    pass
```

### 2. Protocol-Based Architecture

Use Python Protocols for dependency abstraction:

```python
# Define protocol
class IssueTrackerProvider(Protocol):
    async def get_issue(self, issue_id: str) -> Issue: ...

# Implement adapter
class LinearAdapter(IssueTrackerProvider):
    async def get_issue(self, issue_id: str) -> Issue:
        # Implementation
        pass
```

### 3. Stateless Design

No database - all state derived from Linear (issue tracker) and Git:

- Feature assignments: Linear issue assignments
- Feature status: Linear workflow states
- Feature content: GitHub repository files
- Edit locks: Redis TTL-based (temporary only)

### 4. Minimal JavaScript

Target: <100 lines of JavaScript total. Use HTMX for interactivity:

```html
<!-- Good: HTMX handles server interaction -->
<button hx-post="/approval/123/approve" hx-swap="none">
    Approve
</button>

<!-- Bad: Custom JavaScript for AJAX -->
<button onclick="fetch('/approval/123/approve')...">
    Approve
</button>
```

## Code Style

### Python

Follow PEP 8 with these tools:

```bash
# Format code
uv run black backend/

# Sort imports
uv run isort backend/

# Type checking
uv run mypy backend/

# Run all checks
uv run ruff check backend/
```

### Templates

- Use Jinja2 templates with Tailwind CSS
- Keep templates semantic and accessible
- Avoid inline styles

### Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_SNAKE_CASE`
- Protocol implementations: `*Adapter` (e.g., `LinearAdapter`, `GitHubAdapter`)
- Workflow functions: `*_workflow.py` (e.g., `approval_workflow.py`)

## Testing

### Test Structure

```
tests/
├── unit/               # Pure function tests (no I/O)
│   ├── test_validation.py
│   └── test_parsing.py
└── integration/        # Workflow tests (mocked adapters)
    ├── test_approval_workflow.py
    └── test_delegation_workflow.py
```

### Writing Tests

```python
# Unit test example
def test_validate_gherkin_valid(sample_gherkin_valid):
    result = validate_gherkin(sample_gherkin_valid)
    assert result.is_valid is True

# Integration test example
@pytest.mark.asyncio
async def test_approve_feature(mock_issue, mock_issue_tracker, mock_git_provider):
    result = await approve_feature(
        issue=mock_issue,
        feature_content="Feature: Test",
        issue_tracker=mock_issue_tracker,
        git_provider=mock_git_provider
    )
    assert result["commit_sha"] is not None
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_validation.py

# With coverage
uv run pytest --cov=backend --cov-report=html

# Fast mode (skip slow tests)
uv run pytest -m "not slow"
```

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following architecture principles
- Add tests for new functionality
- Update documentation if needed

### 3. Run Quality Checks

```bash
# Format and lint
uv run black backend/
uv run ruff check backend/

# Run tests
uv run pytest

# Type checking
uv run mypy backend/
```

### 4. Commit Changes

Follow conventional commit format:

```bash
git commit -m "feat: Add delegation modal component"
git commit -m "fix: Handle missing feature file gracefully"
git commit -m "docs: Update deployment guide"
git commit -m "test: Add unit tests for validation"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create pull request on GitHub with:
- Clear description of changes
- Link to related Linear issue (if applicable)
- Screenshots for UI changes

## Adding New Features

### Adding a New Route

1. Create route handler in `backend/routes/`:
   ```python
   from fastapi import APIRouter

   router = APIRouter()

   @router.get("/your-route")
   async def your_handler():
       return {"message": "Hello"}
   ```

2. Register in `backend/app.py`:
   ```python
   from backend.routes import your_module

   app.include_router(your_module.router, prefix="/your-prefix")
   ```

### Adding a New Workflow

1. Create workflow module in `backend/workflows/`:
   ```python
   async def your_workflow(
       *,
       issue: Issue,
       issue_tracker: IssueTrackerProvider,
       git_provider: GitProvider
   ) -> dict:
       # Workflow logic
       pass
   ```

2. Write integration tests in `tests/integration/`

### Adding a New Provider Adapter

1. Define protocol in `backend/facades/`:
   ```python
   class YourProvider(Protocol):
       async def your_method(self) -> str: ...
   ```

2. Implement adapter in `backend/adapters/`:
   ```python
   class YourAdapter(YourProvider):
       async def your_method(self) -> str:
           # Implementation
           pass
   ```

## Documentation

Update documentation when:
- Adding new features
- Changing architecture
- Modifying deployment process
- Adding configuration options

Documentation locations:
- `README.md`: Overview and quick start
- `docs/DEPLOYMENT.md`: Deployment instructions
- `docs/CONTRIBUTING.md`: This file
- Docstrings: All public functions and classes

## Questions and Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and discussions
- **Linear**: Internal development planning (Buckler team)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
