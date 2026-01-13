import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 1. 從環境變數讀取金鑰
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 2. 配置 Google AI (確保連線到最新 API)
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(user_text):
    """
    嘗試多種模型路徑，確保避開 404 錯誤
    """
    # 根據你 Playground 的成功經驗，優先使用 flash 系列
    # 加入 'models/' 前綴是為了強制修正部分環境下的路徑問題
    model_list = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-flash-8b',
        'gemini-1.5-flash',
        'gemini-pro'
    ]
    
    for model_name in model_list:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            response = model.generate_content(user_text)
            return response.text
        except Exception as e:
            print(f"嘗試模型 {model_name} 失敗: {e}")
            continue
            
    return "AI 目前無法回應，請確認 Google AI Studio 權限已開通。"

def send_message(chat_id, text):
    """將訊息傳回給 Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"傳送訊息至 Telegram 失敗: {e}")

@app.route("/", methods=["POST"])
def webhook():
    """處理來自 Telegram 的訊息"""
    try:
        data = request.get_json()
        if data and "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            
            # 取得 AI 回覆
            reply = get_ai_response(user_text)
            
            # 回傳訊息
            send_message(chat_id, reply)
    except Exception as e:
        print(f"Webhook 處理出錯: {e}")
        
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "<h1>AI Bot is Live!</h1><p>Your service is running and ready for Telegram messages.</p>"

if __name__ == "__main__":
    # Render 會自動提供 PORT 環境變數
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
