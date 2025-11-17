"""Quick test: Check games available for tomorrow (Nov 18)"""
from datetime import datetime, timedelta
import requests

tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
print(f"Checking games for TOMORROW: {tomorrow} (Nov 18, 2025)")
print("=" * 60)

# NFL
nfl_url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={tomorrow}"
resp = requests.get(nfl_url)
nfl_games = resp.json().get("events", [])
print(f"\nNFL: {len(nfl_games)} games")
for game in nfl_games[:3]:
    comp = game.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) >= 2:
        away = competitors[0].get('team', {}).get('displayName', 'Away')
        home = competitors[1].get('team', {}).get('displayName', 'Home')
        print(f"  - {away} @ {home}")

# NBA
nba_url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={tomorrow}"
resp = requests.get(nba_url)
nba_games = resp.json().get("events", [])
print(f"\nNBA: {len(nba_games)} games")
for game in nba_games[:5]:
    comp = game.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) >= 2:
        away = competitors[0].get('team', {}).get('displayName', 'Away')
        home = competitors[1].get('team', {}).get('displayName', 'Home')
        print(f"  - {away} @ {home}")

# Soccer
soccer_url = f"http://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={tomorrow}"
resp = requests.get(soccer_url)
soccer_games = resp.json().get("events", [])
print(f"\nSOCCER (Premier League): {len(soccer_games)} games")
for game in soccer_games[:5]:
    comp = game.get('competitions', [{}])[0]
    competitors = comp.get('competitors', [])
    if len(competitors) >= 2:
        away = competitors[0].get('team', {}).get('displayName', 'Away')
        home = competitors[1].get('team', {}).get('displayName', 'Home')
        print(f"  - {away} @ {home}")

print("\n" + "=" * 60)
print("SUMMARY: Your agent automatically fetches games for whatever date")
print("you specify. Just change the date parameter in the API call!")
