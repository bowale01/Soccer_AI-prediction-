import requests
from datetime import datetime

API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

def get_fixtures(date):
    url = f"{BASE_URL}/fixtures/matches.json?key={API_KEY}&secret={API_SECRET}&date={date}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("fixtures", [])

def get_h2h(home_id, away_id):
    url = f"{BASE_URL}/teams/head2head.json?team1_id={home_id}&team2_id={away_id}&key={API_KEY}&secret={API_SECRET}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("matches", [])

def get_recent_form(team_id):
    url = f"{BASE_URL}/teams/matches.json?team_id={team_id}&key={API_KEY}&secret={API_SECRET}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("matches", [])

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    fixtures = get_fixtures(today)
    print(f"Found {len(fixtures)} fixtures today.")
    for match in fixtures:
        home = match.get("home_name")
        away = match.get("away_name")
        home_id = match.get("home_id")
        away_id = match.get("away_id")
        match_time = match.get("date")
        print(f"\n{home} vs {away} at {match_time}")
        # H2H
        h2h_matches = get_h2h(home_id, away_id)
        print(f"H2H matches found: {len(h2h_matches)}")
        # Recent form
        home_form = get_recent_form(home_id)
        away_form = get_recent_form(away_id)
        print(f"Recent form for {home}: {len(home_form)} matches")
        print(f"Recent form for {away}: {len(away_form)} matches")

if __name__ == "__main__":
    main()
