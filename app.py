from flask import Flask, request
import requests
import google.generativeai as genai

# ================== CONFIG ==================
PAGE_ACCESS_TOKEN = "EAATeTyxX2KcBQAs0qfrl3VLN3xbgqQdK987r1TvDrQm3ZBH2c6FZCxb51xKge4Bg07LOq9fpljm4ZCdVtFz204f6lhBkvqZB4DEMVASx8fgAQxYqCpvvbHhGyDAE1ry9h7jyKMFPxeqxD5wt5mQuZB9AJ3kPegXPZBMZCL2m1Rfq39005r4ZAED78PRRFDup23ZA5zl2jUBcr"
VERIFY_TOKEN = "verify123"
GEMINI_API_KEY = "AIzaSyCptRQ1Ypm4-Echi0WXFlZ2mSeqAlITlYA"
# ============================================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")



app = Flask(__name__)

# ================== WEBHOOK VERIFY ==================
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid token"

# ================== RECEIVE MESSAGE ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            if "message" in event and "text" in event["message"]:
                psid = event["sender"]["id"]
                text = event["message"]["text"]

                ai_reply = ask_gemini(text)
                send_message(psid, ai_reply)

    return "ok", 200

# ================== GEMINI ==================
def ask_gemini(text):
    try:
        response = model.generate_content(text)
        print("GEMINI RAW RESPONSE:", response)

        if response and hasattr(response, "text") and response.text:
            return response.text
        else:
            return "⚠️ Gemini رجّع جواب فارغ"
    except Exception as e:
        print("❌ GEMINI ERROR:", e)
        return "❌ Gemini ما خدمش (شوف Terminal)"

# ================== SEND MESSAGE ==================
def send_message(psid, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, params=params, json=payload)

# ================== RUN ==================
if __name__ == "__main__":
    app.run(port=5000)
