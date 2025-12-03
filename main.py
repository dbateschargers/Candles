from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

KALSHI_BASE = "https://api.kalshi.com/trade-api/v2"
SPORT_PREFIXES = ["NBA", "NFL", "CFB", "CBB"]


def get_markets():
    """Get all sports markets."""
    url = f"{KALSHI_BASE}/markets"
    r = requests.get(url).json()
    markets = []

    for m in r.get("markets", []):
        ticker = m.get("ticker", "")
        for prefix in SPORT_PREFIXES:
            if ticker.startswith(prefix):
                markets.append({
                    "ticker": ticker,
                    "title": m.get("title", ""),
                    "yes_bid": m.get("yes_bid"),
                    "no_bid": m.get("no_bid")
                })
                break

    return markets


def get_orderbook(ticker):
    url = f"{KALSHI_BASE}/markets/{ticker}/orderbook"
    r = requests.get(url).json()
    return r.get("orderbook", {})


def get_candles(ticker):
    """Build pseudo-candles from orderbook snapshots."""
    candles = []
    for _ in range(20):
        ob = get_orderbook(ticker)
        yes = ob.get("yes", [])
        no = ob.get("no", [])

        if yes:
            price = yes[0][0]
        elif no:
            price = 100 - no[0][0]
        else:
            price = None

        if price:
            candles.append(price)

        time.sleep(0.4)

    return candles


@app.route("/")
def index():
    markets = get_markets()
    return render_template("index.html", markets=markets)


@app.route("/chart")
def chart():
    ticker = request.args.get("ticker")
    return render_template("chart.html", ticker=ticker)


@app.route("/data")
def data():
    ticker = request.args.get("ticker")
    candles = get_candles(ticker)
    return jsonify({"ticker": ticker, "candles": candles})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
