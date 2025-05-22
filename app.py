from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

COMMAND_DIR = "./mt4_commands"
os.makedirs(COMMAND_DIR, exist_ok=True)

# Define pip sizes for common pairs — you can expand this list
PIP_SIZES = {
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "USDJPY": 0.01,
    # add more symbols/pip sizes as needed
}

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        symbol = data["symbol"]
        action = data["action"].lower()
        lot = float(data.get("lot", 0.1))
        sl_pips = data.get("sl_pips")
        tp_pips = data.get("tp_pips")

        # Check pip size for symbol
        pip = PIP_SIZES.get(symbol, 0.0001)  # default 0.0001 if unknown

        # Assume price from webhook or use a default (better to fetch live price in production)
        # Here we simulate: For buy, current price = 1.1000, sell price = 1.1000 (replace with actual data source)
        current_price = 1.1000

        # Calculate SL and TP prices
        if sl_pips is not None:
            sl = current_price - sl_pips * pip if action == "buy" else current_price + sl_pips * pip
        else:
            sl = None
        if tp_pips is not None:
            tp = current_price + tp_pips * pip if action == "buy" else current_price - tp_pips * pip
        else:
            tp = None

        if action not in ["buy", "sell"]:
            return jsonify({"error": "Invalid action"}), 400

        filename = f"{COMMAND_DIR}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol}_{action}.txt"
        command = {
            "symbol": symbol,
            "action": action,
            "lot": lot,
            "sl": sl,
            "tp": tp
        }

        with open(filename, "w") as f:
            f.write(json.dumps(command))

        return jsonify({"status": "Command saved", "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
