#!/usr/bin/env python3
"""Simple test script for API endpoints"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_root():
    print("\nTesting root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_docs():
    print("\nTesting docs endpoint...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")
    return response.status_code == 200

if __name__ == "__main__":
    print("🧪 Testing AI Compliance & Risk Copilot API\n")
    
    try:
        test_root()
        test_health()
        test_docs()
        
        print("\n✅ All tests passed!")
        print(f"\n📚 API Documentation: {BASE_URL}/docs")
        print(f"🏥 Health Check: {BASE_URL}/health")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Please make sure the server is running:")
        print("  docker-compose up -d")
        print("  or")
        print("  cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
