# Testing Guide

This directory contains the test suite for the Practice Routines API, following the clean architecture pattern described in `Architecture.md`.

## Directory Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests (mocked dependencies)
│   ├── test_routine_repository.py
│   └── test_routine_service.py
└── integration/             # Integration tests (multiple layers)
    └── test_api_routes.py
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests from a specific file
pytest tests/unit/test_routine_repository.py

# Run a specific test
pytest tests/unit/test_routine_repository.py::TestRoutineRepositoryGetAll::test_get_all_success
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=term-missing
```

Coverage reports are also generated in HTML format in the `htmlcov/` directory.

## Test Architecture

The tests follow the same layered architecture as the application:

### Unit Tests

**Repository Tests** (`test_routine_repository.py`)
- Mock ChromaDB collection
- Test data access logic in isolation
- Verify error handling and validation

**Service Tests** (`test_routine_service.py`)
- Mock repository and embedding service
- Test business logic
- Verify data transformations and workflows

### Integration Tests

**API Tests** (`test_api_routes.py`)
- Use Flask test client
- Mock database layer only
- Test request/response handling
- Verify HTTP status codes and error responses

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_chroma_collection` - Mock ChromaDB collection
- `mock_embedding_service` - Mock embedding service
- `mock_routine_repository` - Mock routine repository
- `sample_routine_*` - Sample data for testing
- `sample_chroma_*_result` - Sample ChromaDB responses

## Writing New Tests

### Example Unit Test

```python
@pytest.mark.unit
def test_get_all_routines(mock_routine_repository, mock_embedding_service):
    """Test description."""
    # Arrange
    mock_routine_repository.get_all.return_value = {
        "ids": ["routine_1"],
        "documents": ["Practice scales"],
        "metadatas": [{"category": "technique", "tags": "", "state": "not_completed"}]
    }
    service = RoutineService(mock_routine_repository, mock_embedding_service)

    # Act
    result = service.get_all_routines()

    # Assert
    assert len(result) == 1
    mock_routine_repository.get_all.assert_called_once()
```

### Example Integration Test

```python
@pytest.mark.integration
def test_get_routines_endpoint(client, mock_routine_repository):
    """Test description."""
    # Arrange
    mock_routine_repository.get_all.return_value = {
        "ids": ["routine_1"],
        "documents": ["Practice scales"],
        "metadatas": [{"category": "technique", "tags": "", "state": "not_completed"}]
    }

    # Act
    response = client.get('/api/routines')

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1
```

## Test Markers

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Unit tests with mocked dependencies
- `@pytest.mark.integration` - Integration tests across multiple layers
- `@pytest.mark.slow` - Tests that take significant time to run

## Coverage Goals

Current coverage: **56 tests, 100% pass rate**

Coverage by layer:
- Repository layer: 86% (13 uncovered lines are error paths)
- Service layer: 100%
- API routes: 79% (some error paths not fully tested)

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:
- Use mocks to avoid external dependencies
- Run quickly (complete in ~1.5 seconds)
- Provide clear failure messages
- Generate coverage reports

## Best Practices

1. **Isolation** - Each test is independent and can run in any order
2. **Clarity** - Use descriptive test names and docstrings
3. **Arrange-Act-Assert** - Follow AAA pattern for test structure
4. **Mocking** - Mock at the boundary (database, external services)
5. **Coverage** - Aim for high coverage but focus on meaningful tests
6. **Fast** - Keep tests fast by using mocks instead of real dependencies
