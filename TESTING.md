# Testing Guide for EngineerOS

Complete guide to running, writing, and maintaining tests.

## Quick Start

### Backend Tests

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest -m unit      # Unit tests only
pytest -m integration # Integration tests only
pytest -m security   # Security tests only
pytest -m "not slow" # Skip slow tests
```

### Frontend Tests

```bash
# Install dependencies
npm install

# Run tests
npm run test           # Watch mode
npm run test -- --run # Single run
npm run test:coverage # With coverage report
npm run test:ui       # Interactive UI
```

### E2E Tests

```bash
# Start services first
docker compose up -d

# Run E2E tests
npm run e2e

# Debug mode
npm run e2e:debug

# View report
npx playwright show-report
```

---

## Test Structure

### Backend Tests

```
backend/
  tests/
    conftest.py              # Shared fixtures
    test_auth.py             # Authentication tests
    test_security.py         # Security/RBAC tests
    test_config.py           # Configuration tests
    test_api_endpoints.py    # Endpoint integration tests
    test_runner.py           # Test runner script
```

### Frontend Tests

```
tests/
  setup.ts                   # Vitest setup
  components/
    example.test.tsx         # Component tests
  e2e/
    main.spec.ts             # E2E tests
vitest.config.ts            # Vitest config
playwright.config.ts        # Playwright config
```

---

## Writing Tests

### Backend Unit Test Example

```python
import pytest
from app.auth import hash_password, verify_password

@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a valid bcrypt hash."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")
    
    def test_verify_password_success(self):
        """Test that verify_password returns True for correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
```

### Backend Integration Test Example

```python
@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_login_with_demo_credentials(self, client: TestClient):
        """Test login endpoint with demo credentials."""
        response = client.post(
            "/auth/login",
            json={
                "email": "demo@engineeros.io",
                "password": "demo1234",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
```

### Frontend Component Test Example

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('MyComponent', () => {
  it('should render text', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected text')).toBeInTheDocument()
  })

  it('should handle clicks', async () => {
    const user = userEvent.setup()
    render(<MyComponent onSubmit={vi.fn()} />)
    
    await user.click(screen.getByRole('button'))
    expect(onSubmit).toHaveBeenCalled()
  })
})
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test'

test('should login successfully', async ({ page, authenticatedAPI }) => {
  const response = await page.request.post(
    'http://localhost:8000/auth/login',
    {
      data: {
        email: 'demo@engineeros.io',
        password: 'demo1234',
      },
    }
  )
  
  expect(response.ok()).toBeTruthy()
  const data = await response.json()
  expect(data).toHaveProperty('access_token')
})
```

---

## Test Markers/Tags

### Backend Markers

- `@pytest.mark.unit` - Fast tests, no external dependencies
- `@pytest.mark.integration` - Tests requiring services/database
- `@pytest.mark.auth` - Authentication-specific tests
- `@pytest.mark.security` - Security/RBAC tests
- `@pytest.mark.slow` - Tests that take longer (skip with `-m "not slow"`)

### Running Tests by Marker

```bash
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m "auth or security"  # Multiple markers
pytest -m "not slow"        # Exclude slow tests
```

---

## Coverage Requirements

**Target: 70% code coverage**

### Backend Coverage

```bash
cd backend
pytest --cov=app --cov-report=html --cov-fail-under=70
# Report: htmlcov/index.html
```

### Frontend Coverage

```bash
npm run test:coverage
# Report: coverage/index.html
```

### Check Specific Module

```bash
# Backend
pytest backend/tests/test_auth.py --cov=app.auth --cov-report=term

# Frontend
npm run test -- tests/components --coverage
```

---

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/ci-cd.yml` automatically:

1. **Backend Tests**
   - Runs unit tests (fast)
   - Runs integration tests (with PostgreSQL)
   - Checks coverage >= 70%
   - Uploads to Codecov

2. **Frontend Tests**
   - Type checking
   - Linting
   - Unit tests with coverage
   - Uploads to Codecov

3. **Code Quality**
   - Python formatting (black)
   - Python linting (ruff)
   - JavaScript/TypeScript formatting

4. **Security Scanning**
   - Bandit for Python
   - npm audit for dependencies

5. **E2E Tests** (on PR)
   - Runs Playwright tests
   - Uploads test artifacts

### Running CI Locally

```bash
# Simulate CI pipeline
cd backend && pytest && cd ..
npm run type-check
npm run lint
npm run test -- --run
npm run e2e
```

---

## Pre-commit Hooks

Automatically run checks before committing:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Manual run on all files
pre-commit run --all-files

# Skip checks
git commit --no-verify
```

**Included Hooks:**
- Black (Python formatting)
- Ruff (Python linting)
- MyPy (Type checking)
- Bandit (Security scanning)
- Trailing whitespace removal
- Large file detection
- Merge conflict detection
- Private key detection

---

## Debugging Tests

### Backend

```bash
# Run with verbose output
pytest -vv

# Run specific test
pytest backend/tests/test_auth.py::TestPasswordHashing::test_hash_password_creates_hash

# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Run with short summary
pytest -q
```

### Frontend

```bash
# Run in watch mode
npm run test:watch

# Interactive UI
npm run test:ui

# Debug single test
npm run test -- tests/components/example.test.tsx --inspect
```

### E2E

```bash
# Debug mode (opens browser)
npm run e2e:debug

# Trace mode
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip

# Screenshot on failure
# Already configured in playwright.config.ts
```

---

## Best Practices

### ✅ DO

- **Test behavior, not implementation** - Test what users see, not internal code
- **Use descriptive test names** - `test_should_return_401_for_invalid_credentials`
- **Keep tests independent** - No test should depend on another test
- **Mock external services** - Use fixtures/mocks for databases, APIs
- **Test error cases** - Both success and failure paths
- **Use fixtures** - Avoid duplicating setup code
- **Organize by feature** - Group related tests together
- **Add comments for complex tests** - Explain "why", not "what"

### ❌ DON'T

- **Test implementation details** - Implementation can change
- **Use vague names** - `test_function` is too generic
- **Create test dependencies** - Tests must be runnable in any order
- **Skip error testing** - Test both happy and sad paths
- **Use hardcoded values** - Use factories/fixtures
- **Rely on test order** - Each test must be independent
- **Create slow tests** - Keep tests fast (< 1s ideal)
- **Mock everything** - Only mock external dependencies

---

## Test Data

### Backend Fixtures

Defined in `conftest.py`:

```python
@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers(valid_jwt_token: str) -> dict:
    """Authorization headers with valid JWT."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}

@pytest.fixture
def auth_test_data():
    """Test data for authentication."""
    return AuthTestData()
```

### Faker for Random Data

```python
def test_with_fake_data(faker):
    email = faker.email()
    name = faker.name()
    password = faker.password()
```

---

## Coverage Reports

### Backend

```bash
# Generate HTML report
cd backend
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Frontend

```bash
# Generate coverage report
npm run test:coverage

# Open in browser
open coverage/index.html
```

### View Coverage By Module

```bash
# Backend specific module
pytest backend/tests/test_auth.py --cov=app.auth --cov-report=term-missing

# Frontend specific component
npm run test -- tests/components/Button --coverage
```

---

## Troubleshooting

### Tests Won't Run

```bash
# Backend: Ensure environment variables set
export ENVIRONMENT=testing
export JWT_SECRET_KEY=test-key
pytest backend/tests/

# Frontend: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run test
```

### Import Errors

```bash
# Backend: Add __init__.py to test directories
touch backend/tests/__init__.py

# Frontend: Check vitest.config.ts alias configuration
```

### Database Connection Errors

```bash
# Backend integration tests need PostgreSQL
docker compose up postgres -d
pytest -m integration

# Stop after testing
docker compose down
```

### E2E Tests Timeout

```bash
# Ensure services are running
docker compose ps

# Check API is accessible
curl http://localhost:8000/health

# Increase timeout
npx playwright test --timeout 60000
```

---

## Continuous Improvement

### Add Tests for New Features

1. Write failing test first (TDD)
2. Implement feature
3. Test passes
4. Verify test actually tests the feature

### Monitor Coverage Trends

```bash
# Track coverage over time
pytest --cov=app --cov-report=json
# Commit coverage.json to track trends
```

### Regular Test Review

- Monthly: Review test effectiveness
- Quarterly: Refactor test code
- When: Coverage drops below 70%

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

---

**Happy testing!** 🧪
