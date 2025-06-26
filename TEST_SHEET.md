# News Analyzer Application - Test Sheet

## 🧪 Test Overview
This document contains comprehensive test cases for the News Analyzer application covering both manual and automated testing scenarios.

---

## 📋 Manual Test Cases

### 🔐 Authentication Tests

#### Test Case 1: User Login
- **Objective**: Verify user can log in successfully
- **Steps**:
  1. Navigate to `/login`
  2. Click "Login" button
  3. Verify redirect to dashboard
- **Expected Result**: User should be logged in and redirected to dashboard
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 2: Authentication Persistence
- **Objective**: Verify login persists across page refreshes
- **Steps**:
  1. Login to application
  2. Refresh the page
  3. Navigate to different pages
- **Expected Result**: User should remain logged in
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 3: Protected Route Access
- **Objective**: Verify unauthenticated users cannot access protected routes
- **Steps**:
  1. Clear browser storage
  2. Try to access `/dashboard`, `/sources`, `/analysis`
- **Expected Result**: Should redirect to login page
- **Status**: ⬜ Pass ⬜ Fail

---

### 🏠 Dashboard Tests

#### Test Case 4: Dashboard Loading
- **Objective**: Verify dashboard loads correctly
- **Steps**:
  1. Login to application
  2. Navigate to dashboard
- **Expected Result**: Dashboard should display with Quick Actions and Recent Business Interests
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 5: Quick Actions Navigation
- **Objective**: Verify quick action buttons work
- **Steps**:
  1. Click "Set Business Interest"
  2. Click "Manage Sources"
  3. Click "Run Analysis"
- **Expected Result**: Should navigate to respective pages
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 6: Recent Business Interests Display
- **Objective**: Verify recent business interests are shown
- **Steps**:
  1. Create a business interest
  2. Return to dashboard
- **Expected Result**: Should see the created business interest in the list
- **Status**: ⬜ Pass ⬜ Fail

---

### 📝 Business Interest Tests

#### Test Case 7: Create Business Interest
- **Objective**: Verify business interest creation
- **Steps**:
  1. Navigate to Business Interest page
  2. Enter text in the textarea
  3. Click "Save & Continue"
- **Expected Result**: Should save and redirect to Sources page
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 8: Business Interest Validation
- **Objective**: Verify empty business interest is rejected
- **Steps**:
  1. Navigate to Business Interest page
  2. Leave textarea empty
  3. Click "Save & Continue"
- **Expected Result**: Should show error message
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 9: Character Counter
- **Objective**: Verify character counter works
- **Steps**:
  1. Navigate to Business Interest page
  2. Type in the textarea
- **Expected Result**: Character count should update
- **Status**: ⬜ Pass ⬜ Fail

---

### 🌐 Sources Management Tests

#### Test Case 10: Add Source
- **Objective**: Verify adding a new source
- **Steps**:
  1. Navigate to Sources page
  2. Enter a valid URL (e.g., "reuters.com")
  3. Click "Add Source"
- **Expected Result**: Source should be added to the list
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 11: Add Invalid Source
- **Objective**: Verify invalid URLs are rejected
- **Steps**:
  1. Navigate to Sources page
  2. Enter invalid URL (e.g., "not-a-url")
  3. Click "Add Source"
- **Expected Result**: Should show error message
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 12: Add Popular Source
- **Objective**: Verify adding from popular sources
- **Steps**:
  1. Navigate to Sources page
  2. Click on a popular source button
- **Expected Result**: Source should be added to the list
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 13: Remove Source
- **Objective**: Verify removing a source
- **Steps**:
  1. Add a source
  2. Click the trash icon next to the source
  3. Confirm deletion
- **Expected Result**: Source should be removed from the list
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 14: Duplicate Source Prevention
- **Objective**: Verify duplicate sources are not added
- **Steps**:
  1. Add a source
  2. Try to add the same source again
- **Expected Result**: Should show "already exists" message
- **Status**: ⬜ Pass ⬜ Fail

---

### 🔍 Analysis Tests

#### Test Case 15: Analysis Page Loading
- **Objective**: Verify analysis page loads with data
- **Steps**:
  1. Create business interest and add sources
  2. Navigate to Analysis page
- **Expected Result**: Should show business interests and sources for selection
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 16: Select Business Interest
- **Objective**: Verify business interest selection
- **Steps**:
  1. Navigate to Analysis page
  2. Click on a business interest
- **Expected Result**: Should highlight the selected interest
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 17: Select Sources
- **Objective**: Verify source selection
- **Steps**:
  1. Navigate to Analysis page
  2. Click on sources to select/deselect
- **Expected Result**: Should show selected count and highlight selected sources
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 18: Select All Sources
- **Objective**: Verify select all functionality
- **Steps**:
  1. Navigate to Analysis page
  2. Click "Select All"
- **Expected Result**: All sources should be selected
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 19: Start Analysis
- **Objective**: Verify analysis execution
- **Steps**:
  1. Select business interest and sources
  2. Click "Start Analysis"
- **Expected Result**: Should show loading state and redirect to results
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 20: Analysis Validation
- **Objective**: Verify analysis requires both interest and sources
- **Steps**:
  1. Navigate to Analysis page
  2. Try to start analysis without selecting interest or sources
- **Expected Result**: Should show error messages
- **Status**: ⬜ Pass ⬜ Fail

---

### 📊 Results Tests

#### Test Case 21: Results Page Loading
- **Objective**: Verify results page displays analysis data
- **Steps**:
  1. Complete an analysis
  2. View results page
- **Expected Result**: Should show articles, statistics, and summary
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 22: Article Display
- **Objective**: Verify articles are displayed correctly
- **Steps**:
  1. View results page
  2. Check article titles, content, and metadata
- **Expected Result**: Articles should be properly formatted with all information
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 23: External Links
- **Objective**: Verify external article links work
- **Steps**:
  1. View results page
  2. Click external link icon on an article
- **Expected Result**: Should open article in new tab
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 24: Results Persistence
- **Objective**: Verify results remain accessible
- **Steps**:
  1. Complete analysis
  2. Navigate away and back
  3. Check Latest Results section on Analysis page
- **Expected Result**: Results should still be accessible
- **Status**: ⬜ Pass ⬜ Fail

---

### 🎨 UI/UX Tests

#### Test Case 25: Responsive Design
- **Objective**: Verify app works on different screen sizes
- **Steps**:
  1. Test on desktop (1920x1080)
  2. Test on tablet (768x1024)
  3. Test on mobile (375x667)
- **Expected Result**: Layout should adapt appropriately
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 26: Loading States
- **Objective**: Verify loading indicators work
- **Steps**:
  1. Perform actions that trigger loading (add source, run analysis)
- **Expected Result**: Should show appropriate loading indicators
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 27: Error Handling
- **Objective**: Verify error messages are user-friendly
- **Steps**:
  1. Trigger various errors (network issues, invalid inputs)
- **Expected Result**: Should show clear, helpful error messages
- **Status**: ⬜ Pass ⬜ Fail

#### Test Case 28: Navigation
- **Objective**: Verify navigation works correctly
- **Steps**:
  1. Test all navigation links and buttons
  2. Test browser back/forward buttons
- **Expected Result**: Navigation should work smoothly
- **Status**: ⬜ Pass ⬜ Fail

---

## 🔧 API Tests

### Backend Health Check
```bash
curl -X GET http://localhost:8000/api/health
```
**Expected**: `{"status": "healthy"}`

### Authentication Flow
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login

# Get user info (with token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Business Interest API
```bash
# Create business interest
curl -X POST http://localhost:8000/api/analysis/business-interest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"interest_text": "Test interest"}'

# Get business interests
curl -X GET http://localhost:8000/api/analysis/business-interest \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Sources API
```bash
# Add source
curl -X POST http://localhost:8000/api/sources/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_url": "https://reuters.com"}'

# Get sources
curl -X GET http://localhost:8000/api/sources/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get popular sources
curl -X GET http://localhost:8000/api/sources/popular \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Analysis API
```bash
# Run analysis
curl -X POST http://localhost:8000/api/news/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_interest": "Test interest",
    "sources": ["https://reuters.com"]
  }'

# Get sessions
curl -X GET http://localhost:8000/api/news/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🚀 Performance Tests

### Test Case 29: Page Load Performance
- **Objective**: Verify pages load within acceptable time
- **Steps**:
  1. Measure page load times for all pages
- **Expected Result**: Pages should load within 3 seconds
- **Status**: ⬜ Pass ⬜ Fail

### Test Case 30: Analysis Performance
- **Objective**: Verify analysis completes in reasonable time
- **Steps**:
  1. Run analysis with multiple sources
- **Expected Result**: Analysis should complete within 5 minutes
- **Status**: ⬜ Pass ⬜ Fail

---

## 🐛 Bug Report Template

### Bug Report
- **Title**: [Brief description]
- **Severity**: [Critical/High/Medium/Low]
- **Steps to Reproduce**:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Expected Result**: [What should happen]
- **Actual Result**: [What actually happened]
- **Environment**: [Browser, OS, etc.]
- **Screenshots**: [If applicable]

---

## 📝 Test Execution Log

| Test Case | Date | Tester | Status | Notes |
|-----------|------|--------|--------|-------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| ... | | | | |

---

## ✅ Test Completion Checklist

- [ ] All manual test cases executed
- [ ] All API endpoints tested
- [ ] Performance benchmarks met
- [ ] Cross-browser compatibility verified
- [ ] Mobile responsiveness confirmed
- [ ] Error scenarios covered
- [ ] Security tests completed
- [ ] Documentation updated

---

## 🎯 Test Summary

**Total Test Cases**: 30
**Passed**: ___
**Failed**: ___
**Pass Rate**: ___%

**Critical Issues Found**: ___
**High Priority Issues**: ___
**Medium Priority Issues**: ___
**Low Priority Issues**: ___ 