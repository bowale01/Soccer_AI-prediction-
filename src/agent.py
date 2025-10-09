import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from predictor import GamePredictor
from data_collector import LiveScoreDataCollector

# Initialize predictor and data collector
predictor = GamePredictor()
data_collector = LiveScoreDataCollector()

app = FastAPI(title="GamePredict AI Agent", version="0.2.0")

class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    home_id: int = None
    away_id: int = None

class TrainRequest(BaseModel):
    days: int = 30

@app.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "GamePredict AI Agent v2.0 is running", 
        "status": "ok",
        "model_loaded": predictor.model is not None
    }

@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_status": "loaded" if predictor.model else "not_loaded",
        "api_status": "connected"
    }

@app.post("/predict")
def predict(req: PredictRequest):
    """Predict match outcome using team names or IDs"""
    try:
        # If team IDs not provided, try to find them from recent fixtures
        home_id = req.home_id
        away_id = req.away_id
        
        if not home_id or not away_id:
            # Try to find team IDs from today's fixtures
            fixtures = data_collector.get_today_fixtures()
            for fixture in fixtures:
                if (fixture.get("home_name", "").lower() == req.home_team.lower() and 
                    fixture.get("away_name", "").lower() == req.away_team.lower()):
                    home_id = fixture.get("home_id")
                    away_id = fixture.get("away_id")
                    break
            
            if not home_id or not away_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not find team IDs. Please provide home_id and away_id, or ensure teams are playing today."
                )
        
        # Generate prediction
        prediction = predictor.predict_match(req.home_team, req.away_team, home_id, away_id)
        
        return {
            "home_team": req.home_team,
            "away_team": req.away_team,
            "rule_based_prediction": prediction["rule_based_prediction"],
            "ml_prediction": prediction["ml_prediction"],
            "confidence": prediction["confidence"],
            "is_high_confidence": prediction["is_high_confidence"],
            "h2h_matches_analyzed": prediction["h2h_matches_count"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/daily-predictions")
def get_daily_predictions(max_predictions: int = 20, min_confidence: float = 0.8) -> Dict:
    """Get today's best predictions"""
    try:
        predictions = predictor.get_daily_predictions(min_confidence, max_predictions)
        
        return {
            "date": data_collector.get_today_fixtures()[0].get("date", "today") if data_collector.get_today_fixtures() else "today",
            "total_predictions": len(predictions),
            "min_confidence": min_confidence,
            "predictions": predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily predictions error: {str(e)}")

@app.get("/fixtures")
def get_today_fixtures() -> Dict:
    """Get today's fixtures"""
    try:
        fixtures = data_collector.get_today_fixtures()
        
        return {
            "date": "today",
            "total_fixtures": len(fixtures),
            "fixtures": [
                {
                    "home_team": f.get("home_name"),
                    "away_team": f.get("away_name"),
                    "home_id": f.get("home_id"),
                    "away_id": f.get("away_id"),
                    "time": f.get("date"),
                    "competition": f.get("competition_name")
                }
                for f in fixtures
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fixtures error: {str(e)}")

@app.post("/train")
def train_model(req: TrainRequest) -> Dict:
    """Train the ML model with historical data"""
    try:
        success = predictor.train_model(days=req.days)
        
        if success:
            return {
                "status": "success",
                "message": f"Model trained successfully with {req.days} days of data",
                "model_path": predictor.model_path
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to train model - insufficient data",
                "model_path": predictor.model_path
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.get("/model-status")
def model_status() -> Dict:
    """Get model status information"""
    return {
        "model_loaded": predictor.model is not None,
        "model_path": predictor.model_path,
        "model_exists": os.path.exists(predictor.model_path) if predictor.model_path else False
    }
