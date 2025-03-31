#!/bin/bash

echo "⏳ Fetching fresh data from backend..."
curl -X GET https://apartment-finder-backend.onrender.com/search -o data.json

echo "📂 Staging updated data.json..."
git add data.json

echo "📝 Committing update..."
git commit -m "🔄 Auto-refresh: Updated data.json with latest apartment data"

echo "🚀 Pushing to test GitHub repo..."
git push https://github.com/cltaptfinders/apartment-finder-test.git main