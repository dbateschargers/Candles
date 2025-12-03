from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime, timezone

app = Flask(__name__)

KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")

# ---------------------------------------------------------
# FETCH ALL SPORTS MARKETS FOR TODAY
# ---------------------------------------------------------
def get_todays_games():
    url = "https://api.kalshi.com/trade-api/v2/markets"
    headers = {"Authorization": f"Bearer {KALSHI_API_KEY}"}

    resp = requests.get(url, headers=headers).json()
    markets = resp.get("markets", [])

    today = datetime.now(timezone.utc).date()
    sports = []

    for m in markets:
        ticker = m["ticker"]

        # Only keep sports tickers
        if not any(x in ticker.upper() for x in ["NFL", "NBA", "NCAAF", "NCAAB"]):
            continue

        # Convert close time
        close_ts = datetime.fromtimestamp(m["close_time"], timezone.utc).date()
        if close_ts != today:
            continue

        # Build display name (example: "PHI vs DAL")
        name = m.get("title", ticker)

        sports.append({
            "ticker": ticker,
            "name": name
        })

    return sports

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/")
def home():
    games = get_todays_games()
    return render_template("index.html", games=games)

@app.route("/chart")
def chart():
    ticker = request.args.get("ticker")
    return render_template("chart.html", ticker=ticker)

@app.route("/api/candles")
def get_candles():
    ticker = request.args.get("ticker")

    url = f"https://api.kalshi.com/trade-api/v2/markets/{ticker}/candles?interval=1m"
    headers = {"Authorization": f"Bearer {KALSHI_API_KEY}"}

    resp = requests.get(url, headers=headers).json()
    candles_raw = resp.get("candles", [])

    candles = []
    for c in candles_raw:
        candles.append({
            "time": c["start_time"],
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
            "close": c["close"]
        })

    return jsonify(candles)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
