from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

COMMAND_DIR = "./mt4_commands"
os.makedirs(COMMAND_DIR, exist_ok=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        symbol = data["symbol"]
        action = data["action"].lower()
        lot = str(data.get("lot", 0.1))
        sl = data.get("sl")
        tp = data.get("tp")

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

@app.route("/")
def home():
    return "✅ TradingView to MT4 Webhook Bridge is Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
