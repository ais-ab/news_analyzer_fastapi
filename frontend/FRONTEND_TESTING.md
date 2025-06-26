# Frontend Testing Guide

This document provides a comprehensive guide to testing the News Analyzer frontend application.

## 🧪 Test Types

### 1. Unit Tests
- **Location**: `src/__tests__/`
- **Framework**: Jest + React Testing Library
- **Coverage**: Components, pages, services, utilities
- **Command**: `npm test` or `npm run test:coverage`

### 2. E2E Tests
- **Location**: `e2e/`
- **Framework**: Playwright
- **Coverage**: User workflows, integration scenarios
- **Command**: `npm run test:e2e`

### 3. Integration Tests
- **Location**: `src/__tests__/services/`
- **Framework**: Jest + Axios mocks
- **Coverage**: API service functions

## 🚀 Quick Start

### Install Dependencies
```bash
cd frontend
npm install
```

### Run All Tests
```bash
# Using the test runner script
node scripts/test-runner.js

# Or run individual test types
npm run test:coverage    # Unit tests with coverage
npm run test:e2e         # E2E tests
npm run test:e2e:ui      # E2E tests with UI
npm run test:e2e:headed  # E2E tests in headed mode
```

## 📁 Test Structure

```
frontend/
├── src/__tests__/
│   ├── utils/
│   │   └── test-utils.tsx          # Custom render function with providers
│   ├── components/
│   │   └── Layout.test.tsx         # Component unit tests
│   ├── pages/
│   │   ├── Login.test.tsx          # Page unit tests
│   │   ├── Dashboard.test.tsx
│   │   └── Sources.test.tsx
│   └── services/
│       └── api.test.ts             # API service tests
├── e2e/
│   ├── auth.spec.ts                # Authentication E2E tests
│   ├── dashboard.spec.ts           # Dashboard E2E tests
│   └── sources.spec.ts             # Sources management E2E tests
├── scripts/
│   └── test-runner.js              # Comprehensive test runner
└── playwright.config.ts            # Playwright configuration
```

## 🧩 Unit Testing

### Test Utilities
The `test-utils.tsx` file provides a custom render function that includes all necessary providers:
- React Query Client
- React Router
- Authentication Context

### Writing Unit Tests

#### Component Test Example
```typescript
import React from 'react';
import { render, screen, fireEvent } from '../utils/test-utils';
import MyComponent from '../../components/MyComponent';

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  test('handles user interaction', () => {
    render(<MyComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Clicked!')).toBeInTheDocument();
  });
});
```

#### Page Test Example
```typescript
import React from 'react';
import { render, screen, waitFor } from '../utils/test-utils';
import MyPage from '../../pages/MyPage';

// Mock dependencies
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { client_id: 'testuser' } }),
}));

jest.mock('react-query', () => ({
  useQuery: () => ({ data: mockData, isLoading: false }),
}));

describe('MyPage', () => {
  test('renders page content', () => {
    render(<MyPage />);
    expect(screen.getByText('Page Title')).toBeInTheDocument();
  });
});
```

### Mocking Strategies

#### API Calls
```typescript
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  })),
}));
```

#### React Query
```typescript
jest.mock('react-query', () => ({
  useQuery: () => ({
    data: mockData,
    isLoading: false,
    error: null,
  }),
  useMutation: () => ({
    mutate: jest.fn(),
    isLoading: false,
  }),
}));
```

## 🌐 E2E Testing

### Playwright Setup
Playwright is configured to run tests against the development server and supports multiple browsers.

### Writing E2E Tests

#### Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: login, navigate, etc.
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass');
    await page.click('button[type="submit"]');
  });

  test('should perform user action', async ({ page }) => {
    await page.goto('/target-page');
    await page.click('button:has-text("Action")');
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

#### Test Patterns

**Authentication Setup**
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'testpass');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
});
```

**Form Interaction**
```typescript
await page.fill('input[name="field"]', 'value');
await page.selectOption('select[name="dropdown"]', 'option');
await page.check('input[type="checkbox"]');
await page.click('button[type="submit"]');
```

**Assertions**
```typescript
await expect(page).toHaveURL('/expected-url');
await expect(page.locator('text=Expected Text')).toBeVisible();
await expect(page.locator('input[name="field"]')).toHaveValue('expected');
```

## 📊 Test Coverage

### Coverage Goals
- **Statements**: 80%+
- **Branches**: 80%+
- **Functions**: 80%+
- **Lines**: 80%+

### Coverage Report
Run `npm run test:coverage` to generate a coverage report. The report will be available in the `coverage/` directory.

## 🔧 Test Configuration

### Jest Configuration
Jest is configured via `package.json` with:
- React Testing Library setup
- Coverage reporting
- Mock file handling

### Playwright Configuration
Playwright is configured in `playwright.config.ts` with:
- Multiple browser support
- Development server integration
- Screenshot and trace capture on failure

## 🚨 Common Issues & Solutions

### 1. Provider Errors
**Issue**: Component requires context providers
**Solution**: Use the custom render function from `test-utils.tsx`

### 2. Async Operations
**Issue**: Tests failing due to async operations
**Solution**: Use `waitFor` or `findBy` queries
```typescript
await waitFor(() => {
  expect(screen.getByText('Loaded Content')).toBeInTheDocument();
});
```

### 3. Mock Cleanup
**Issue**: Mocks persisting between tests
**Solution**: Use `jest.clearAllMocks()` in `beforeEach`

### 4. E2E Timeouts
**Issue**: E2E tests timing out
**Solution**: Increase timeout or add explicit waits
```typescript
await page.waitForSelector('selector', { timeout: 10000 });
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: npm run test:e2e
```

## 🎯 Best Practices

### 1. Test Organization
- Group related tests using `describe` blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data
- Use factories for test data
- Keep test data close to tests
- Use meaningful test data

### 3. Assertions
- Test behavior, not implementation
- Use semantic queries (getByRole, getByLabelText)
- Avoid testing implementation details

### 4. Performance
- Keep tests fast and focused
- Use `beforeEach` for setup
- Clean up after tests

## 📚 Additional Resources

- [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) 