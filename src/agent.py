import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

# Lazy-load model bundle if present
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "sports_model.pkl"))

app = FastAPI(title="GamePredict AI Agent", version="0.1.0")
_bundle = None

class PredictRequest(BaseModel):
    home_team: str
    away_team: str

@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "GamePredict AI Agent is running", "status": "ok"}

@app.on_event("startup")
def load_model_on_startup():
    global _bundle
    try:
        if os.path.exists(MODEL_PATH):
            _bundle = joblib.load(MODEL_PATH)
    except Exception:
        _bundle = None

@app.post("/predict")
def predict(req: PredictRequest):
    global _bundle
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet. Train the model and place sports_model.pkl at project root or set MODEL_PATH.")

    model = _bundle.get("model")
    team_to_id = _bundle.get("team_to_id", {})

    if req.home_team not in team_to_id or req.away_team not in team_to_id:
        raise HTTPException(status_code=400, detail="Unknown team name(s). Ensure the teams exist in the training data.")

    home_id = team_to_id[req.home_team]
    away_id = team_to_id[req.away_team]

    # Minimal feature vector for MVP (goal_diff placeholder = 0)
    X = [[home_id, away_id, 0]]
    try:
        probs = model.predict_proba(X)[0]
        pred = int(model.predict(X)[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    outcomes = {0: "Draw", 1: "Home Win", 2: "Away Win"}
    return {
        "home_team": req.home_team,
        "away_team": req.away_team,
        "predicted_outcome": outcomes.get(pred, str(pred)),
        "probabilities": {
            "draw": float(probs[0]) if len(probs) > 0 else None,
            "home_win": float(probs[1]) if len(probs) > 1 else None,
            "away_win": float(probs[2]) if len(probs) > 2 else None,
        },
    }
