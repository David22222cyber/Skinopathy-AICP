"""
Test script for AICP API endpoints.
Run the API server first: python api_server.py
Then run this: python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*50)
    print("TEST: Health Check")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_index():
    """Test index endpoint."""
    print("\n" + "="*50)
    print("TEST: API Info")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_login(api_key):
    """Test login endpoint."""
    print("\n" + "="*50)
    print("TEST: Login")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"api_key": api_key}
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        return data.get("token")
    return None


def test_login_invalid():
    """Test login with invalid credentials."""
    print("\n" + "="*50)
    print("TEST: Login with Invalid Credentials")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"api_key": "invalid-key-123"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401


def test_query_without_token():
    """Test query endpoint without authentication."""
    print("\n" + "="*50)
    print("TEST: Query Without Token")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"question": "How many patients?"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401


def test_profile(token):
    """Test profile endpoint."""
    print("\n" + "="*50)
    print("TEST: Get User Profile")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_schema(token):
    """Test schema endpoint."""
    print("\n" + "="*50)
    print("TEST: Get Database Schema")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/api/schema",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    if response.status_code == 200:
        # Truncate schema for readability
        schema = data.get("schema", "")
        if len(schema) > 500:
            data["schema"] = schema[:500] + "... (truncated)"
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200


def test_query(token, question):
    """Test query endpoint."""
    print("\n" + "="*50)
    print(f"TEST: Execute Query")
    print("="*50)
    print(f"Question: {question}")
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question": question,
            "include_sql": True,
            "max_rows": 50
        }
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"Success: {data.get('success')}")
        print(f"SQL: {data.get('sql', 'N/A')}")
        print(f"Row Count: {data.get('row_count')}")
        print(f"Execution Time: {data.get('execution_time_ms')}ms")
        print(f"AI Summary: {data.get('analysis', {}).get('ai_summary', 'N/A')[:200]}...")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    
    return response.status_code == 200


def test_logout(token):
    """Test logout endpoint."""
    print("\n" + "="*50)
    print("TEST: Logout")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def main():
    print("="*50)
    print("AICP API Test Suite")
    print("="*50)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the API server is running!")
    print()
    
    # Get API key from user
    api_key = input("Enter your API key for testing: ").strip()
    if not api_key:
        print("ERROR: API key is required")
        return
    
    results = {}
    
    # Run tests
    try:
        results["Health Check"] = test_health()
        results["API Info"] = test_index()
        results["Login Invalid"] = test_login_invalid()
        
        # Login with valid credentials
        token = test_login(api_key)
        if token:
            results["Login Valid"] = True
            results["Query Without Token"] = test_query_without_token()
            results["Get Profile"] = test_profile(token)
            results["Get Schema"] = test_schema(token)
            
            # Test queries
            results["Query 1"] = test_query(token, "How many patients do I have?")
            time.sleep(1)  # Rate limit
            results["Query 2"] = test_query(token, "What are the most common diagnoses?")
            
            results["Logout"] = test_logout(token)
        else:
            results["Login Valid"] = False
            print("\nERROR: Could not login. Remaining tests skipped.")
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*50)


if __name__ == "__main__":
    main()
