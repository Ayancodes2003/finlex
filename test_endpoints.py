import requests
import json

# Test policy analysis endpoint
policy_id = "092265aa-baa6-4f64-a762-2caf845ed39c"
policy_url = f"http://localhost:18002/analyze/{policy_id}"

print("Testing policy analysis endpoint...")
try:
    response = requests.post(policy_url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test transaction analysis endpoint
transaction_id = "bb717742-7cbd-426b-8ba7-f4410ade3c5f"
transaction_url = f"http://localhost:18001/analyze/{transaction_id}"

print("\nTesting transaction analysis endpoint...")
try:
    response = requests.post(transaction_url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")