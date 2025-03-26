import requests
import json

BACKEND_URL = "https://apartment-finder-backend.onrender.com/search"
OUTPUT_FILE = "data.json"

try:
    response = requests.get(BACKEND_URL)
    if response.status_code == 200:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(response.json(), f)
        print("✅ Data refreshed and saved to data.json")
    else:
        print(f"❌ Failed to fetch data: {response.status_code}")
except Exception as e:
    print(f"⚠️ Error occurred: {e}")
