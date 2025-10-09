"""
Consolidated Data Collection Module
Combines functionality from:
- step1_collect_historical_data.py
- step1_daily_data_collection.py  
- test_live_score_api_h2h.py
"""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('LIVESCORE_API_KEY')
API_SECRET = os.getenv('LIVESCORE_API_SECRET')
BASE_URL = "https://livescore-api.com/api-client"

# Validate API credentials are loaded
if not API_KEY or not API_SECRET:
    raise ValueError("API credentials not found. Please check your .env file contains LIVESCORE_API_KEY and LIVESCORE_API_SECRET")

class LiveScoreDataCollector:
    """Unified data collector for Live Score API"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
    
    def get_fixtures(self, date: str = None, days: int = 1) -> List[Dict]:
        """Get fixtures for a specific date or date range"""
        fixtures = []
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        for i in range(days):
            if days > 1:
                current_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
            else:
                current_date = date
                
            url = f"{self.base_url}/fixtures/matches.json?key={self.api_key}&secret={self.api_secret}&date={current_date}"
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                data = resp.json()
                fixtures.extend(data.get("data", {}).get("fixtures", []))
            except requests.RequestException as e:
                print(f"Error fetching fixtures for {current_date}: {e}")
        
        return fixtures
    
    def get_today_fixtures(self) -> List[Dict]:
        """Get today's fixtures"""
        return self.get_fixtures()
    
    def get_todays_valid_fixtures(self) -> List[Dict]:
        """Get today's fixtures that have sufficient H2H data for predictions"""
        fixtures = self.get_today_fixtures()
        valid_fixtures = []
        
        print(f"📊 Analyzing {len(fixtures)} total fixtures for H2H data quality...")
        
        skipped_count = 0
        for match in fixtures:
            home_id = match.get("home_id")
            away_id = match.get("away_id")
            home_team = match.get("home_name")
            away_team = match.get("away_name")
            
            h2h_matches = self.get_h2h(home_id, away_id)
            valid_h2h_count = len([m for m in h2h_matches if self._parse_score(m.get("score", ""))])
            
            # Only include matches with sufficient H2H data  
            match_time = match.get("date", "TBD")
            if self.has_sufficient_h2h_data(h2h_matches):
                match["h2h_data"] = h2h_matches
                valid_fixtures.append(match)
                print(f"✅ {match_time:<8} | {home_team:<18} vs {away_team:<18} - {valid_h2h_count} H2H matches")
            else:
                print(f"⏭️  {match_time:<8} | {home_team:<18} vs {away_team:<18} - Only {valid_h2h_count} H2H (need ≥3)")
                skipped_count += 1
        
        print(f"\n🎯 SUMMARY: {len(valid_fixtures)} fixtures qualify, {skipped_count} skipped due to insufficient H2H data")
        print(f"💡 Quality over quantity - better to predict {len(valid_fixtures)} matches well than many poorly!")
        return valid_fixtures
    
    def get_historical_fixtures(self, days: int = 30) -> List[Dict]:
        """Get historical fixtures for the past N days"""
        fixtures = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            fixtures.extend(self.get_fixtures(date))
        return fixtures
    
    def get_h2h(self, home_id: int, away_id: int) -> List[Dict]:
        """Get head-to-head matches between two teams"""
        url = f"{self.base_url}/teams/head2head.json?team1_id={home_id}&team2_id={away_id}&key={self.api_key}&secret={self.api_secret}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("matches", [])
        except requests.RequestException as e:
            print(f"Error fetching H2H for teams {home_id} vs {away_id}: {e}")
            return []
    
    def get_recent_form(self, team_id: int) -> List[Dict]:
        """Get recent form for a team"""
        url = f"{self.base_url}/teams/matches.json?team_id={team_id}&key={self.api_key}&secret={self.api_secret}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("matches", [])
        except requests.RequestException as e:
            print(f"Error fetching recent form for team {team_id}: {e}")
            return []
    
    def get_match_stats(self, match_id: int) -> Dict:
        """Get detailed match statistics"""
        url = f"{self.base_url}/matches/stats.json?match_id={match_id}&key={self.api_key}&secret={self.api_secret}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching stats for match {match_id}: {e}")
            return {}
    
    def has_sufficient_h2h_data(self, h2h_matches: List[Dict], min_matches: int = 3) -> bool:
        """Check if there's sufficient H2H data for reliable predictions"""
        valid_matches = 0
        for match in h2h_matches:
            score = match.get("score", "")
            if self._parse_score(score):
                valid_matches += 1
        return valid_matches >= min_matches
    
    def collect_comprehensive_data(self, output_file: str = "comprehensive_match_data.csv") -> None:
        """Collect comprehensive historical data including H2H and form"""
        print("Starting comprehensive data collection...")
        
        # Get fixtures for next 7 days to get team matchups
        fixtures = self.get_fixtures(days=7)
        all_rows = []
        
        for match in fixtures:
            home = match.get("home_name")
            away = match.get("away_name")
            home_id = match.get("home_id")
            away_id = match.get("away_id")
            match_time = match.get("date")
            
            print(f"Processing {home} vs {away}...")
            
            # Get H2H data
            h2h_matches = self.get_h2h(home_id, away_id)
            
            # Get recent form
            home_form = self.get_recent_form(home_id)
            away_form = self.get_recent_form(away_id)
            
            # Process H2H matches
            for h2h in h2h_matches:
                score = h2h.get("score")
                home_goals, away_goals = self._parse_score(score)
                
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
                    "result": self._determine_result(home_goals, away_goals),
                    "home_form_matches": len(home_form),
                    "away_form_matches": len(away_form)
                }
                all_rows.append(row)
        
        # Save to CSV
        df = pd.DataFrame(all_rows)
        
        # Append to existing file if it exists
        try:
            existing = pd.read_csv(output_file)
            df = pd.concat([existing, df], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            pass
        
        df.to_csv(output_file, index=False)
        print(f"Saved {len(all_rows)} records to {output_file} (total: {len(df)})")
    
    def collect_daily_data(self) -> Dict:
        """Collect today's fixture data with analysis"""
        today = datetime.now().strftime("%Y-%m-%d")
        fixtures = self.get_fixtures(today)
        
        print(f"Found {len(fixtures)} fixtures for {today}")
        daily_data = []
        
        for match in fixtures:
            home = match.get("home_name")
            away = match.get("away_name")
            home_id = match.get("home_id")
            away_id = match.get("away_id")
            match_time = match.get("date")
            
            print(f"\n{home} vs {away} at {match_time}")
            
            # Get analysis data
            h2h_matches = self.get_h2h(home_id, away_id)
            home_form = self.get_recent_form(home_id)
            away_form = self.get_recent_form(away_id)
            
            print(f"H2H matches: {len(h2h_matches)}")
            print(f"Recent form - {home}: {len(home_form)} matches")
            print(f"Recent form - {away}: {len(away_form)} matches")
            
            match_data = {
                "home_team": home,
                "away_team": away,
                "home_id": home_id,
                "away_id": away_id,
                "match_time": match_time,
                "h2h_matches": h2h_matches,
                "home_form": home_form,
                "away_form": away_form
            }
            daily_data.append(match_data)
        
        return {
            "date": today,
            "total_matches": len(fixtures),
            "matches": daily_data
        }
    
    def _parse_score(self, score: str) -> tuple:
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
    
    def _determine_result(self, home_goals: int, away_goals: int) -> str:
        """Determine match result"""
        if home_goals is None or away_goals is None:
            return "Unknown"
        
        if home_goals > away_goals:
            return "Home Win"
        elif home_goals < away_goals:
            return "Away Win"
        else:
            return "Draw"

def main():
    """Main function for testing data collection"""
    collector = LiveScoreDataCollector()
    
    # Test API connection
    print("Testing API connection...")
    today_fixtures = collector.get_today_fixtures()
    print(f"Successfully retrieved {len(today_fixtures)} fixtures for today")
    
    # Test H2H functionality
    if today_fixtures:
        first_match = today_fixtures[0]
        home_id = first_match.get("home_id")
        away_id = first_match.get("away_id")
        if home_id and away_id:
            h2h = collector.get_h2h(home_id, away_id)
            print(f"H2H test: Found {len(h2h)} matches")
    
    # Test match stats
    test_match_id = 172252
    stats = collector.get_match_stats(test_match_id)
    print(f"Match stats test: {len(stats)} data points retrieved")

if __name__ == "__main__":
    main()