import requests
import json
import os
import subprocess

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN environment variable not set.")
    exit(1)

REPO_URL = f"https://{GITHUB_TOKEN}@github.com/cltaptfinders/apartment-finder.git"
APIFY_API_URL = "https://api.apify.com/v2/acts/epctex~apartments-scraper/runs/last/dataset/items?token=apify_api_GL1wNUgK91WADqxulii7YA2acoGeZF4k9kCz"
DATA_FILE = "data.json"

# Set Git identity
subprocess.run(["git", "config", "--local", "user.name", "Render Bot"])
subprocess.run(["git", "config", "--local", "user.email", "render@bot.com"])

# Ensure Git repo is initialized
if not os.path.isdir(".git"):
    subprocess.run(["git", "init"])
    subprocess.run(["git", "checkout", "-b", "main"])

# Check if origin exists
remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
if "origin" not in remote_check.stdout:
    subprocess.run(["git", "remote", "add", "origin", REPO_URL])
else:
    subprocess.run(["git", "remote", "set-url", "origin", REPO_URL])

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
    subprocess.run(["git", "push", "-u", "origin", "main"])
    print("✅ data.json committed and pushed to GitHub")
else:
    print("⚠️ Data refresh failed. Nothing was pushed.")