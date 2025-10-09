import requests
import random
from datetime import datetime

API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

def get_today_fixtures():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures/matches.json?key={API_KEY}&secret={API_SECRET}&date={today}"
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

def analyze_match(h2h_matches):
    # Rule-based: average goals, win rates, etc.
    if not h2h_matches:
        return random.choice(["Home Win", "Away Win", "Draw"])
    goals = []
    for m in h2h_matches:
        score = m.get("score")
        if score:
            # Handle '1:2' or '1 - 2' formats
            score = score.replace(" ","")
            if ":" in score:
                parts = score.split(":")
            elif "-" in score:
                parts = score.split("-")
            else:
                continue
            try:
                goals.append(int(parts[0]) + int(parts[1]))
            except:
                continue
    avg_goals = sum(goals) / len(goals) if goals else 0
    if avg_goals > 2.5:
        return "Over 2.5 goals"
    elif avg_goals > 1.5:
        return "Over 1.5 goals"
    else:
        return random.choice(["Home Win", "Away Win", "Draw"])

def main():
    fixtures = get_today_fixtures()
    print(f"Found {len(fixtures)} fixtures today.")
    for match in fixtures:
        home = match.get("home_name")
        away = match.get("away_name")
        home_id = match.get("home_id")
        away_id = match.get("away_id")
        match_time = match.get("date")
        print(f"\n{home} vs {away} at {match_time}")
        h2h_matches = get_h2h(home_id, away_id)
        prediction = analyze_match(h2h_matches)
        print(f"Prediction: {prediction}")

if __name__ == "__main__":
    main()
