# valorant_tournaments_app.py
import os, json, threading, webbrowser
from flask import Flask, request, redirect, session, render_template_string
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ====== CONFIG ======
CLIENT_ID = "<YOUR_RSO_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_RSO_CLIENT_SECRET>"
REDIRECT_URI = "http://localhost:5000/callback"
RIOT_REGIONS = ["americas", "europe", "asia"]
TOURNAMENT_DATA_FILE = "tournaments.json"
API_BASE = "https://ap.api.riotgames.com"  # default for AP region
PROD_API_KEY = "<YOUR_PRODUCTION_API_KEY>"  # never include in client code

# ====== TOURNAMENT DATA ======
if not os.path.exists(TOURNAMENT_DATA_FILE):
    json.dump({"tournaments":[]}, open(TOURNAMENT_DATA_FILE,"w"))

# ====== RSO LOGIN ======
@app.route("/login")
def login():
    auth_url = (
        f"https://auth.riotgames.com/authorize?"
        f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid+offline_access"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = "https://auth.riotgames.com/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    token_res = requests.post(token_url, data=data).json()
    session["access_token"] = token_res.get("access_token")
    return redirect("/dashboard")

# ====== PLAYER DASHBOARD ======
@app.route("/dashboard")
def dashboard():
    if "access_token" not in session:
        return redirect("/login")
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    account = {}
    for region in RIOT_REGIONS:
        try:
            res = requests.get(f"https://{region}.api.riotgames.com/riot/account/v1/accounts/me", headers=headers, timeout=5)
            if res.status_code == 200:
                account = res.json()
                break
        except:
            continue
    puuid = account.get("puuid")
    player_data = {"account": account, "rank": {}, "matches": {}, "tournaments":[]}
    if puuid:
        player_data["rank"] = requests.get(f"{API_BASE}/val/ranked/v1/players/{puuid}", headers={"X-Riot-Token":PROD_API_KEY}).json()
        player_data["matches"] = requests.get(f"{API_BASE}/val/match/v1/matchlists/by-puuid/{puuid}", headers={"X-Riot-Token":PROD_API_KEY}).json()
    # include tournaments user is registered for
    tournaments = json.load(open(TOURNAMENT_DATA_FILE))
    player_data["tournaments"] = tournaments.get("tournaments", [])
    return render_template_string("<html><head><title>Valorant Tournaments Dashboard</title></head><body><h2>Welcome {{account['gameName']}}</h2><pre>{{data}}</pre></body></html>", account=account, data=json.dumps(player_data, indent=4))

# ====== TOURNAMENT MANAGEMENT ======
@app.route("/tournaments/create", methods=["POST"])
def create_tournament():
    req = request.json
    tournaments = json.load(open(TOURNAMENT_DATA_FILE))
    tournaments["tournaments"].append(req)
    json.dump(tournaments, open(TOURNAMENT_DATA_FILE,"w"))
    return {"status":"created","tournament":req}

@app.route("/tournaments/list")
def list_tournaments():
    tournaments = json.load(open(TOURNAMENT_DATA_FILE))
    return {"tournaments": tournaments.get("tournaments",[])}

# ====== LEADERBOARD ======
@app.route("/leaderboard/<act_id>")
def leaderboard(act_id):
    lb = requests.get(f"{API_BASE}/val/ranked/v1/leaderboards/by-act/{act_id}", headers={"X-Riot-Token":PROD_API_KEY}).json()
    return lb

# ====== START SERVER ======
threading.Timer(1, lambda:webbrowser.open("http://127.0.0.1:5000/login")).start()
app.run(host="0.0.0.0", port=5000)
