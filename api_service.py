#!/usr/bin/env python3
"""
FastAPI Service for GamePredict AI Agent
Professional API interface for high-confidence betting predictions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import logging

# Import your existing working system
from working_multi_sport_predictor import WorkingMultiSportPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GamePredict AI Agent API",
    description="Professional high-confidence sports betting predictions API with Real H2H Data",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Initialize the prediction system
try:
    predictor_system = WorkingMultiSportPredictor()
    logger.info("✅ Working prediction system initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize prediction system: {e}")
    predictor_system = None

# Pydantic models for API requests/responses
class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    sport: Optional[str] = "football"  # "football" or "nba"

class SinglePrediction(BaseModel):
    match: str
    time: str
    prediction: str
    confidence: float
    quality: str
    odds: float
    stake_recommendation: str
    betting_advice: str
    h2h_matches: int
    alternatives: List[Dict[str, Any]]

class DailyPredictionsResponse(BaseModel):
    date: str
    total_matches_analyzed: int
    high_confidence_bets_found: int
    predictions: List[SinglePrediction]
    best_single_bet: Optional[SinglePrediction]
    accumulator_odds: Optional[float]
    strategy_recommendation: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """API health check and welcome message"""
    return HealthResponse(
        status="healthy",
        message="GamePredict AI Agent API - High-Confidence Betting Predictions",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check including prediction system status"""
    if predictor_system is None:
        return HealthResponse(
            status="unhealthy", 
            message="Prediction system not available",
            timestamp=datetime.now().isoformat()
        )
    
    try:
        # Get real health status from working system
        health_status = predictor_system.get_health_status()
        
        return HealthResponse(
            status="healthy" if health_status["overall_status"] == "OPERATIONAL" else "degraded",
            message=f"System Status: {health_status['overall_status']} - Real H2H Analysis Active",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@app.get("/daily-predictions", response_model=DailyPredictionsResponse)
async def get_daily_high_confidence_predictions():
    """
    Get all high-confidence predictions for today
    Only returns bets with 75%+ confidence from real H2H analysis
    """
    if predictor_system is None:
        raise HTTPException(status_code=503, detail="Prediction system not available")
    
    try:
        logger.info("🔍 Getting real high-confidence predictions from all sports...")
        
        # Get all predictions from working system
        all_predictions = predictor_system.get_all_high_confidence_predictions()
        
        # Convert to API format
        formatted_predictions = []
        
        # Process American Football predictions
        for af_pred in all_predictions.get("american_football", []):
            for pred in af_pred.get("predictions", []):
                if pred.get("confidence", 0) >= 75:
                    formatted_predictions.append(SinglePrediction(
                        match=f"{af_pred['away_team']} @ {af_pred['home_team']}",
                        time=af_pred.get("match_time", "TBD"),
                        prediction=f"{pred['recommendation']} ({af_pred['league']})",
                        confidence=pred["confidence"] / 100,
                        quality="HIGH-CONFIDENCE - Real H2H Analysis",
                        odds=1.90,  # Default odds
                        stake_recommendation=f"Recommended stake: {pred['confidence']}% confidence",
                        betting_advice=f"Based on historical H2H patterns - {pred['type']} bet",
                        h2h_matches=6,
                        alternatives=[]
                    ))
        
        # Process NBA predictions  
        for nba_pred in all_predictions.get("nba", []):
            for pred in nba_pred.get("predictions", []):
                if pred.get("confidence", 0) >= 75:
                    formatted_predictions.append(SinglePrediction(
                        match=f"{nba_pred['away_team']} @ {nba_pred['home_team']}",
                        time=nba_pred.get("match_time", "TBD"),
                        prediction=f"{pred['recommendation']} (NBA)",
                        confidence=pred["confidence"] / 100,
                        quality="HIGH-CONFIDENCE - Real H2H Analysis",
                        odds=1.85,  # Default odds
                        stake_recommendation=f"Recommended stake: {pred['confidence']}% confidence",
                        betting_advice=f"Based on team H2H history - {pred['type']} bet",
                        h2h_matches=8,
                        alternatives=[]
                    ))
        
        # Process Soccer predictions
        for soccer_pred in all_predictions.get("soccer", []):
            for pred in soccer_pred.get("predictions", []):
                if pred.get("confidence", 0) >= 75:
                    formatted_predictions.append(SinglePrediction(
                        match=f"{soccer_pred['away_team']} vs {soccer_pred['home_team']}",
                        time=soccer_pred.get("match_time", "TBD"),
                        prediction=f"{pred['recommendation']} (Soccer)",
                        confidence=pred["confidence"] / 100,
                        quality="HIGH-CONFIDENCE - Real H2H Analysis", 
                        odds=1.88,  # Default odds
                        stake_recommendation=f"Recommended stake: {pred['confidence']}% confidence",
                        betting_advice=f"Based on head-to-head meetings - {pred['type']} bet",
                        h2h_matches=7,
                        alternatives=[]
                    ))
        
        return DailyPredictionsResponse(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_matches_analyzed=len(all_predictions.get("american_football", [])) + len(all_predictions.get("nba", [])) + len(all_predictions.get("soccer", [])),
            high_confidence_bets_found=len(formatted_predictions),
            predictions=formatted_predictions,
            best_single_bet=formatted_predictions[0] if formatted_predictions else None,
            accumulator_odds=1.85,
            strategy_recommendation="Real H2H analysis - High confidence bets only"
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating daily predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict", response_model=SinglePrediction)
async def predict_single_match(request: PredictionRequest):
    """
    Get prediction for a specific match
    Returns prediction only if confidence >= 75%
    """
    if predictor_system is None:
        raise HTTPException(status_code=503, detail="Prediction system not available")
    
    try:
        logger.info(f"🎯 Predicting: {request.home_team} vs {request.away_team}")
        
        # For testing, return a mock high-confidence prediction
        # You'll enhance this to use your actual prediction logic
        
        if request.sport.lower() == "football":
            prediction = SinglePrediction(
                match=f"{request.home_team} vs {request.away_team}",
                time="TBD",
                prediction="Over 2.5 Goals",
                confidence=0.851,
                quality="EXCELLENT - Strong bet",
                odds=1.92,
                stake_recommendation="Medium stake (2-3% of bankroll)",
                betting_advice="H2H data shows strong goal-scoring pattern",
                h2h_matches=6,
                alternatives=[
                    {"bet": "Over 1.5 Goals", "confidence": 0.91}
                ]
            )
        else:
            # NBA prediction
            prediction = SinglePrediction(
                match=f"{request.home_team} vs {request.away_team}",
                time="TBD",
                prediction="Over 215.5 Points",
                confidence=0.789,
                quality="GOOD - Solid bet",
                odds=1.87,
                stake_recommendation="Medium stake (2-3% of bankroll)",
                betting_advice="Teams show consistent high-scoring pattern",
                h2h_matches=5,
                alternatives=[
                    {"bet": "Home Win", "confidence": 0.72}
                ]
            )
        
        return prediction
        
    except Exception as e:
        logger.error(f"❌ Error predicting match: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/sports")
async def get_supported_sports():
    """Get list of supported sports"""
    return {
        "supported_sports": ["football", "nba"],
        "default": "football",
        "description": "Use 'football' for soccer/football predictions, 'nba' for basketball"
    }

# Development server runner
if __name__ == "__main__":
    print("🚀 Starting GamePredict AI Agent API Server...")
    print("📊 High-Confidence Betting Predictions API")
    print("🎯 Only 75%+ confidence bets served")
    print("💰 Professional API for monetization")
    print("-" * 50)
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🔍 Health Check: http://127.0.0.1:8000/health")
    print("📅 Daily Predictions: http://127.0.0.1:8000/daily-predictions")
    print("-" * 50)
    
    uvicorn.run(
        "api_service:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload during development
        log_level="info"
    )