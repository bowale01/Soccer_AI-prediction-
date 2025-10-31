"""
American Football Betting Odds API Integration
Fetches real betting lines from sportsbooks for accurate predictions
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class BettingOddsAPI:
    """Integration with sports betting APIs to get real odds"""
    
    def __init__(self):
        # The Odds API - Free tier: 500 requests/month
        self.odds_api_key = "YOUR_ODDS_API_KEY"  # User needs to get free key
        self.odds_base_url = "https://api.the-odds-api.com/v4/sports"
        
        # Backup: ESPN API for basic odds data
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/football"
        
    def get_ncaa_betting_lines(self, date: str = None) -> List[Dict]:
        """Get NCAA Football betting lines for specific date"""
        
        if not date:
            date = datetime.now().strftime('%Y%m%d')
            
        try:
            # Try The Odds API first (most accurate)
            odds_data = self._get_odds_api_data('americanfootball_ncaaf', date)
            if odds_data:
                return self._parse_odds_api_response(odds_data)
                
            # Fallback to ESPN odds data
            print("⚠️  Using ESPN fallback for betting lines")
            return self._get_espn_odds_fallback('college-football', date)
            
        except Exception as e:
            print(f"❌ Error fetching betting lines: {e}")
            return self._get_mock_realistic_lines(date)
    
    def get_nfl_betting_lines(self, date: str = None) -> List[Dict]:
        """Get NFL betting lines for specific date"""
        
        if not date:
            date = datetime.now().strftime('%Y%m%d')
            
        try:
            # Try The Odds API first
            odds_data = self._get_odds_api_data('americanfootball_nfl', date)
            if odds_data:
                return self._parse_odds_api_response(odds_data)
                
            # Fallback to ESPN
            print("⚠️  Using ESPN fallback for betting lines")
            return self._get_espn_odds_fallback('nfl', date)
            
        except Exception as e:
            print(f"❌ Error fetching betting lines: {e}")
            return self._get_mock_realistic_lines(date, league='NFL')
    
    def _get_odds_api_data(self, sport: str, date: str) -> Optional[Dict]:
        """Fetch data from The Odds API"""
        
        # Check if API key is configured
        if self.odds_api_key == "YOUR_ODDS_API_KEY":
            return None
            
        url = f"{self.odds_base_url}/{sport}/odds"
        params = {
            'apiKey': self.odds_api_key,
            'regions': 'us',
            'markets': 'h2h,totals',  # Moneylines and Over/Under
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Odds API error: {e}")
            return None
    
    def _parse_odds_api_response(self, odds_data: List[Dict]) -> List[Dict]:
        """Parse The Odds API response into our format"""
        
        parsed_lines = []
        
        for game in odds_data:
            if not game.get('bookmakers'):
                continue
                
            # Get DraftKings or FanDuel odds (most reliable)
            bookmaker = None
            for bm in game['bookmakers']:
                if bm['key'] in ['draftkings', 'fanduel', 'betmgm']:
                    bookmaker = bm
                    break
            
            if not bookmaker:
                continue
                
            game_data = {
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': game['commence_time'],
                'moneylines': {},
                'totals': {}
            }
            
            # Parse markets
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':  # Moneylines
                    for outcome in market['outcomes']:
                        team_name = outcome['name']
                        game_data['moneylines'][team_name] = outcome['price']
                        
                elif market['key'] == 'totals':  # Over/Under
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Over':
                            game_data['totals']['over'] = {
                                'line': outcome['point'],
                                'odds': outcome['price']
                            }
                        elif outcome['name'] == 'Under':
                            game_data['totals']['under'] = {
                                'line': outcome['point'],
                                'odds': outcome['price']
                            }
            
            parsed_lines.append(game_data)
        
        return parsed_lines
    
    def _get_espn_odds_fallback(self, sport: str, date: str) -> List[Dict]:
        """Fallback to ESPN for basic odds data"""
        
        try:
            url = f"{self.espn_base_url}/{sport}/scoreboard"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games_with_odds = []
            
            for event in data.get('events', []):
                if not event.get('competitions'):
                    continue
                    
                competition = event['competitions'][0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) != 2:
                    continue
                    
                home_team = next((c['team']['displayName'] for c in competitors if c.get('homeAway') == 'home'), '')
                away_team = next((c['team']['displayName'] for c in competitors if c.get('homeAway') == 'away'), '')
                
                # ESPN sometimes has odds data
                odds_data = competition.get('odds', [])
                if odds_data:
                    odds = odds_data[0]
                    game_odds = {
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': event.get('date'),
                        'moneylines': {},
                        'totals': {}
                    }
                    
                    # Parse ESPN odds format
                    if 'overUnder' in odds:
                        game_odds['totals']['over'] = {
                            'line': odds['overUnder'],
                            'odds': -110  # Standard
                        }
                        game_odds['totals']['under'] = {
                            'line': odds['overUnder'],
                            'odds': -110  # Standard
                        }
                    
                    games_with_odds.append(game_odds)
            
            return games_with_odds
            
        except Exception as e:
            print(f"⚠️  ESPN fallback error: {e}")
            return []
    
    def _get_mock_realistic_lines(self, date: str, league: str = 'NCAA') -> List[Dict]:
        """Generate realistic mock betting lines as last resort"""
        
        print("⚠️  Using mock realistic betting lines - Get API key for real odds!")
        print("📝 Sign up at https://the-odds-api.com for free 500 requests/month")
        
        # These ranges are based on actual 2024 betting line analysis
        if league == 'NFL':
            total_ranges = [
                (41.5, 43.5),   # Low-scoring games
                (44.5, 47.5),   # Average games  
                (48.5, 52.5)    # High-scoring games
            ]
        else:  # NCAA
            total_ranges = [
                (45.5, 49.5),   # Low-scoring games
                (52.5, 58.5),   # Average games
                (61.5, 68.5)    # High-scoring games
            ]
        
        # Common betting lines (sportsbooks use .5 to avoid pushes)
        common_totals = []
        for min_total, max_total in total_ranges:
            current = min_total
            while current <= max_total:
                common_totals.append(current)
                current += 1.0  # Increment by 1
        
        mock_games = []
        import random
        
        # Generate some realistic mock games
        teams = [
            "Alabama", "Georgia", "Ohio State", "Michigan", "Texas", 
            "USC", "Oklahoma", "Notre Dame", "Clemson", "Florida State"
        ]
        
        for i in range(5):  # Generate 5 mock games
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            total_line = random.choice(common_totals)
            
            mock_games.append({
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': datetime.now().isoformat(),
                'moneylines': {
                    home_team: random.choice([-120, -110, +105, +110, +125]),
                    away_team: random.choice([-120, -110, +105, +110, +125])
                },
                'totals': {
                    'over': {'line': total_line, 'odds': -110},
                    'under': {'line': total_line, 'odds': -110}
                }
            })
        
        return mock_games
    
    def find_game_odds(self, home_team: str, away_team: str, all_odds: List[Dict]) -> Optional[Dict]:
        """Find betting odds for specific game"""
        
        # Normalize team names for matching
        home_normalized = self._normalize_team_name(home_team)
        away_normalized = self._normalize_team_name(away_team)
        
        for game in all_odds:
            game_home = self._normalize_team_name(game['home_team'])
            game_away = self._normalize_team_name(game['away_team'])
            
            if (home_normalized in game_home or game_home in home_normalized) and \
               (away_normalized in game_away or game_away in away_normalized):
                return game
        
        return None
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names for matching"""
        
        # Remove common suffixes
        name = team_name.lower()
        suffixes = ['tigers', 'bulldogs', 'wildcats', 'eagles', 'bears', 'lions', 
                   'hawks', 'wolves', 'cougars', 'trojans', 'spartans', 'cardinals']
        
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name.replace(suffix, '').strip()
                break
        
        # Remove state abbreviations
        name = name.replace('(', '').replace(')', '')
        
        return name

# Example usage and testing
if __name__ == "__main__":
    api = BettingOddsAPI()
    
    print("🏈 Testing Betting Odds API Integration")
    print("=" * 50)
    
    # Test NCAA odds
    print("\n📊 NCAA Football Betting Lines:")
    ncaa_odds = api.get_ncaa_betting_lines()
    
    for game in ncaa_odds[:3]:  # Show first 3 games
        print(f"\n🏈 {game['away_team']} @ {game['home_team']}")
        
        if game['totals']:
            total_line = game['totals']['over']['line']
            print(f"   💰 OVER/UNDER: {total_line} points")
        
        if game['moneylines']:
            print(f"   💰 MONEYLINES: Available")
    
    print("\n✅ Integration ready - Get free API key for real odds!")
    print("📝 Visit: https://the-odds-api.com")