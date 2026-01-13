import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 從環境變數讀取金鑰
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 設定 Gemini (使用 1.5-flash 版本)
genai.configure(api_key=GEMINI_API_KEY)

# 建立模型並關閉過濾器，確保 AI 一定會回話
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
)

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
            
            try:
                # 啟動對話
                response = model.generate_content(user_text)
                reply_text = response.text
            except Exception as e:
                # 如果 API 報錯，直接把錯誤訊息傳給你的 Telegram，方便除錯
                reply_text = f"Gemini 報錯了：{str(e)}"

            send_message(chat_id, reply_text)
    except Exception as e:
        print(f"系統錯誤: {e}")
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI Bot is Online!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
