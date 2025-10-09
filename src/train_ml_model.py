import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
import joblib

API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

def get_historical_fixtures(days=30):
    fixtures = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"{BASE_URL}/fixtures/matches.json?key={API_KEY}&secret={API_SECRET}&date={date}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            fixtures.extend(data.get("data", {}).get("fixtures", []))
    return fixtures

def get_h2h(home_id, away_id):
    url = f"{BASE_URL}/teams/head2head.json?team1_id={home_id}&team2_id={away_id}&key={API_KEY}&secret={API_SECRET}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("data", {}).get("matches", [])
    return []

def extract_features_and_label(h2h_matches, actual_score):
    # Features: avg goals, num matches, home win rate
    if not h2h_matches:
        return [0, 0, 0], None
    goals = []
    home_wins = 0
    for m in h2h_matches:
        score = m.get("score")
        if score:
            score = score.replace(" ","")
            if ":" in score:
                parts = score.split(":")
            elif "-" in score:
                parts = score.split("-")
            else:
                continue
            try:
                g1, g2 = int(parts[0]), int(parts[1])
                goals.append(g1 + g2)
                if g1 > g2:
                    home_wins += 1
            except:
                continue
    avg_goals = sum(goals) / len(goals) if goals else 0
    num_matches = len(goals)
    home_win_rate = home_wins / num_matches if num_matches else 0

    # Label: 0=Home Win, 1=Draw, 2=Away Win, 3=Over 1.5, 4=Over 2.5
    label = None
    if actual_score:
        actual_score = actual_score.replace(" ","")
        if ":" in actual_score:
            parts = actual_score.split(":")
        elif "-" in actual_score:
            parts = actual_score.split("-")
        else:
            parts = []
        try:
            g1, g2 = int(parts[0]), int(parts[1])
            total_goals = g1 + g2
            if g1 > g2:
                label = 0
            elif g1 == g2:
                label = 1
            else:
                label = 2
            if total_goals > 2.5:
                label = 4
            elif total_goals > 1.5:
                label = 3
        except:
            pass
    return [avg_goals, num_matches, home_win_rate], label

def main():
    fixtures = get_historical_fixtures(days=30)
    X = []
    y = []
    for match in fixtures:
        home_id = match.get("home_id")
        away_id = match.get("away_id")
        actual_score = match.get("score")
        h2h_matches = get_h2h(home_id, away_id)
        features, label = extract_features_and_label(h2h_matches, actual_score)
        if label is not None:
            X.append(features)
            y.append(label)
    if not X or not y:
        print("Not enough data to train model.")
        return
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, "ml_model.pkl")
    print("Model trained and saved as ml_model.pkl")

if __name__ == "__main__":
    main()