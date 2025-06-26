#!/usr/bin/env python3
"""
Simple test script for News Analyzer API
Run with: python test_app.py
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_RESULTS = []

def log_test(test_name, passed, details=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   Details: {details}")
    TEST_RESULTS.append({"test": test_name, "passed": passed, "details": details})

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            log_test("Health Check", data.get("status") == "healthy")
        else:
            log_test("Health Check", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Health Check", False, f"Error: {str(e)}")

def test_login():
    """Test login endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login")
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "token_type" in data:
                log_test("Login", True)
                return data["access_token"]
            else:
                log_test("Login", False, "Missing token in response")
        else:
            log_test("Login", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Login", False, f"Error: {str(e)}")
    return None

def test_get_user_info(token):
    """Test getting user info"""
    if not token:
        log_test("Get User Info", False, "No token available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log_test("Get User Info", "client_id" in data)
        else:
            error_detail = f"Status code: {response.status_code}"
            try:
                error_detail += f", Response: {response.json()}"
            except:
                error_detail += f", Response: {response.text}"
            log_test("Get User Info", False, error_detail)
    except Exception as e:
        log_test("Get User Info", False, f"Error: {str(e)}")

def test_create_business_interest(token):
    """Test creating business interest"""
    if not token:
        log_test("Create Business Interest", False, "No token available")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"interest_text": "Test business interest for API testing"}
        response = requests.post(
            f"{BASE_URL}/analysis/business-interest",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            log_test("Create Business Interest", "id" in result)
        else:
            log_test("Create Business Interest", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Create Business Interest", False, f"Error: {str(e)}")

def test_get_business_interests(token):
    """Test getting business interests"""
    if not token:
        log_test("Get Business Interests", False, "No token available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/analysis/business-interest", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log_test("Get Business Interests", isinstance(data, list))
        else:
            log_test("Get Business Interests", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Get Business Interests", False, f"Error: {str(e)}")

def test_add_source(token):
    """Test adding a source"""
    if not token:
        log_test("Add Source", False, "No token available")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"source_url": "https://reuters.com"}
        response = requests.post(
            f"{BASE_URL}/sources/",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            log_test("Add Source", "source_id" in result)
        elif response.status_code == 409:
            # 409 Conflict means source already exists, which is expected behavior
            log_test("Add Source", True, "Source already exists (409 Conflict - expected)")
        else:
            log_test("Add Source", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Add Source", False, f"Error: {str(e)}")

def test_get_sources(token):
    """Test getting sources"""
    if not token:
        log_test("Get Sources", False, "No token available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/sources/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log_test("Get Sources", "sources" in data and "total_count" in data)
        else:
            log_test("Get Sources", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Get Sources", False, f"Error: {str(e)}")

def test_get_popular_sources(token):
    """Test getting popular sources"""
    if not token:
        log_test("Get Popular Sources", False, "No token available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/sources/popular", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log_test("Get Popular Sources", isinstance(data, dict) and len(data) > 0)
        else:
            log_test("Get Popular Sources", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Get Popular Sources", False, f"Error: {str(e)}")

def test_unauthorized_access():
    """Test unauthorized access to protected endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code in [401, 403]:
            # Both 401 (Unauthorized) and 403 (Forbidden) are valid for unauthorized access
            log_test("Unauthorized Access", True, f"Got {response.status_code} (expected)")
        else:
            log_test("Unauthorized Access", False, f"Expected 401 or 403, got {response.status_code}")
    except Exception as e:
        log_test("Unauthorized Access", False, f"Error: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("🧪 Running News Analyzer API Tests")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test unauthorized access
    test_unauthorized_access()
    
    # Test login and get token
    token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_get_user_info(token)
        test_create_business_interest(token)
        test_get_business_interests(token)
        test_add_source(token)
        test_get_sources(token)
        test_get_popular_sources(token)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for result in TEST_RESULTS if result["passed"])
    total = len(TEST_RESULTS)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {(passed/total)*100:.1f}%")
    
    # Show failed tests
    failed_tests = [result for result in TEST_RESULTS if not result["passed"]]
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test['test']}: {test['details']}")

if __name__ == "__main__":
    run_all_tests() 