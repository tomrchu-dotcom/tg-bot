import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 從環境變數讀取金鑰
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 設定 Gemini
genai.configure(api_key=GEMINI_API_KEY)
# 這裡換成最新的 1.5 版本，並關閉所有過濾器
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
    """傳送訊息給 Telegram 使用者的函式"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    """接收 Telegram 傳來的訊息"""
    try:
        data = request.get_json()
        
        # 確認訊息格式正確 (有 message 也有 text)
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            
            try:
                # 呼叫 Gemini AI
                response = model.generate_content(user_text)
                reply_text = response.text
            except Exception as e:
                reply_text = "AI 目前有點忙碌，請稍後再試。"
                print(f"Gemini Error: {e}")

            # 回傳給使用者
            send_message(chat_id, reply_text)
            
    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

# 這是讓 Render 知道服務還活著的檢查點
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
