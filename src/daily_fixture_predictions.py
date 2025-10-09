import requests
import numpy as np
from datetime import datetime

try:
    import joblib
    model = joblib.load("ml_model.pkl")
except Exception:
    model = None

API_KEY = "Xvt1DJzDokBfqQth"
API_SECRET = "rfu1GldGcY657Rl5nP60yGEW0fcq6GIx"
BASE_URL = "https://livescore-api.com/api-client"

def get_daily_fixtures():
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

def extract_features(h2h_matches):
    if not h2h_matches:
        return [0, 0, 0]
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
    return [avg_goals, num_matches, home_win_rate]

def rule_based_prediction(h2h_matches):
    if not h2h_matches:
        return "No head to head data"
    goals = []
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
                goals.append(int(parts[0]) + int(parts[1]))
            except:
                continue
    avg_goals = sum(goals) / len(goals) if goals else 0
    if avg_goals > 2.5:
        return "Over 2.5 goals"
    elif avg_goals > 1.5:
        return "Over 1.5 goals"
    else:
        return "No strong prediction"

def main():
    fixtures = get_daily_fixtures()
    print(f"Found {len(fixtures)} fixtures for today.")
    best_predictions = []
    for match in fixtures:
        home = match.get("home_name")
        away = match.get("away_name")
        home_id = match.get("home_id")
        away_id = match.get("away_id")
        match_time = match.get("date")
        print(f"\n{home} vs {away} at {match_time}")
        h2h_matches = get_h2h(home_id, away_id)
        features = extract_features(h2h_matches)
        if model:
            X = np.array(features).reshape(1, -1)
            proba = model.predict_proba(X)[0]
            pred_class = np.argmax(proba)
            confidence = np.max(proba)
            class_map = {0: "Home Win", 1: "Draw", 2: "Away Win", 3: "Over 1.5 goals", 4: "Over 2.5 goals"}
            prediction = class_map.get(pred_class, "Unknown")
            if confidence > 0.8:
                print(f"Prediction: {prediction} (Confidence: {confidence:.2f})")
                best_predictions.append((confidence, f"{home} vs {away} at {match_time} → {prediction} (Confidence: {confidence:.2f})"))
            else:
                print("No high-confidence prediction for this game.")
        else:
            prediction = rule_based_prediction(h2h_matches)
            print(f"Prediction: {prediction}")

    if model and best_predictions:
        print("\nBest predictions for today:")
        for _, pred in sorted(best_predictions, reverse=True):
            print(pred)

if __name__ == "__main__":
    main()