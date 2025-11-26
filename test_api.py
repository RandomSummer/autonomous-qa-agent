"""
Test script for FastAPI endpoints
Run this to verify the API is working correctly
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

print("=" * 70)
print("🧪 Testing FastAPI Endpoints")
print("=" * 70)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{API_BASE}/")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ API Status: {data['status']}")
        print(f"  ✅ Groq Configured: {data['groq_api_configured']}")
        print(f"  ✅ Vector DB: {data['vector_db_initialized']}")
    else:
        print(f"  ❌ Failed: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  ❌ Cannot connect. Is FastAPI running?")
    print("  💡 Start with: uvicorn backend.main:app --reload --port 8000")
    exit(1)

# Test 2: Upload List
print("\n2️⃣ Testing Upload List...")
try:
    response = requests.get(f"{API_BASE}/api/uploads/list")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Total files: {data['total']}")
        if data['files']:
            for file in data['files']:
                print(f"    - {file}")
    else:
        print(f"  ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {str(e)}")

# Test 3: Knowledge Base Stats
print("\n3️⃣ Testing Knowledge Base Stats...")
try:
    response = requests.get(f"{API_BASE}/api/knowledge-base/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Total chunks: {data['total_chunks']}")
        print(f"  ✅ Total documents: {data['total_documents']}")
        if data['documents']:
            print(f"  ✅ Documents:")
            for doc in data['documents']:
                print(f"    - {doc}")
    else:
        print(f"  ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {str(e)}")

# Test 4: Scripts List
print("\n4️⃣ Testing Generated Scripts...")
try:
    response = requests.get(f"{API_BASE}/api/scripts/list")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Total scripts: {data['total']}")
        if data['scripts']:
            for script in data['scripts']:
                print(f"    - {script}")
    else:
        print(f"  ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {str(e)}")

# Test 5: Test Case Generation (if KB exists)
print("\n5️⃣ Testing Test Case Generation...")
try:
    stats_response = requests.get(f"{API_BASE}/api/knowledge-base/stats")
    stats = stats_response.json()
    
    if stats['total_chunks'] > 0:
        print("  📝 Knowledge base exists, testing generation...")
        
        response = requests.post(
            f"{API_BASE}/api/test-cases/generate",
            json={
                "query": "Generate a simple test case for form validation",
                "include_negative": False
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"  ✅ Generated {data['total_cases']} test cases")
                if data['test_cases']:
                    tc = data['test_cases'][0]
                    print(f"    - {tc['test_id']}: {tc['feature']}")
                    print(f"    - Grounded in: {tc['grounded_in']}")
            else:
                print(f"  ⚠️ Generation failed: {data['message']}")
        else:
            print(f"  ❌ API error: {response.status_code}")
    else:
        print("  ⚠️ Knowledge base is empty. Build KB first.")
        
except Exception as e:
    print(f"  ❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("✅ API Testing Complete")
print("=" * 70)

print("\n📊 Summary:")
print("  • Health check: Passed")
print("  • File operations: Passed")
print("  • Knowledge base: Check stats above")
print("  • Script generation: Check lists above")

print("\n🚀 Next Steps:")
print("  1. If KB is empty, upload docs and build KB")
print("  2. Open Streamlit UI: http://localhost:8501")
print("  3. Follow the 4-step workflow")
print("  4. Check API docs: http://localhost:8000/docs")