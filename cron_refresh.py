import requests
import json
import os
import subprocess

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN environment variable not set.")
    exit(1)

GITHUB_REPO = f"https://{GITHUB_TOKEN}@github.com/cltaptfinders/apartment-finder.git"
APIFY_API_URL = "https://api.apify.com/v2/acts/epctex~apartments-scraper/runs/last/dataset/items?token=apify_api_GL1wNUgK91WADqxulii7YA2acoGeZF4k9kCz"
DATA_FILE = "data.json"

# Set Git identity
subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])
subprocess.run(["git", "config", "--global", "user.email", "render@bot.com"])

# Initialize git if necessary and set remote
if not os.path.exists(".git"):
    subprocess.run(["git", "init"])
    subprocess.run(["git", "remote", "add", "origin", GITHUB_REPO])
else:
    subprocess.run(["git", "remote", "set-url", "origin", GITHUB_REPO])

# Pull fresh data
def refresh_data():
    response = requests.get(APIFY_API_URL)
    if response.status_code == 200:
        with open(DATA_FILE, "w") as f:
            json.dump(response.json(), f)
        print("✅ Data refreshed and saved to data.json")
        return True
    else:
        print(f"❌ Failed to fetch data: {response.status_code}")
        return False

if refresh_data():
    subprocess.run(["git", "add", DATA_FILE])
    subprocess.run(["git", "commit", "-m", "Auto-update data.json from cron", "--allow-empty"])
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "push", "-u", "origin", "main"])
    print("✅ data.json committed and pushed to GitHub")
else:
    print("⚠️ Data refresh failed. Nothing was pushed.")