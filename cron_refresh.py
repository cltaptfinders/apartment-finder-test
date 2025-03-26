import requests
import json
import os
import subprocess

# Pull fresh data from Apify Actor's latest successful run
APIFY_API_URL = "https://api.apify.com/v2/acts/epctex~apartments-scraper/runs/last/dataset/items?token=apify_api_GL1wNUgK91WADqxulii7YA2acoGeZF4k9kCz"
DATA_FILE = "data.json"

def refresh_data():
    response = requests.get(APIFY_API_URL)
    if response.status_code == 200:
        with open(DATA_FILE, "w") as f:
            json.dump(response.json(), f)
        print("✅ Data refreshed and saved to data.json")
        return True
    else:
        print(f"❌ Failed to fetch data. Status code: {response.status_code}")
        return False

def commit_and_push():
    subprocess.run(["git", "add", DATA_FILE])
    subprocess.run(["git", "commit", "-m", "Auto-update data.json from cron"])
    subprocess.run(["git", "push", "origin", "main"])
    print("✅ data.json committed and pushed to GitHub")

if __name__ == "__main__":
    if refresh_data():
        commit_and_push()
