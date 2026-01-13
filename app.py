import os, requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(user_text):
    try:
        # 【核心修正】動態抓取你帳號目前「真正可用」的模型清單
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 優先尋找 flash 相關模型，如果沒有就用清單第一個
        target_model = next((m for m in available_models if 'flash' in m), available_models[0])
        
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        return f"連線異常，請檢查 Google AI Studio。錯誤碼：{str(e)}"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if data and "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            reply = get_ai_response(data["message"]["text"])
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": reply})
    except: pass
    return "OK", 200

@app.route("/", methods=["GET"])
def index(): return "Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
