from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chart")
def chart():
    ticker = request.args.get("ticker")
    return render_template("chart.html", ticker=ticker)

@app.route("/api/candles")
def get_candles():
    ticker = request.args.get("ticker")

    url = f"https://api.kalshi.com/trade-api/v2/markets/{ticker}/candles?interval=1m"
    headers = { "Authorization": f"Bearer {KALSHI_API_KEY}" }

    resp = requests.get(url, headers=headers)
    data = resp.json()

    # Convert Kalshi candles → TradingView format
    candles = []
    for c in data.get("candles", []):
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
