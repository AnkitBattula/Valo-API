import requests
import os
import time
from datetime import datetime

# ⚠️ WARNING: This is an EXAMPLE key from Riot documentation
# It will NOT work. Get your real key from: https://developer.riotgames.com/
API_KEY = "RGAPI-10ed1805-eed6-46aa-b68d-e2f4c20d8c3b"
HEADERS = {"X-Riot-Token": API_KEY}

# Player information - replace with your actual details
GAME_NAME = "DrAnKitYT"
TAG_LINE = "54321"

# Region - change if you're not in North America
REGION = "na"  # Options: na, eu, ap, kr, latam, br
ACCOUNT_REGION = "americas"  # For account APIs
VAL_REGION = f"{REGION}.api.riotgames.com"

# Base URLs
ACCOUNT_BASE = f"https://{ACCOUNT_REGION}.api.riotgames.com"
VALORANT_BASE = f"https://{VAL_REGION}"

def safe_request(url, headers):
    """Make API request with error handling"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 429:
            print("⏳ Rate limited. Waiting 2 seconds...")
            time.sleep(2)
            return safe_request(url, headers)
            
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def get_player_puuid(game_name, tag_line):
    """Get PUUID from Riot ID"""
    print(f"\n🔍 Looking up player: {game_name}#{tag_line}")
    
    url = f"{ACCOUNT_BASE}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    response = safe_request(url, HEADERS)
    
    if response and response.status_code == 200:
        data = response.json()
        print(f"✅ Found: {data['gameName']}#{data['tagLine']}")
        print(f"   PUUID: {data['puuid'][:16]}...")
        return data['puuid']
    elif response:
        print(f"❌ API Error {response.status_code}: {response.text}")
        
        if "403" in str(response.status_code):
            print("   ⚠️  Invalid API key! Get a real key from:")
            print("   https://developer.riotgames.com/")
    else:
        print("❌ Failed to connect to API")
    
    return None

def get_match_history(puuid, count=5):
    """Get recent match history"""
    print(f"\n📊 Fetching last {count} matches...")
    
    url = f"{ACCOUNT_BASE}/val/match/v1/matchlists/by-puuid/{puuid}"
    response = safe_request(url, HEADERS)
    
    if response and response.status_code == 200:
        matches = response.json()
        history = matches.get('history', [])
        
        print(f"✅ Found {len(history)} total matches")
        print("=" * 60)
        
        # Show recent matches
        for i, match in enumerate(history[:count]):
            match_id = match['matchId']
            queue = match.get('queueId', 'unknown')
            
            # Convert queue ID to readable name
            queue_names = {
                'competitive': 'Competitive',
                'unrated': 'Unrated',
                'deathmatch': 'Deathmatch',
                'spikerush': 'Spike Rush',
                'ggteam': 'Escalation',
                'newmap': 'New Map',
                'snowball': 'Snowball Fight'
            }
            
            queue_type = queue_names.get(queue, queue)
            
            print(f"\n#{i+1}: {queue_type}")
            print(f"   Match ID: {match_id[:12]}...")
            print(f"   Started: {datetime.fromtimestamp(match['gameStartTime']/1000).strftime('%Y-%m-%d %H:%M')}")
            
            # Get match details
            match_details = get_match_details(match_id, puuid)
            if match_details:
                time.sleep(0.1)  # Rate limiting
        
        return matches
    return None

def get_match_details(match_id, puuid):
    """Get detailed match information"""
    url = f"{ACCOUNT_BASE}/val/match/v1/matches/{match_id}"
    response = safe_request(url, HEADERS)
    
    if response and response.status_code == 200:
        data = response.json()
        
        # Find player in match
        players = data.get('players', [])
        player_data = next((p for p in players if p['puuid'] == puuid), None)
        
        if player_data:
            agent = player_data.get('character', 'Unknown')
            team = player_data.get('teamId', '').lower()
            
            # Get teams
            teams = data.get('teams', [])
            team_data = next((t for t in teams if t['teamId'].lower() == team), {})
            
            # Score
            team_score = team_data.get('roundsWon', 0)
            opp_team = next((t for t in teams if t['teamId'].lower() != team), {})
            opp_score = opp_team.get('roundsWon', 0)
            
            # Result
            result = "Win" if team_data.get('won', False) else "Loss"
            result_symbol = "✅" if result == "Win" else "❌"
            
            # Stats
            stats = player_data.get('stats', {})
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            
            print(f"   Agent: {agent} {result_symbol}")
            print(f"   Score: {team_score}-{opp_score} ({result})")
            print(f"   K/D/A: {kills}/{deaths}/{assists}")
            print(f"   Map: {data.get('matchInfo', {}).get('mapId', 'Unknown')}")
        
        return data
    return None

def get_current_rank(puuid):
    """Attempt to get rank info (works only for current act)"""
    print(f"\n🏆 Checking rank information...")
    
    # First, get current act ID from content API
    content_url = f"{VALORANT_BASE}/val/content/v1/contents"
    content_resp = safe_request(content_url, HEADERS)
    
    act_id = None
    if content_resp and content_resp.status_code == 200:
        content = content_resp.json()
        # Find current act (this requires parsing the acts array)
        acts = content.get('acts', [])
        for act in acts:
            if act.get('isActive', False):
                act_id = act.get('id')
                act_name = act.get('name', 'Current Act')
                print(f"   Current Act: {act_name}")
                break
    
    if act_id:
        # Try to get rank from ranked API
        rank_url = f"{VALORANT_BASE}/val/ranked/v1/leaderboards/by-act/{act_id}?puuid={puuid}"
        rank_resp = safe_request(rank_url, HEADERS)
        
        if rank_resp and rank_resp.status_code == 200:
            data = rank_resp.json()
            if data.get('players'):
                player = next((p for p in data['players'] if p['puuid'] == puuid), None)
                if player:
                    tier = player.get('rankedTier', 'Unranked')
                    rr = player.get('rankedRating', 0)
                    wins = player.get('numberOfWins', 0)
                    
                    # Convert tier number to rank name
                    ranks = {
                        3: 'Iron', 4: 'Bronze', 5: 'Silver',
                        6: 'Gold', 7: 'Platinum', 8: 'Diamond',
                        9: 'Ascendant', 10: 'Immortal', 24: 'Radiant'
                    }
                    
                    rank_name = ranks.get(tier, f'Tier {tier}')
                    print(f"   Rank: {rank_name} {rr} RR")
                    print(f"   Wins: {wins}")
                    return player
    
    print("   ⚠️  Rank data limited (only shows for Immortal+ on leaderboard)")
    print("   In-game rank with RR is not available via API")
    return None

def display_summary():
    """Display what data IS available via API"""
    print("\n" + "=" * 60)
    print("📋 WHAT THE VALORANT API CAN SHOW YOU:")
    print("=" * 60)
    print("✅ Available via API:")
    print("   • Match history (last 5+ matches)")
    print("   • K/D/A and performance stats")
    print("   • Agents played")
    print("   • Maps and game modes")
    print("   • Match results (win/loss)")
    print("   • Current Act information")
    print("   • Leaderboards (Immortal/Radiant only)")
    
    print("\n❌ NOT Available via API:")
    print("   • Exact RR (Rank Rating) number")
    print("   • RR gains/losses per match")
    print("   • MMR (Match Making Rating)")
    print("   • Rank progress percentage")
    print("   • Friend lists")
    print("   • Skin inventory")
    print("=" * 60)

def main():
    print("\n" + "=" * 60)
    print("🎯 VALORANT PLAYER INFO FETCHER")
    print("=" * 60)
    
    # Test API key first
    test_url = f"{ACCOUNT_BASE}/riot/account/v1/accounts/by-riot-id/riot/1"
    test_resp = safe_request(test_url, HEADERS)
    
    if test_resp and test_resp.status_code == 403:
        print("❌ INVALID API KEY DETECTED!")
        print("\nThis key 'RGAPI-...' is an EXAMPLE key from Riot's documentation.")
        print("It will not work for real API calls.")
        print("\n🔑 To get a REAL API key:")
        print("1. Go to: https://developer.riotgames.com/")
        print("2. Log in with your Riot account")
        print("3. Click 'Register' for a new API key")
        print("4. Copy that key and replace the API_KEY variable")
        print("=" * 60)
        return
    
    # Get player PUUID
    puuid = get_player_puuid(GAME_NAME, TAG_LINE)
    
    if puuid:
        # Get match history
        matches = get_match_history(puuid, count=3)
        
        # Try to get rank info
        rank_info = get_current_rank(puuid)
        
        # Display API capabilities
        display_summary()
        
        print("\n✅ Script completed!")
        print(f"\n💡 Tip: To see RR data, you must:")
        print("   1. Play the game and check post-match screens")
        print("   2. Use tracker sites for estimates (not exact RR)")
        print("   3. Accept that RR is intentionally hidden by Riot")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Clear screen for better display
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Run main function
    main()
