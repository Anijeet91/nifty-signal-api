from flask import Flask, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com",
    "Connection": "keep-alive"
}

def get_nse_session():
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
    except Exception:
        pass
    return session

@app.route("/")
def home():
    return jsonify({"status": "NSE Signal API Running"})

@app.route("/price")
def get_price():
    try:
        session = get_nse_session()
        response = session.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", headers=HEADERS, timeout=10)
        data = response.json()
        spot = data["records"]["underlyingValue"]
        return jsonify({"symbol": "NIFTY", "price": spot})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/raw")
def get_raw():
    try:
        session = get_nse_session()
        response = session.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", headers=HEADERS, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/besttrade")
def get_best_trade():
    try:
        session = get_nse_session()
        response = session.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", headers=HEADERS, timeout=10)
        data = response.json()
        records = data["filtered"]["data"]
        spot = data["records"]["underlyingValue"]

        best = None
        max_vol = 0

        for row in records:
            for opt_type in ["CE", "PE"]:
                if opt_type in row:
                    option = row[opt_type]
                    vol = option.get("totalTradedVolume", 0)
                    ltp = option.get("lastPrice", 0)
                    strike = option.get("strikePrice", 0)

                    if ltp > 0.05 and vol > max_vol and abs(spot - strike) <= 200:
                        max_vol = vol
                        best = {
                            "symbol": "NIFTY",
                            "type": opt_type,
                            "strike": strike,
                            "ltp": round(ltp, 2),
                            "volume": vol
                        }

        if best:
            best["entry"] = best["ltp"]
            best["target"] = round(best["entry"] * 1.2, 2)
            best["sl"] = round(best["entry"] * 0.9, 2)
            return jsonify(best)
        else:
            return jsonify({"message": "No strong trade found. Indicators not aligned."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
