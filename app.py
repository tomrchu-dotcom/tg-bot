import os, requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_response(text):
    # 這裡列出目前所有可能的型號名稱，程式會一個一個試，直到成功為止
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',  # 這是你剛看到的那個
        'gemini-1.0-pro'
    ]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(text)
            return response.text
        except Exception:
            continue
    return "所有 AI 型號目前都無法連線，請檢查 API Key 權限。"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        reply_text = get_response(data["message"]["text"])
        
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply_text}
        )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
