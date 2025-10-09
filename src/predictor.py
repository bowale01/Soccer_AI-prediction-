"""
Consolidated Prediction and Training Module
Combines functionality from:
- train_ml_model.py
- daily_ai_match_predictor.py
- daily_fixture_predictions.py
"""

import requests
import numpy as np
import pandas as pd
import random
import joblib
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict, Tuple, Optional
from data_collector import LiveScoreDataCollector

class GamePredictor:
    """Unified prediction and training system"""
    
    def __init__(self, model_path: str = "ml_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.data_collector = LiveScoreDataCollector()
        self.class_map = {
            0: "Home Win", 
            1: "Draw", 
            2: "Away Win", 
            3: "Over 1.5 goals", 
            4: "Over 2.5 goals"
        }
        
        # Try to load existing model
        self.load_model()
    
    def load_model(self) -> bool:
        """Load existing model if available"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"Model loaded from {self.model_path}")
            return True
        except (FileNotFoundError, Exception) as e:
            print(f"No existing model found: {e}")
            return False
    
    def save_model(self) -> None:
        """Save the trained model"""
        if self.model:
            joblib.dump(self.model, self.model_path)
            print(f"Model saved to {self.model_path}")
    
    def extract_features_and_label(self, h2h_matches: List[Dict], actual_score: str = None) -> Tuple[List, Optional[int]]:
        """Extract features from H2H matches and determine label if actual score provided"""
        # Features: avg goals, num matches, home win rate
        if not h2h_matches:
            return [0, 0, 0], None
        
        goals = []
        home_wins = 0
        
        for match in h2h_matches:
            score = match.get("score")
            if score:
                home_goals, away_goals = self._parse_score(score)
                if home_goals is not None and away_goals is not None:
                    goals.append(home_goals + away_goals)
                    if home_goals > away_goals:
                        home_wins += 1
        
        # Calculate features
        avg_goals = sum(goals) / len(goals) if goals else 0
        num_matches = len(goals)
        home_win_rate = home_wins / num_matches if num_matches else 0
        
        features = [avg_goals, num_matches, home_win_rate]
        
        # Calculate label if actual score provided
        label = None
        if actual_score:
            home_goals, away_goals = self._parse_score(actual_score)
            if home_goals is not None and away_goals is not None:
                total_goals = home_goals + away_goals
                
                # Primary label based on match result
                if home_goals > away_goals:
                    label = 0  # Home Win
                elif home_goals == away_goals:
                    label = 1  # Draw
                else:
                    label = 2  # Away Win
                
                # Override with goals prediction if more appropriate
                if total_goals > 2.5:
                    label = 4  # Over 2.5 goals
                elif total_goals > 1.5:
                    label = 3  # Over 1.5 goals
        
        return features, label
    
    def train_model(self, days: int = 30) -> bool:
        """Train the ML model using historical data"""
        print(f"Training model with {days} days of historical data...")
        
        # Get historical fixtures
        fixtures = self.data_collector.get_historical_fixtures(days=days)
        
        X = []
        y = []
        
        print(f"Processing {len(fixtures)} historical fixtures...")
        
        for i, match in enumerate(fixtures):
            if i % 50 == 0:
                print(f"Processed {i}/{len(fixtures)} fixtures...")
            
            home_id = match.get("home_id")
            away_id = match.get("away_id")
            actual_score = match.get("score")
            
            if not home_id or not away_id:
                continue
            
            # Get H2H data
            h2h_matches = self.data_collector.get_h2h(home_id, away_id)
            features, label = self.extract_features_and_label(h2h_matches, actual_score)
            
            if label is not None:
                X.append(features)
                y.append(label)
        
        if not X or not y:
            print("Not enough data to train model.")
            return False
        
        print(f"Training model with {len(X)} samples...")
        
        # Train Random Forest model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save the model
        self.save_model()
        
        print("Model trained and saved successfully!")
        return True
    
    def rule_based_prediction(self, h2h_matches: List[Dict]) -> str:
        """Generate rule-based prediction from H2H data"""
        if not h2h_matches:
            return "No head-to-head data available"
        
        goals = []
        home_wins = 0
        total_matches = 0
        
        for match in h2h_matches:
            score = match.get("score")
            if score:
                home_goals, away_goals = self._parse_score(score)
                if home_goals is not None and away_goals is not None:
                    goals.append(home_goals + away_goals)
                    total_matches += 1
                    if home_goals > away_goals:
                        home_wins += 1
        
        if not goals:
            return random.choice(["Home Win", "Away Win", "Draw"])
        
        avg_goals = sum(goals) / len(goals)
        home_win_rate = home_wins / total_matches
        
        # Decision logic
        if avg_goals > 2.5:
            return "Over 2.5 goals"
        elif avg_goals > 1.5:
            return "Over 1.5 goals"
        elif home_win_rate > 0.6:
            return "Home Win"
        elif home_win_rate < 0.3:
            return "Away Win"
        else:
            return "Draw"
    
    def ml_prediction(self, h2h_matches: List[Dict]) -> Tuple[str, float]:
        """Generate ML-based prediction with confidence"""
        if not self.model:
            return "Model not available", 0.0
        
        features, _ = self.extract_features_and_label(h2h_matches)
        X = np.array(features).reshape(1, -1)
        
        try:
            probabilities = self.model.predict_proba(X)[0]
            predicted_class = np.argmax(probabilities)
            confidence = np.max(probabilities)
            
            prediction = self.class_map.get(predicted_class, "Unknown")
            return prediction, confidence
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return "Prediction error", 0.0
    
    def predict_match(self, home_team: str, away_team: str, home_id: int, away_id: int) -> Dict:
        """Generate comprehensive prediction for a match"""
        # Get H2H data
        h2h_matches = self.data_collector.get_h2h(home_id, away_id)
        
        # Rule-based prediction
        rule_prediction = self.rule_based_prediction(h2h_matches)
        
        # ML prediction (if model available)
        ml_prediction, confidence = self.ml_prediction(h2h_matches)
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "h2h_matches_count": len(h2h_matches),
            "rule_based_prediction": rule_prediction,
            "ml_prediction": ml_prediction,
            "confidence": confidence,
            "is_high_confidence": confidence > 0.8
        }
    
    def get_daily_predictions(self, min_confidence: float = 0.75) -> List[Dict]:
        """Get ALL confident predictions for today (no quantity limits - quality only)"""
        print("Getting today's fixtures with sufficient H2H data...")
        fixtures = self.data_collector.get_todays_valid_fixtures()  # Only fixtures with H2H data
        
        if not fixtures:
            print("No fixtures with sufficient H2H data found for today")
            return []
        
        print(f"Analyzing {len(fixtures)} fixtures...")
        all_predictions = []
        
        for match in fixtures:
            home = match.get("home_name")
            away = match.get("away_name")
            home_id = match.get("home_id")
            away_id = match.get("away_id")
            match_time = match.get("date")
            
            if not all([home, away, home_id, away_id]):
                continue
            
            print(f"Analyzing {home} vs {away}...")
            
            prediction = self.predict_match(home, away, home_id, away_id)
            prediction["match_time"] = match_time
            
            all_predictions.append(prediction)
        
        # Filter predictions by confidence threshold only (no quantity limits)
        if self.model:
            confident_predictions = [
                p for p in all_predictions 
                if p["confidence"] >= min_confidence
            ]
            
            # Sort by confidence - return ALL confident predictions
            confident_predictions.sort(key=lambda x: x["confidence"], reverse=True)
            
            print(f"\n🎯 Found {len(confident_predictions)} confident predictions (>{min_confidence:.0%} confidence)")
            if confident_predictions:
                for pred in confident_predictions:
                    match_info = f"{pred['home_team']} vs {pred['away_team']}"
                    match_time = pred.get('match_time', 'TBD')
                    print(f"  ✅ {match_time} | {match_info}: {pred['prediction']} ({pred['confidence']:.1%})")
            else:
                print("  ℹ️  No predictions meet the confidence threshold today")
            
            return confident_predictions
        else:
            print("Using rule-based predictions (no ML model available)")
            print(f"📊 Returning {len(all_predictions)} rule-based predictions")
            return all_predictions
    
    def analyze_match_detailed(self, home_team: str, away_team: str, home_id: int, away_id: int) -> Dict:
        """Detailed match analysis with statistics"""
        h2h_matches = self.data_collector.get_h2h(home_id, away_id)
        home_form = self.data_collector.get_recent_form(home_id)
        away_form = self.data_collector.get_recent_form(away_id)
        
        # Analyze H2H statistics
        h2h_stats = self._analyze_h2h_stats(h2h_matches)
        
        # Get predictions
        prediction_data = self.predict_match(home_team, away_team, home_id, away_id)
        
        return {
            **prediction_data,
            "h2h_statistics": h2h_stats,
            "home_recent_form": len(home_form),
            "away_recent_form": len(away_form)
        }
    
    def _analyze_h2h_stats(self, h2h_matches: List[Dict]) -> Dict:
        """Analyze H2H match statistics"""
        if not h2h_matches:
            return {"total_matches": 0}
        
        total_goals = []
        home_wins = 0
        away_wins = 0
        draws = 0
        
        for match in h2h_matches:
            score = match.get("score")
            if score:
                home_goals, away_goals = self._parse_score(score)
                if home_goals is not None and away_goals is not None:
                    total_goals.append(home_goals + away_goals)
                    
                    if home_goals > away_goals:
                        home_wins += 1
                    elif home_goals < away_goals:
                        away_wins += 1
                    else:
                        draws += 1
        
        total_matches = len(total_goals)
        
        return {
            "total_matches": total_matches,
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "avg_goals": sum(total_goals) / len(total_goals) if total_goals else 0,
            "over_1_5_rate": sum(1 for g in total_goals if g > 1.5) / len(total_goals) if total_goals else 0,
            "over_2_5_rate": sum(1 for g in total_goals if g > 2.5) / len(total_goals) if total_goals else 0
        }
    
    def _parse_score(self, score: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse score string into home and away goals"""
        if not score:
            return None, None
        
        score = score.replace(" ", "")
        if ":" in score:
            parts = score.split(":")
        elif "-" in score:
            parts = score.split("-")
        else:
            return None, None
        
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return None, None

def main():
    """Main function for testing predictions"""
    predictor = GamePredictor()
    
    # Train model if not available
    if not predictor.model:
        print("No trained model found. Training new model...")
        success = predictor.train_model(days=30)
        if not success:
            print("Failed to train model. Using rule-based predictions only.")
    
    # Get daily predictions (all confident ones - no quantity limits)
    predictions = predictor.get_daily_predictions()
    
    if predictions:
        print(f"\n=== ALL CONFIDENT PREDICTIONS FOR TODAY ({len(predictions)} matches) ===")
        for i, pred in enumerate(predictions, 1):
            match_time = pred.get('match_time', 'TBD')
            print(f"\n{i}. 🕐 {match_time} | {pred['home_team']} vs {pred['away_team']}")
            print(f"   🎯 Prediction: {pred.get('ml_prediction', pred.get('prediction', 'N/A'))} (Confidence: {pred.get('confidence', 0):.1%})")
            print(f"   📊 Rule-based: {pred.get('rule_based_prediction', 'N/A')}")
            print(f"   📈 H2H Matches: {pred.get('h2h_matches_count', pred.get('h2h_matches', 0))}")
    else:
        print(f"\n=== NO CONFIDENT PREDICTIONS TODAY ===")
        print("All matches either lack sufficient H2H data or don't meet confidence threshold.")

if __name__ == "__main__":
    main()