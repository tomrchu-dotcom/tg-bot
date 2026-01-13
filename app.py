import os, requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 讀取環境變數
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 配置 Google AI
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(user_text):
    # 這裡我們使用你在網頁端測試成功的最新 flash 型號
    # 如果 1.5-flash 不行，它會自動嘗試 1.5-flash-8b
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(user_text)
            return response.text
        except Exception:
            continue
    return "AI 思考中，請稍後再試。"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            
            # 取得 AI 回覆
            reply = get_ai_response(user_text)
            
            # 回傳給 Telegram
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
