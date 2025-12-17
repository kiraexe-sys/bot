from flask import Flask, request
import requests
import google.generativeai as genai
import datetime

# ================== CONFIG ==================
PAGE_ACCESS_TOKEN = "EAATeTyxX2KcBQAs0qfrl3VLN3xbgqQdK987r1TvDrQm3ZBH2c6FZCxb51xKge4Bg07LOq9fpljm4ZCdVtFz204f6lhBkvqZB4DEMVASx8fgAQxYqCpvvbHhGyDAE1ry9h7jyKMFPxeqxD5wt5mQuZB9AJ3kPegXPZBMZCL2m1Rfq39005r4ZAED78PRRFDup23ZA5zl2jUBcr"
VERIFY_TOKEN = "kira_verify"
GEMINI_API_KEY = "AIzaSyDTP_DpC3BrOxV1vu99kQgtWxYHx0JUJZY"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

app = Flask(__name__)

# ================== EMPLOI ==================
EMPLOI_TEXT = """
المستوى: الأولى علوم 2

الإثنين:
09:00-11:00 الفيزياء (LABO SVT2)
11:00-13:00 علوم الحياة والأرض (LABO SVT1)
16:00-17:00 العربية (القاعة 1)
17:00-18:00 الاجتماعيات (القاعة 2)
18:00-19:00 التربية الإسلامية (القاعة 2)

الثلاثاء:
10:00-11:00 الفرنسية (القاعة 8)
11:00-12:00 الإنجليزية (القاعة 2)
15:00-16:00 الاجتماعيات (LABO SVT2)

الأربعاء:
11:00-13:00 الرياضيات (القاعة 10)
15:00-16:00 الفرنسية (القاعة 13)
16:00-17:00 التربية الإسلامية (القاعة 10)

الخميس:
09:00-11:00 الفيزياء (LABO PC2)
15:00-16:00 الفرنسية (القاعة 13)

الجمعة:
09:00-10:00 العربية (القاعة 10)
10:00-11:00 الفرنسية (القاعة 1)

السبت:
15:00-16:00 الرياضيات (القاعة 10)
"""

# ================== PROMPT ==================
SYSTEM_PROMPT = f"""
نتا صاحب ديال المستخدم، كتجاوب معاه بالدارجة المغربية وبطريقة خفيفة.

القواعد:
- جاوب بحال صحابك كيهضرو.
- ما تطوّلش، جملة ولا جوج كافيين.
- استعمل "عندك" و"ديال" و"من … حتى …".
- إلا تسوّل على نهار، عطِ غير داك النهار.
- إلا قال "الصباح" → 09:00 حتى 13:00
- إلا قال "العشية" → 15:00 حتى 19:00
- ما تزيد حتى مادة ما كايناش.
- إلا تسوّل المستخدم على "اليوم"، راه المقصود هو نهار اليوم الحقيقي.
- ما تسولش المستخدم شنو هو النهار.
- إلا ما كانش عندو دروس، قول ليه "ما عندك والو".
- إلى بغى يعرف جميع الدروس ديالو، عطِه جميع الدروس.
ها هو
ila swlk 3la xi haja dyal l9raya bhal xi exercic wla chi mawdo3 dyal l9raya jawbo jawab shih o b oslob dyal xi wahd 3nddo niveau 1bac


الemploi:
{EMPLOI_TEXT}

أمثلة ديال الجواب:
- عندك 2h ديال الماط من 11 حتى 1
- الصباح عندك غير الفيزياء من 9 حتى 11
- ما عندك والو فالعشية


جاوب دابا على السؤال.
"""

def today_name_ar():
    days = {
        "Monday": "الاثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الأحد"
    }
    today_en = datetime.datetime.now().strftime("%A")
    return days.get(today_en, "")

# ================== GEMINI ==================
def ask_gemini(user_text):
    try:
        today = today_name_ar()

        # إلى قال "اليوم" بوحدها
        if "اليوم" in user_text:
            user_text = f"شنو عندي {today}؟"

        prompt = SYSTEM_PROMPT + "\n\nالسؤال: " + user_text
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("GEMINI ERROR:", e)
        return "وقع مشكل فـ الذكاء الاصطناعي 😅"

# ================== FB SEND ==================
def send_message(user_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# ================== WEBHOOK ==================
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    for entry in data.get("entry", []):
        for msg in entry.get("messaging", []):
            if "message" in msg and "text" in msg["message"]:
                user_id = msg["sender"]["id"]
                text = msg["message"]["text"]

                if text.lower() in ["start", "hi", "hello"]:
                    send_message(user_id, "مرحبا 👋 سولني على emploi ديالك")
                else:
                    reply = ask_gemini(text)
                    send_message(user_id, reply)

    return "ok", 200

# ================== RUN ==================
if __name__ == "__main__":
    app.run(port=5000)
