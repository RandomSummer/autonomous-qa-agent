"""
Test script to verify the API connection
"""
import requests

API_BASE = "http://127.0.0.1:8000"

print("Testing API connection...")
print(f"API Base URL: {API_BASE}")
print()

try:
    response = requests.get(f"{API_BASE}/api/health", timeout=5)
    print(f"[OK] Connection successful!")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError as e:
    print(f"[ERROR] Connection failed: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")
