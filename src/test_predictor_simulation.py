"""
Test simulation for the quality-first prediction system
This creates mock data to demonstrate the H2H validation and quality filtering logic
"""
import random
from datetime import datetime
from typing import List, Dict

class MockDataCollector:
    """Mock data collector that simulates Live Score API responses"""
    
    def __init__(self):
        self.teams = [
            "Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United",
            "Tottenham", "Newcastle", "Brighton", "West Ham", "Aston Villa",
            "Crystal Palace", "Fulham", "Wolves", "Everton", "Brentford",
            "Nottingham Forest", "Sheffield United", "Luton Town", "Burnley", "Bournemouth"
        ]
    
    def has_sufficient_h2h_data(self, h2h_matches: List[Dict], min_matches: int = 3) -> bool:
        """Check if there's sufficient H2H data"""
        return len(h2h_matches) >= min_matches
    
    def get_todays_valid_fixtures(self) -> List[Dict]:
        """Generate mock fixtures with varying H2H data quality"""
        fixtures = []
        
        print("📊 Simulating today's fixtures...")
        
        # Generate 12 random matchups
        for i in range(12):
            home_team = random.choice(self.teams)
            away_team = random.choice([t for t in self.teams if t != home_team])
            
            # Simulate H2H matches (some teams have more history than others)
            h2h_count = random.choice([0, 1, 2, 3, 5, 8, 12, 15])  # Varying H2H data
            h2h_matches = self._generate_mock_h2h(home_team, away_team, h2h_count)
            
            match = {
                "home_name": home_team,
                "away_name": away_team,
                "home_id": i * 2,
                "away_id": i * 2 + 1,
                "date": f"2025-10-09 {14 + i//2}:{(i%2)*30:02d}",
                "h2h_data": h2h_matches
            }
            fixtures.append(match)
        
        # Filter for sufficient H2H data
        valid_fixtures = []
        insufficient_count = 0
        
        print(f"📊 Analyzing {len(fixtures)} total fixtures for H2H data quality...")
        
        for match in fixtures:
            home = match["home_name"]
            away = match["away_name"]
            h2h_matches = match["h2h_data"]
            h2h_count = len(h2h_matches)
            
            if self.has_sufficient_h2h_data(h2h_matches):
                valid_fixtures.append(match)
                print(f"✅ {home:<20} vs {away:<20} - {h2h_count} valid H2H matches")
            else:
                print(f"⏭️  {home:<20} vs {away:<20} - Only {h2h_count} H2H matches (need ≥3)")
                insufficient_count += 1
        
        print(f"\n🎯 SUMMARY: {len(valid_fixtures)} fixtures qualify, {insufficient_count} skipped due to insufficient H2H data")
        print(f"💡 Quality over quantity - better to predict {len(valid_fixtures)} matches well than many poorly!")
        
        return valid_fixtures
    
    def _generate_mock_h2h(self, home_team: str, away_team: str, count: int) -> List[Dict]:
        """Generate mock H2H match data"""
        h2h_matches = []
        for i in range(count):
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 4)
            h2h_matches.append({
                "home_name": home_team,
                "away_name": away_team,
                "score": f"{home_goals}:{away_goals}",
                "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            })
        return h2h_matches

class MockPredictor:
    """Mock predictor that simulates ML predictions with confidence levels"""
    
    def __init__(self):
        self.data_collector = MockDataCollector()
        self.prediction_types = [
            "Home Win", "Away Win", "Draw", 
            "Over 1.5 Goals", "Over 2.5 Goals", "Over 3.5 Goals",
            "Under 2.5 Goals", "Both Teams to Score"
        ]
    
    def predict_match(self, home: str, away: str, h2h_matches: List[Dict]) -> Dict:
        """Generate mock prediction with realistic confidence levels"""
        
        # Analyze H2H to generate realistic confidence
        total_goals = []
        home_wins = 0
        
        for match in h2h_matches:
            score = match.get("score", "")
            if ":" in score:
                try:
                    h_goals, a_goals = map(int, score.split(":"))
                    total_goals.append(h_goals + a_goals)
                    if h_goals > a_goals:
                        home_wins += 1
                except:
                    continue
        
        avg_goals = sum(total_goals) / len(total_goals) if total_goals else 2.5
        home_win_rate = home_wins / len(h2h_matches) if h2h_matches else 0.33
        
        # Generate prediction based on H2H analysis
        if avg_goals > 3.0:
            prediction = "Over 2.5 Goals"
            base_confidence = 0.75
        elif avg_goals > 2.5:
            prediction = "Over 1.5 Goals"  
            base_confidence = 0.80
        elif home_win_rate > 0.6:
            prediction = "Home Win"
            base_confidence = 0.70
        elif home_win_rate < 0.3:
            prediction = "Away Win"
            base_confidence = 0.72
        else:
            prediction = random.choice(self.prediction_types)
            base_confidence = 0.65
        
        # Add some randomness to confidence
        confidence = base_confidence + random.uniform(-0.15, 0.15)
        confidence = max(0.5, min(0.95, confidence))  # Keep between 50-95%
        
        return {
            "home_team": home,
            "away_team": away,
            "prediction": prediction,
            "confidence": confidence,
            "h2h_matches": len(h2h_matches),
            "ml_prediction": prediction,
            "rule_based_prediction": prediction,
            "h2h_matches_count": len(h2h_matches)
        }
    
    def get_daily_predictions(self, min_confidence: float = 0.75) -> List[Dict]:
        """Get quality-filtered predictions"""
        print("Getting today's fixtures with sufficient H2H data...")
        fixtures = self.data_collector.get_todays_valid_fixtures()
        
        if not fixtures:
            print("No fixtures with sufficient H2H data found for today")
            return []
        
        print(f"Analyzing {len(fixtures)} fixtures...")
        all_predictions = []
        
        for match in fixtures:
            home = match["home_name"]
            away = match["away_name"]
            h2h_matches = match["h2h_data"]
            match_time = match["date"]
            
            print(f"Analyzing {home} vs {away}...")
            
            prediction = self.predict_match(home, away, h2h_matches)
            prediction["match_time"] = match_time
            
            all_predictions.append(prediction)
        
        # Filter by confidence threshold (no quantity limits)
        confident_predictions = [
            p for p in all_predictions 
            if p["confidence"] >= min_confidence
        ]
        
        confident_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        print(f"\n🎯 Found {len(confident_predictions)} confident predictions (>{min_confidence:.0%} confidence)")
        if confident_predictions:
            for pred in confident_predictions:
                match_info = f"{pred['home_team']} vs {pred['away_team']}"
                print(f"  ✅ {match_info}: {pred['prediction']} ({pred['confidence']:.1%})")
        else:
            print("  ℹ️  No predictions meet the confidence threshold today")
        
        return confident_predictions

def main():
    """Test the quality-first prediction system with mock data"""
    print("=== TESTING QUALITY-FIRST PREDICTION SYSTEM ===\n")
    
    predictor = MockPredictor()
    
    # Test with different confidence thresholds
    for confidence_threshold in [0.70, 0.75, 0.80]:
        print(f"\n{'='*60}")
        print(f"TESTING WITH {confidence_threshold:.0%} CONFIDENCE THRESHOLD")
        print(f"{'='*60}")
        
        predictions = predictor.get_daily_predictions(min_confidence=confidence_threshold)
        
        if predictions:
            print(f"\n=== ALL CONFIDENT PREDICTIONS ({len(predictions)} matches) ===")
            for i, pred in enumerate(predictions, 1):
                print(f"\n{i}. {pred['home_team']} vs {pred['away_team']}")
                print(f"   Time: {pred['match_time']}")
                print(f"   Prediction: {pred['prediction']} (Confidence: {pred['confidence']:.1%})")
                print(f"   H2H Matches: {pred['h2h_matches']}")
        else:
            print(f"\n=== NO CONFIDENT PREDICTIONS AT {confidence_threshold:.0%} THRESHOLD ===")
            print("Consider lowering confidence threshold or waiting for matches with better H2H data.")

if __name__ == "__main__":
    main()