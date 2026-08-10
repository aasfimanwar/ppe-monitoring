import requests

# Pick a real violation id you saw in /api/violations earlier
violation_id = 12

response = requests.patch(
    f"http://127.0.0.1:5000/api/violations/{violation_id}/resolve",
    json={"resolved_by": "test-safety-officer"},
)
print("Status code:", response.status_code)
print("Response:", response.json())