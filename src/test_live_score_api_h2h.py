import requests

# Provided endpoint, key, and secret
match_id = 172252
API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

stats_url = f"{BASE_URL}/matches/stats.json?match_id={match_id}&key={API_KEY}&secret={API_SECRET}"
print(f"Fetching match stats for match_id={match_id}")
resp = requests.get(stats_url)
resp.raise_for_status()
data = resp.json()

print("Raw match stats response:")
print(data)
