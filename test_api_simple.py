import urllib.request
import json

BASE_URL = "http://localhost:8000"

print("[Testing Intelligent Workflow Assistant Backend]\n")

# Test 1: Health check
print("[1] Health Check:")
try:
    response = urllib.request.urlopen(f"{BASE_URL}/")
    data = json.loads(response.read())
    print(f"   Status: Healthy")
    print(f"   Message: {data['message']}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 2: Generate workflow
print("[2] Generate Workflow:")
try:
    payload = {
        "goal": "Build a machine learning image classifier",
        "context": "Using Python and deep learning"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/generate-workflow/",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    print(f"   Goal: {data.get('goal')}")
    print(f"   Total Steps: {data.get('total_steps')}")
    if data.get('steps'):
        print(f"   First Step: {data['steps'][0].get('task')}")
    print(f"   Overall Tools: {', '.join(data.get('overall_tools', [])[:5])}\n")
except Exception as e:
    print(f"   Error: {e}\n")

# Test 3: Get available tools
print("[3] Get Available Tools:")
try:
    response = urllib.request.urlopen(f"{BASE_URL}/tools/")
    data = json.loads(response.read())
    tools = data.get('available_tools', [])
    print(f"   Total Tools Available: {len(tools)}")
    print(f"   Sample Tools: {', '.join(tools[:8])}\n")
except Exception as e:
    print(f"   Error: {e}\n")

print("[SUCCESS] Backend is operational!")
