import requests
import json

BASE_URL = "http://localhost:5001"

def test_index():
    url = f"{BASE_URL}/"
    response = requests.get(url)
    print(f"GET / : {response.status_code} - {response.text}")

def test_generate():
    url = f"{BASE_URL}/generate/"
    payload = {
        "username": "test_user",
        "message": "Hello, how are you?",
        "usertype": "adult",
        "location": "SampleLocation",
        "region_id": 1
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"POST /generate/ : {response.status_code} - {response.text}")

def test_retrieve_regions():
    url = f"{BASE_URL}/retrieve_regions"
    response = requests.get(url)
    print(f"GET /retrieve_regions : {response.status_code} - {response.text}")

def test_storage_stats():
    url = f"{BASE_URL}/storage_stats"
    response = requests.get(url)
    print(f"GET /storage_stats : {response.status_code} - {response.text}")

if __name__ == "__main__":
    
    test_index()
    test_generate()
    test_retrieve_regions()
    test_storage_stats()
