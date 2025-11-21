# Gherkin Taster

A stateless web application for business users to review, edit, and approve AI-generated Gherkin feature specifications with Linear integration and Git-based version control.

## Overview

Gherkin Taster enables business validation of BDD specifications before test implementation, maintaining complete audit trails for SOC2 Type II compliance.

### Key Features

- **Business-Friendly Gherkin Editor**: Real-time syntax validation with CodeMirror
- **Linear Integration**: Workflow state tracking, assignee management, comment threading
- **Git Version Control**: Immutable commit history with AI-generated messages
- **Stateless Architecture**: All state derived from Linear and Git - no application database
- **Protocol-Based Design**: Pluggable providers for auth, issue tracking, and Git services

## Architecture

- **Backend**: FastAPI with pure function architecture
- **Frontend**: HTMX + Jinja2 (server-side rendering)
- **Storage**: Git (features), Linear (workflow state), Redis (sessions/locks)
- **JavaScript**: <100 lines (CodeMirror only)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Linear API token
- GitHub API token
- (Optional) Anthropic API key for AI commit messages

### Development Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API tokens
vim .env

# Start services
docker-compose up --build

# Access application
open http://localhost:8100
```

### Configuration

Create `gherkin-config.yaml` in your repository root:

```yaml
linear:
  org: your-org
  team: ENG

features:
  - path: tests/features
    issue_pattern: "{issue_id}-*.feature"

commit_message:
  generator: llm  # or 'template'
  llm:
    provider: anthropic
    model: claude-sonnet-4
    max_tokens: 200
```

## Project Structure

```
gherkin-taster/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── config.py           # Environment configuration
│   ├── routes/             # HTMX endpoints
│   ├── workflows/          # Pure function workflows
│   ├── facades/            # Protocol definitions
│   ├── adapters/           # Linear/GitHub implementations
│   ├── gherkin/            # Validation, parsing
│   └── middleware/         # Auth, rate limiting
├── app/
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS, JS assets
├── tests/
│   ├── unit/               # Pure function tests
│   └── integration/        # Workflow tests
└── docs/
    └── architecture.md     # Detailed architecture doc
```

## Testing

```bash
# Run all tests
docker-compose exec gherkin-web pytest

# Run with coverage
docker-compose exec gherkin-web pytest --cov=backend
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment instructions.

## License

Proprietary - Buckler Corporation

## Related Projects

- [IDD](../idd/) - Investment Due Diligence application
- [IAM](../iam/) - Identity & Access Management service
