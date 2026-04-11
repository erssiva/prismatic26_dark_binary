import requests
import json

# Test the API
BASE_URL = "http://localhost:8000"

print("🔹 Testing Intelligent Workflow Assistant Backend\n")

# Test 1: Health check
print("1️⃣  Health Check:")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 2: Generate workflow
print("2️⃣  Generate Workflow:")
try:
    payload = {
        "goal": "Build a machine learning image classifier for detecting cat vs dog photos",
        "context": "Using Python and deep learning"
    }
    response = requests.post(f"{BASE_URL}/generate-workflow/", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Goal: {data.get('goal')}")
    print(f"   Total Steps: {data.get('total_steps')}")
    print(f"   Overall Tools: {', '.join(data.get('overall_tools', [])[:5])}...")
    print("\n   Steps:")
    for step in data.get('steps', [])[:3]:
        print(f"   [{step['step_number']}] {step['task']}")
        print(f"       Tools: {', '.join(step['tools'])}")
    print()
except Exception as e:
    print(f"   Error: {e}\n")

# Test 3: Get available tools
print("3️⃣  Get Available Tools:")
try:
    response = requests.get(f"{BASE_URL}/tools/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total Tools Available: {len(data.get('available_tools', []))}")
    print(f"   Sample Tools: {', '.join(data.get('available_tools', [])[:10])}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 4: Get examples
print("4️⃣  Get Example Workflows:")
try:
    response = requests.get(f"{BASE_URL}/examples/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    for example in data.get('examples', []):
        print(f"   • {example['goal']} ({example['category']})")
    print()
except Exception as e:
    print(f"   Error: {e}\n")

print("✅ Testing Complete!")
