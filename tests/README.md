# Consilium Tests

This directory contains unit and integration tests for the Consilium project.

## Running Tests

### Install test dependencies

```bash
uv pip install -e ".[dev]"
```

### Run all tests

```bash
uv run pytest
```

### Run specific test file

```bash
uv run pytest tests/test_councillors.py
```

### Run tests with coverage

```bash
uv run pytest --cov=src --cov-report=html
```

### Run only unit tests (skip integration tests)

By default, tests that require AWS credentials are marked with `@pytest.mark.skip`.
To run them, remove the skip decorators or use:

```bash
uv run pytest -v
```

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_councillors.py` - Tests for councillor classes
- `test_summarizer.py` - Tests for memory/summarizer component
- `test_orchestrator.py` - Tests for orchestrator engine

## Test Fixtures

The following fixtures are available (defined in `conftest.py`):

- `simple_goal` - A simple goal for testing (web framework selection)
- `simple_resources` - Simple resources and context
- `dummy_proposal` - A single proposal example
- `dummy_critique` - A single critique example
- `dummy_proposals` - Multiple proposals (A-E)
- `dummy_critiques` - Multiple critiques

## Integration Tests

Some tests are marked with `@pytest.mark.skip` because they:
- Require AWS credentials to be configured
- Make real API calls to AWS Bedrock
- Can take longer to complete

To run integration tests:
1. Ensure your `.env` file has valid AWS credentials
2. Remove or comment out the `@pytest.mark.skip` decorator
3. Run the tests

**Warning:** Integration tests will make real API calls to AWS Bedrock.

## Test Categories

- **Unit Tests**: Test individual components in isolation (no API calls)
- **Integration Tests**: Test component interactions with real LLM APIs
- **Edge Cases**: Test error handling and unusual inputs

## Example Test Run

```bash
$ uv run pytest -v

tests/test_councillors.py::TestBaseCouncillor::test_councillor_initialization PASSED
tests/test_councillors.py::TestBaseCouncillor::test_councillor_lazy_loading PASSED
tests/test_councillors.py::TestIndividualCouncillors::test_opus_councillor PASSED
tests/test_summarizer.py::TestSummarizerInitialization::test_summarizer_creation PASSED
tests/test_orchestrator.py::TestOrchestratorInitialization::test_orchestrator_creation PASSED

======================== 25 passed, 10 skipped in 2.34s =========================
```

## Writing New Tests

When adding new tests:

1. Use descriptive test names: `test_<what_is_being_tested>`
2. Group related tests in classes: `TestComponentName`
3. Use fixtures for common test data
4. Mark integration tests with `@pytest.mark.skip` (require AWS credentials)
5. Add docstrings explaining what the test does

Example:

```python
class TestNewFeature:
    """Tests for the new feature."""

    def test_feature_basic_functionality(self, simple_goal):
        """Test that the feature works with basic input."""
        # Test implementation
        assert result is not None
```
