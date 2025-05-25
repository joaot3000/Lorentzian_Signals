from flask import Flask, request, jsonify

app = Flask(__name__)

latest_command = None

@app.route("/webhook", methods=["POST"])
def webhook():
    global latest_command
    data = request.json

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

@app.route("/clear_command", methods=["POST"])
def clear_command():
    global latest_command
    latest_command = None
    print("Command cleared")
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
