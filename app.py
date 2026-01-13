import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 從環境變數讀取金鑰
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 配置 API
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(prompt):
    try:
        # 使用最穩定的模型調用方式，並加上安全設定
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash'
        )
        # 加入一個簡單的過濾處理
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 如果還是失敗，嘗試切換到另一個穩定模型
        try:
            model_alt = genai.GenerativeModel('gemini-1.5-pro')
            response = model_alt.generate_content(prompt)
            return response.text
        except:
            return f"AI 暫時無法回應，請檢查 API 權限或稍後再試。錯誤細節：{str(e)}"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        reply_text = get_ai_response(user_text)
        send_message(chat_id, reply_text)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI Bot is Online!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
