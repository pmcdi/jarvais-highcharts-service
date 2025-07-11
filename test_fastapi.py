#!/usr/bin/env python3
"""
Simple test script for the FastAPI Jarvais Highcharts Service
"""

import sys
import os
import requests
import time

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_docs_endpoint(base_url="http://localhost:5000"):
    """Test the docs endpoint"""
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs endpoint accessible")
            return True
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs failed: {e}")
        return False

def test_analyzers_endpoint(base_url="http://localhost:5000"):
    """Test the analyzers endpoint"""
    try:
        response = requests.get(f"{base_url}/analyzers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyzers endpoint working: {data['count']} analyzers")
            return True
        else:
            print(f"❌ Analyzers endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Analyzers endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing FastAPI Jarvais Highcharts Service...")
    print("=" * 50)
    
    base_url = os.environ.get('TEST_BASE_URL', 'http://localhost:5000')
    print(f"Testing against: {base_url}")
    print()
    
    # Wait a bit for the server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("API Documentation", test_docs_endpoint),
        ("Analyzers List", test_analyzers_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func(base_url):
            passed += 1
        else:
            print(f"   ❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI conversion successful!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the server logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 