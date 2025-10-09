import requests
import pandas as pd
from datetime import datetime

API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

def get_today_fixtures():
    fixtures = []
    for i in range(7):
        date_str = (datetime.now() + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"{BASE_URL}/fixtures/matches.json?key={API_KEY}&secret={API_SECRET}&date={date_str}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        fixtures.extend(data.get("data", {}).get("fixtures", []))
    return fixtures

def get_h2h(home_id, away_id):
    url = f"{BASE_URL}/teams/head2head.json?team1_id={home_id}&team2_id={away_id}&key={API_KEY}&secret={API_SECRET}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("matches", [])

def collect_historical_data():
    fixtures = get_today_fixtures()
    all_rows = []
    for match in fixtures:
        home = match.get("home_name")
        away = match.get("away_name")
        home_id = match.get("home_id")
        away_id = match.get("away_id")
        match_time = match.get("date")
        h2h_matches = get_h2h(home_id, away_id)
        for h2h in h2h_matches:
            score = h2h.get("score")
            if score:
                score = score.replace(" ","")
                if ":" in score:
                    parts = score.split(":")
                elif "-" in score:
                    parts = score.split("-")
                else:
                    continue
                try:
                    home_goals = int(parts[0])
                    away_goals = int(parts[1])
                except:
                    continue
            else:
                home_goals = None
                away_goals = None
            row = {
                "fixture_home": home,
                "fixture_away": away,
                "fixture_time": match_time,
                "h2h_date": h2h.get("date"),
                "h2h_home": h2h.get("home_name"),
                "h2h_away": h2h.get("away_name"),
                "home_goals": home_goals,
                "away_goals": away_goals,
                "competition": h2h.get("competition_name"),
                "venue": h2h.get("venue"),
                "result": "Home Win" if home_goals is not None and home_goals > away_goals else ("Away Win" if home_goals is not None and home_goals < away_goals else "Draw")
            }
            all_rows.append(row)
    df = pd.DataFrame(all_rows)
    # Append to CSV if it exists, else create new
    csv_path = "historical_fixture_h2h_data.csv"
    try:
        existing = pd.read_csv(csv_path)
        if not existing.empty:
            df = pd.concat([existing, df], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass
    df.to_csv(csv_path, index=False)
    print(f"Appended {len(all_rows)} new rows to historical_fixture_h2h_data.csv (total: {len(df)})")

if __name__ == "__main__":
    collect_historical_data()
