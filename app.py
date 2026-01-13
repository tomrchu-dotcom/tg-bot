import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 從環境變數讀取金鑰
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 強制設定 Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# 終極修正：直接使用內容生成功能，並加上錯誤捕捉
def get_ai_response(prompt):
    try:
        # 強制指定最新模型
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 啟動失敗，錯誤訊息：{str(e)}"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            
            # 呼叫 AI 回應
            reply_text = get_ai_response(user_text)
            
            # 回傳給 Telegram
            send_message(chat_id, reply_text)
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI Bot is Online!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
