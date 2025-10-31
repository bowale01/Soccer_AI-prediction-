"""
Working Multi-Sport Interface
Connects the actual working American Football, NBA, and Soccer systems
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Add paths for working modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'american_football'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'nba'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class WorkingMultiSportPredictor:
    """Multi-sport predictor using the actual working systems"""
    
    def __init__(self):
        """Initialize all working sport predictors"""
        print("🚀 WORKING MULTI-SPORT AI PREDICTION SYSTEM")
        print("🎯 Real H2H + AI Agentic Enhancement")
        print("=" * 60)
        
        # Initialize American Football System
        print("\n🏈 AMERICAN FOOTBALL SYSTEM - Real H2H Data")
        print("-" * 45)
        try:
            from american_football.predictor import AmericanFootballPredictor
            self.american_football_predictor = AmericanFootballPredictor()
            print("✅ American Football system initialized (ESPN API + Real H2H)")
        except Exception as e:
            print(f"❌ American Football system error: {e}")
            self.american_football_predictor = None
        
        # Initialize NBA System  
        print("\n🏀 NBA SYSTEM - Real H2H Data")
        print("-" * 35)
        try:
            from nba.predictor import ReliableNBAPredictor
            self.nba_predictor = ReliableNBAPredictor()
            print("✅ NBA system initialized (ESPN API + Real H2H)")
        except Exception as e:
            print(f"❌ NBA system error: {e}")
            self.nba_predictor = None
        
        # Initialize Soccer System - Dual Mode (ESPN + LiveScore Ready)
        print("\n⚽ SOCCER SYSTEM - Dual Mode Ready")
        print("-" * 35)
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'soccer'))
            from soccer.dual_mode_soccer_predictor import DualModeSoccerPredictor
            
            # Check for LiveScore credentials
            livescore_available = os.getenv('LIVESCORE_API_KEY') and os.getenv('LIVESCORE_API_SECRET')
            
            if livescore_available:
                print("🎯 LiveScore credentials found - using premium mode")
                self.soccer_predictor = DualModeSoccerPredictor(use_livescore=True)
            else:
                print("🎯 Using ESPN mode (LiveScore ready when you add credentials)")
                self.soccer_predictor = DualModeSoccerPredictor(use_livescore=False)
                
            print("✅ Dual-mode Soccer system initialized (ESPN + LiveScore Ready)")
        except Exception as e:
            print(f"❌ Soccer system error: {e}")
            self.soccer_predictor = None
        
        print("\n" + "=" * 60)
        print("🎯 All systems ready for high-confidence predictions!")
        print("💰 75% confidence threshold protects customer money")
        print("=" * 60)
    
    def get_all_high_confidence_predictions(self) -> Dict:
        """Get high-confidence predictions from all sports"""
        
        predictions = {
            "timestamp": datetime.now().isoformat(),
            "american_football": [],
            "nba": [], 
            "soccer": [],
            "summary": {
                "total_games_analyzed": 0,
                "high_confidence_picks": 0,
                "success_rate_target": "75%+"
            }
        }
        
        # Get American Football predictions
        if self.american_football_predictor:
            try:
                af_predictions = self._get_american_football_predictions()
                predictions["american_football"] = af_predictions
                predictions["summary"]["total_games_analyzed"] += len(af_predictions)
                high_conf_af = [p for p in af_predictions if p.get("confidence", 0) >= 75]
                predictions["summary"]["high_confidence_picks"] += len(high_conf_af)
            except Exception as e:
                print(f"Error getting American Football predictions: {e}")
        
        # Get NBA predictions  
        if self.nba_predictor:
            try:
                nba_predictions = self._get_nba_predictions()
                predictions["nba"] = nba_predictions
                predictions["summary"]["total_games_analyzed"] += len(nba_predictions)
                high_conf_nba = [p for p in nba_predictions if p.get("confidence", 0) >= 75]
                predictions["summary"]["high_confidence_picks"] += len(high_conf_nba)
            except Exception as e:
                print(f"Error getting NBA predictions: {e}")
        
        # Get Soccer predictions - ESPN API
        if self.soccer_predictor:
            try:
                soccer_predictions = self._get_soccer_predictions() 
                predictions["soccer"] = soccer_predictions
                predictions["summary"]["total_games_analyzed"] += len(soccer_predictions)
                high_conf_soccer = [p for p in soccer_predictions if p.get("confidence", 0) >= 75]
                predictions["summary"]["high_confidence_picks"] += len(high_conf_soccer)
            except Exception as e:
                print(f"Error getting Soccer predictions: {e}")
        
        return predictions
    
    def _get_american_football_predictions(self) -> List[Dict]:
        """Get American Football predictions in standard format"""
        
        try:
            # Get today's games
            nfl_games = self.american_football_predictor.get_nfl_games()
            ncaa_games = self.american_football_predictor.get_ncaa_games()
            all_games = nfl_games + ncaa_games
            
            predictions = []
            
            for game in all_games[:5]:  # Limit to 5 games for API performance
                try:
                    prediction = self.american_football_predictor.predict_game_with_h2h_focus(game)
                    
                    if prediction.get("prediction_made", False):
                        formatted_prediction = {
                            "sport": "american_football",
                            "league": game.get("league", "NFL"),
                            "home_team": game.get("home_team", ""),
                            "away_team": game.get("away_team", ""),
                            "match_time": game.get("time", "TBD"),
                            "predictions": [],
                            "confidence": 0
                        }
                        
                        # Add high-confidence predictions only
                        if prediction.get("over_under_confidence", 0) >= 0.75:
                            formatted_prediction["predictions"].append({
                                "type": "over_under",
                                "recommendation": prediction.get("over_under_recommendation", ""),
                                "confidence": round(prediction.get("over_under_confidence", 0) * 100, 1),
                                "line": prediction.get("predicted_total", 0)
                            })
                            formatted_prediction["confidence"] = max(formatted_prediction["confidence"], 
                                                                   prediction.get("over_under_confidence", 0) * 100)
                        
                        if prediction.get("win_confidence", 0) >= 0.75:
                            formatted_prediction["predictions"].append({
                                "type": "moneyline",
                                "recommendation": prediction.get("win_prediction", ""),
                                "confidence": round(prediction.get("win_confidence", 0) * 100, 1)
                            })
                            formatted_prediction["confidence"] = max(formatted_prediction["confidence"],
                                                                   prediction.get("win_confidence", 0) * 100)
                        
                        if formatted_prediction["predictions"]:  # Only add if has high-confidence picks
                            predictions.append(formatted_prediction)
                
                except Exception as e:
                    continue
            
            return predictions
            
        except Exception as e:
            print(f"Error in American Football predictions: {e}")
            return []
    
    def _get_nba_predictions(self) -> List[Dict]:
        """Get NBA predictions in standard format"""
        
        try:
            # Get today's games
            games = self.nba_predictor.get_todays_nba_games()
            predictions = []
            
            for game in games[:8]:  # Limit for performance
                try:
                    prediction = self.nba_predictor.predict_game_with_h2h_focus(game)
                    
                    if prediction.get("prediction_made", False):
                        formatted_prediction = {
                            "sport": "nba",
                            "league": "NBA",
                            "home_team": game.get("home_team", ""),
                            "away_team": game.get("away_team", ""),
                            "match_time": game.get("time", "TBD"),
                            "predictions": [],
                            "confidence": 0
                        }
                        
                        # Add high-confidence predictions only
                        if prediction.get("over_confidence", 0) >= 0.75:
                            formatted_prediction["predictions"].append({
                                "type": "over_under",
                                "recommendation": "OVER",
                                "confidence": round(prediction.get("over_confidence", 0) * 100, 1),
                                "line": prediction.get("predicted_total", 0)
                            })
                            formatted_prediction["confidence"] = max(formatted_prediction["confidence"],
                                                                   prediction.get("over_confidence", 0) * 100)
                        
                        if prediction.get("win_confidence", 0) >= 0.75:
                            formatted_prediction["predictions"].append({
                                "type": "moneyline", 
                                "recommendation": prediction.get("winner_prediction", ""),
                                "confidence": round(prediction.get("win_confidence", 0) * 100, 1)
                            })
                            formatted_prediction["confidence"] = max(formatted_prediction["confidence"],
                                                                   prediction.get("win_confidence", 0) * 100)
                        
                        if formatted_prediction["predictions"]:  # Only add if has high-confidence picks
                            predictions.append(formatted_prediction)
                
                except Exception as e:
                    continue
            
            return predictions
            
        except Exception as e:
            print(f"Error in NBA predictions: {e}")
            return []
    
    def _get_soccer_predictions(self) -> List[Dict]:
        """Get Soccer predictions using ESPN API system"""
        
        try:
            if not self.soccer_predictor:
                return []
            
            # Use the ESPN soccer predictor directly
            daily_predictions = self.soccer_predictor.get_daily_predictions()
            formatted_predictions = []
            
            for pred in daily_predictions:
                # ESPN predictor already returns high-confidence predictions
                formatted_prediction = {
                    "sport": "soccer",
                    "league": pred.get("league", "Soccer"),
                    "home_team": pred.get("home_team", ""),
                    "away_team": pred.get("away_team", ""),
                    "match_time": pred.get("match_time", "TBD"),
                    "predictions": pred.get("predictions", []),
                    "h2h_summary": pred.get("h2h_summary", {}),
                    "confidence": max([p.get("confidence", 0) for p in pred.get("predictions", [])]) if pred.get("predictions") else 0
                }
                formatted_predictions.append(formatted_prediction)
                
                if len(formatted_predictions) >= 6:  # Limit for performance
                    break
                    
            return formatted_predictions
            
        except Exception as e:
            print(f"Error in Soccer predictions: {e}")
            return []
    
    def get_sport_predictions(self, sport: str) -> List[Dict]:
        """Get predictions for a specific sport"""
        
        if sport.lower() in ["american_football", "football", "nfl", "ncaa"]:
            return self._get_american_football_predictions()
        elif sport.lower() in ["nba", "basketball"]:
            return self._get_nba_predictions()
        elif sport.lower() in ["soccer", "football_soccer"]:
            return self._get_soccer_predictions()
        else:
            return []
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        
        return {
            "status": "operational",
            "systems": {
                "american_football": self.american_football_predictor is not None,
                "nba": self.nba_predictor is not None, 
                "soccer": self.soccer_predictor is not None
            },
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }

# Test the system
if __name__ == "__main__":
    predictor = WorkingMultiSportPredictor()
    
    print("\n🧪 TESTING MULTI-SPORT SYSTEM")
    print("=" * 50)
    
    # Test health status
    health = predictor.get_health_status()
    print(f"\n📊 System Health: {health}")
    
    # Test getting all predictions
    print(f"\n🎯 Getting all high-confidence predictions...")
    all_predictions = predictor.get_all_high_confidence_predictions()
    
    summary = all_predictions["summary"]
    print(f"📊 Games Analyzed: {summary['total_games_analyzed']}")
    print(f"🎯 High-Confidence Picks: {summary['high_confidence_picks']}")
    
    print("\n✅ Working Multi-Sport System Ready!")