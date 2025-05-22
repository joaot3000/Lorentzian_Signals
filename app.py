from flask import Flask, request, jsonify

app = Flask(__name__)

# Stores the latest trade command from TradingView
latest_command = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    global latest_command
    data = request.json

    # Make sure all required fields are present
    if not data or not all(k in data for k in ["symbol", "action", "lot"]):
        return jsonify({"error": "Missing fields"}), 400

    latest_command = data
    print("Received command:", latest_command)
    return jsonify({"status": "received"})

@app.route("/get_command", methods=["GET"])
def get_command():
    global latest_command
    if latest_command:
        return jsonify(latest_command)
    else:
        return jsonify({"status": "no_command"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
