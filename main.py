from flask import Flask, render_template, request
import requests
import base64
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Show chart for a ticker
@app.route("/chart")
def chart():
    ticker = request.args.get("ticker", "KXNFLGAME-2025PHI")
    
    # Example fake candle data — replace with Kalshi API later
    prices = [40, 45, 60, 55, 70, 65]

    # Generate chart
    fig, ax = plt.subplots()
    ax.plot(prices)
    ax.set_title(f"Candles for {ticker}")

    # Convert chart to base64
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    chart_url = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()

    return render_template("chart.html", ticker=ticker, chart_url=chart_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
