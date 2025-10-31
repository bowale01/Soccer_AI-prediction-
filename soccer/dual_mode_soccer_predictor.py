"""
Dual-Mode Soccer Predictor
Supports both ESPN (current) and LiveScore (future) with easy switching
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from soccer.espn_soccer_h2h_collector import ESPNSoccerH2HCollector

class DualModeSoccerPredictor:
    """Soccer predictor that can seamlessly switch between ESPN and LiveScore"""
    
    def __init__(self, use_livescore: bool = False):
        self.name = "Dual-Mode Soccer Predictor"
        self.confidence_threshold = 75.0
        self.use_livescore = use_livescore
        
        # Check for LiveScore credentials
        livescore_key = os.getenv('LIVESCORE_API_KEY')
        livescore_secret = os.getenv('LIVESCORE_API_SECRET')
        
        if use_livescore and livescore_key and livescore_secret:
            self._initialize_livescore()
        else:
            self._initialize_espn()
    
    def _initialize_espn(self):
        """Initialize ESPN mode (current working system)"""
        try:
            self.data_source = "ESPN"
            self.h2h_collector = ESPNSoccerH2HCollector()
            print("⚽ Using ESPN Soccer API (Free)")
            print("📊 Coverage: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, MLS, Champions League")
            print("✅ ESPN Soccer system ready")
            self.system_ready = True
        except Exception as e:
            print(f"❌ ESPN initialization failed: {e}")
            self.system_ready = False
    
    def _initialize_livescore(self):
        """Initialize LiveScore mode (when credentials available)"""
        try:
            self.data_source = "LiveScore"
            # Import your existing LiveScore code
            sys.path.append(str(Path(__file__).parent.parent / "src"))
            from data_collector import LiveScoreDataCollector
            from predictor import GamePredictor
            
            self.livescore_collector = LiveScoreDataCollector()
            self.livescore_predictor = GamePredictor()
            print("⚽ Using LiveScore API (Premium)")
            print("📊 Coverage: Comprehensive global soccer leagues")
            print("✅ LiveScore Soccer system ready")
            self.system_ready = True
        except Exception as e:
            print(f"⚠️ LiveScore unavailable, falling back to ESPN: {e}")
            self._initialize_espn()
    
    def get_daily_predictions(self) -> List[Dict]:
        """Get predictions using active data source"""
        if not self.system_ready:
            print("❌ No prediction system available")
            return []
        
        if self.data_source == "LiveScore":
            return self._get_livescore_predictions()
        else:
            return self._get_espn_predictions()
    
    def _get_espn_predictions(self) -> List[Dict]:
        """Get ESPN predictions (your current working system)"""
        print(f"\n🔍 {self.data_source}: Analyzing today's fixtures...")
        
        try:
            fixtures = self.h2h_collector.get_today_fixtures()
            
            if not fixtures:
                print("📅 No soccer fixtures found for today")
                return []
            
            print(f"📊 Analyzing {len(fixtures)} fixtures across major leagues...")
            
            predictions = []
            for fixture in fixtures:
                prediction_data = self._analyze_espn_match(fixture)
                if prediction_data:
                    predictions.append(prediction_data)
            
            # Filter for high confidence only
            high_confidence_predictions = [
                p for p in predictions 
                if any(pred.get('confidence', 0) >= self.confidence_threshold for pred in p.get('predictions', []))
            ]
            
            print(f"🎯 Found {len(high_confidence_predictions)} high-confidence predictions")
            return high_confidence_predictions
            
        except Exception as e:
            print(f"❌ ESPN prediction error: {str(e)[:50]}")
            return []
    
    def _get_livescore_predictions(self) -> List[Dict]:
        """Get LiveScore predictions (when available)"""
        print(f"\n🔍 {self.data_source}: Getting comprehensive predictions...")
        
        try:
            # Use your existing LiveScore predictor
            daily_preds = self.livescore_predictor.get_daily_predictions()
            
            formatted_predictions = []
            for pred in daily_preds:
                if pred.get('is_high_confidence', False) or pred.get('confidence', 0) > 0.75:
                    formatted_pred = {
                        'home_team': pred.get('home_team', 'Home'),
                        'away_team': pred.get('away_team', 'Away'),
                        'league': 'Soccer',
                        'match_time': pred.get('match_time', 'TBD'),
                        'data_source': 'LiveScore',
                        'predictions': [{
                            'type': 'soccer_prediction',
                            'recommendation': pred.get('ml_prediction', pred.get('prediction', 'Unknown')),
                            'confidence': int((pred.get('confidence', 0.75)) * 100),
                            'reasoning': f"LiveScore H2H Analysis - {pred.get('h2h_matches_count', 0)} matches"
                        }]
                    }
                    formatted_predictions.append(formatted_pred)
            
            print(f"🎯 Found {len(formatted_predictions)} high-confidence LiveScore predictions")
            return formatted_predictions
            
        except Exception as e:
            print(f"❌ LiveScore prediction error: {str(e)[:50]}")
            return []
    
    def _analyze_espn_match(self, fixture: Dict) -> Optional[Dict]:
        """Analyze ESPN match (reuse your existing logic)"""
        try:
            home_team = fixture['home_team']
            away_team = fixture['away_team']
            home_id = fixture['home_id']
            away_id = fixture['away_id']
            league_code = fixture['league_code']
            
            # Get H2H data
            h2h_data = self.h2h_collector.get_team_h2h_data(home_id, away_id, league_code)
            
            if h2h_data['matches_count'] < 3:
                return None  # Not enough data
            
            # Generate predictions based on H2H analysis
            predictions = []
            
            # Over/Under 2.5 Goals prediction
            over_under_pred = self._predict_over_under(h2h_data)
            if over_under_pred['confidence'] >= self.confidence_threshold:
                predictions.append(over_under_pred)
            
            # Match result prediction
            result_pred = self._predict_match_result(h2h_data)
            if result_pred['confidence'] >= self.confidence_threshold:
                predictions.append(result_pred)
            
            if not predictions:
                return None  # No confident predictions
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'league': fixture['league'],
                'match_time': fixture.get('match_time', 'TBD'),
                'data_source': 'ESPN',
                'h2h_matches': h2h_data['matches_count'],
                'predictions': predictions
            }
            
        except Exception as e:
            return None
    
    def _predict_over_under(self, h2h_data: Dict) -> Dict:
        """Predict Over/Under 2.5 goals"""
        avg_goals = h2h_data['avg_goals_per_match']
        over_2_5_rate = h2h_data['over_2_5_rate']
        matches_count = h2h_data['matches_count']
        
        base_confidence = min(60 + (matches_count * 2), 85)
        
        if avg_goals >= 3.0 and over_2_5_rate >= 0.7:
            confidence = min(base_confidence + 15, 95)
            recommendation = "Over 2.5 Goals"
        elif avg_goals <= 1.8 and over_2_5_rate <= 0.3:
            confidence = min(base_confidence + 12, 92)
            recommendation = "Under 2.5 Goals"
        elif avg_goals >= 2.5:
            confidence = min(base_confidence + 8, 85)
            recommendation = "Over 2.5 Goals"
        else:
            confidence = min(base_confidence, 76)
            recommendation = "Under 2.5 Goals"
        
        return {
            'type': 'over_under',
            'recommendation': recommendation,
            'confidence': round(confidence, 1),
            'reasoning': f"H2H avg: {avg_goals} goals, Over 2.5 rate: {over_2_5_rate:.1%}"
        }
    
    def _predict_match_result(self, h2h_data: Dict) -> Dict:
        """Predict match result"""
        team1_wins = h2h_data['team1_wins']
        team2_wins = h2h_data['team2_wins']
        draws = h2h_data['draws']
        total_matches = h2h_data['matches_count']
        
        team1_win_rate = team1_wins / total_matches
        team2_win_rate = team2_wins / total_matches
        
        base_confidence = 55 + (total_matches * 3)
        
        if team1_win_rate >= 0.6:
            prediction = "Home Win"
            confidence = min(base_confidence + (team1_win_rate * 25), 88)
        elif team2_win_rate >= 0.6:
            prediction = "Away Win"
            confidence = min(base_confidence + (team2_win_rate * 25), 88)
        else:
            # Pick most likely
            if team1_win_rate > team2_win_rate:
                prediction = "Home Win"
                confidence = min(base_confidence + 5, 78)
            else:
                prediction = "Away Win"
                confidence = min(base_confidence + 5, 78)
        
        return {
            'type': 'match_result',
            'recommendation': prediction,
            'confidence': round(confidence, 1),
            'reasoning': f"H2H record: {team1_wins}-{draws}-{team2_wins}"
        }
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        try:
            if self.data_source == "ESPN":
                fixtures = self.h2h_collector.get_today_fixtures()
                fixture_count = len(fixtures)
            else:
                fixture_count = "Unknown"  # LiveScore check would go here
            
            return {
                'status': 'OPERATIONAL' if self.system_ready else 'DEGRADED',
                'data_source': self.data_source,
                'fixtures_available': fixture_count,
                'confidence_threshold': f"{self.confidence_threshold}%",
                'livescore_ready': os.getenv('LIVESCORE_API_KEY') is not None
            }
            
        except Exception as e:
            return {
                'status': 'DEGRADED',
                'error': str(e)[:50],
                'data_source': self.data_source
            }
    
    def switch_to_livescore(self):
        """Switch to LiveScore mode (when subscription ready)"""
        print("🔄 Switching to LiveScore mode...")
        self.use_livescore = True
        self._initialize_livescore()
    
    def switch_to_espn(self):
        """Switch to ESPN mode"""
        print("🔄 Switching to ESPN mode...")
        self.use_livescore = False
        self._initialize_espn()

def main():
    """Demo the dual-mode system"""
    print("🚀 Testing Dual-Mode Soccer Predictor...")
    
    # Current mode (ESPN)
    predictor = DualModeSoccerPredictor(use_livescore=False)
    
    health = predictor.get_health_status()
    print(f"\n📊 Health: {health}")
    
    predictions = predictor.get_daily_predictions()
    print(f"\n✅ Generated {len(predictions)} predictions")
    
    print("\n" + "="*60)
    print("💡 TO SWITCH TO LIVESCORE LATER:")
    print("1. Get LiveScore API subscription")
    print("2. Add keys to .env file:")
    print("   LIVESCORE_API_KEY=your_key")
    print("   LIVESCORE_API_SECRET=your_secret")
    print("3. predictor.switch_to_livescore()")
    print("4. Or just: DualModeSoccerPredictor(use_livescore=True)")

if __name__ == "__main__":
    main()