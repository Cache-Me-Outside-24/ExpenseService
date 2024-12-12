import requests
import json

# API endpoint URL
url = "http://localhost:8000/expenses/create_expense_and_group"

# Sample request payload
payload = {
    "total": 150.00,
    "description": "Dinner at Restaurant",
    "group_id": 18,  # Assuming an existing group ID
    "owed_to": "defg",   # Assuming the user ID who is owed the money
    "payments": [
        {
            "payer_id": "defg",
            "amount_owed": 50.00,
            "paid": True
        },
        {
            "payer_id": "abcd",
            "amount_owed": 100.00,
            "paid": False
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Send POST request
response = requests.post(url, json=payload, headers=headers)

# Check response
print("Status Code:", response.status_code)
print("Response Headers:", response.headers)
print("Response Body:", response.json())
