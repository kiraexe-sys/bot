from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "kira_verify"

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    return "ok"

app.run(host="0.0.0.0", port=5000)
