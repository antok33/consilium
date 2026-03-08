"""
Pytest configuration and fixtures for LLM Council tests.
"""
import pytest
import sys
from pathlib import Path

# Add src to path so we can import modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def simple_goal():
    """A simple goal for testing."""
    return """# Goal: Choose a Web Framework

Decide which web framework to use for a new Python REST API project.

Requirements:
- Must support async/await
- Good documentation
- Active community
- Easy to test

Options to consider: FastAPI, Flask, Django REST Framework
"""


@pytest.fixture
def simple_resources():
    """Simple resources for testing."""
    return """# Team Context

- Team size: 3 developers
- Timeline: 2 months
- Experience: Intermediate Python, beginner async

# Constraints

- Must deploy on AWS Lambda
- Budget: Limited
"""


@pytest.fixture
def dummy_proposal():
    """A dummy proposal for testing."""
    return """## Proposal: FastAPI with Serverless Framework

### Summary
Use FastAPI as the web framework with Serverless Framework for deployment to AWS Lambda.

### Detailed Plan
1. Set up FastAPI project structure
2. Implement async endpoints
3. Add dependency injection
4. Configure Serverless Framework
5. Deploy to AWS Lambda

### Key Advantages
- Native async/await support
- Automatic OpenAPI documentation
- Fast performance
- Easy testing with pytest

### Technology Choices
- FastAPI 0.100+
- Pydantic for validation
- Serverless Framework for deployment
- pytest for testing

### Trade-offs and Considerations
- Smaller community than Flask/Django
- Relatively new framework
- Cold start times on Lambda

### Implementation Approach
Phase 1: Core API (2 weeks)
Phase 2: Testing & Documentation (2 weeks)
Phase 3: Deployment setup (1 week)
Phase 4: Production deployment (1 week)
"""


@pytest.fixture
def dummy_critique():
    """A dummy critique for testing."""
    return """## Critique

### Proposal A
**Strengths:**
- Good async support
- Modern approach

**Weaknesses:**
- Cold start concerns not addressed
- No migration plan

**Ideas Worth Adopting:**
- Serverless deployment strategy
- Pydantic validation
"""


@pytest.fixture
def dummy_proposals():
    """Multiple dummy proposals for testing."""
    return {
        "A": "Proposal A: Use FastAPI with async support and Pydantic validation.",
        "B": "Proposal B: Use Flask with Gunicorn and SQLAlchemy for traditional deployment.",
        "C": "Proposal C: Use Django REST Framework with Celery for background tasks.",
        "D": "Proposal D: Use FastAPI with GraphQL support via Strawberry.",
        "E": "Proposal E: Use Flask with async extensions and API versioning.",
    }


@pytest.fixture
def dummy_critiques():
    """Multiple dummy critiques for testing."""
    return {
        "Councillor 1": "All proposals show good understanding. FastAPI proposals are strongest.",
        "Councillor 2": "Concerned about Lambda cold starts. Flask might be safer.",
        "Councillor 3": "Django offers most features but may be overkill for this project.",
        "Councillor 4": "FastAPI + Pydantic combination is excellent for APIs.",
        "Councillor 5": "Consider hybrid approach: FastAPI with traditional deployment.",
    }
