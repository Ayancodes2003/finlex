import requests
import json
import uuid
from datetime import datetime

# Create a test policy with a unique ID
policy_data = {
    "id": str(uuid.uuid4()),  # Generate a unique ID
    "title": "Test Policy for Verification",
    "content": "This is a test policy created to verify that the policy viewing functionality works correctly. It contains important information about compliance requirements and demonstrates the view functionality.",
    "jurisdiction": "US",
    "category": "Testing",
    "created_at": datetime.utcnow().isoformat() + "Z",
    "embeddings": "test-embeddings"
}

response = requests.post(
    "http://localhost:18002/policies",
    headers={"Content-Type": "application/json"},
    data=json.dumps(policy_data)
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# Verify the policy was created
response = requests.get("http://localhost:18002/policies")
print(f"Get Policies Status Code: {response.status_code}")
# Print just the titles to keep output manageable
policies = response.json()
print(f"Number of policies: {len(policies)}")
print("Policy titles:")
for policy in policies:
    print(f"  - {policy['title']}")