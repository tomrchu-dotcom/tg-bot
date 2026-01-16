import os, requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# 讀取你在 Render 設定的環境變數
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 配置 Google AI
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(user_text):
    try:
        # 1. 先抓取你帳號目前可用的模型清單
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. 優先找 flash 系列，沒找到就用清單第一個
        target_model = next((m for m in available_models if 'flash' in m), available_models[0])
        
        # 3. 定義模型並注入「25歲女孩」的個性指令
        model = genai.GenerativeModel(
            model_name=target_model,
            system_instruction="""
            你現在是一位 25 歲的台灣女生，個性溫柔、活潑且充滿正能量。
            你的說話風格：
            1. 語氣親切自然，像是在跟好朋友聊天，要讓對方感到放鬆。
            2. 經常使用「～」、「喔」、「吧」、「呀」、「呢」等語助詞。
            3. 遇到使用者有困難或挫折時，會先溫柔地說「辛苦了」或是給予鼓勵，再提供建議。
            4. 訊息中會適度加入 😊、✨、💪、💖 等表情符號。
            5. 稱呼使用者為「你」或「親愛的」，不要太嚴肅喔！
            """
        )
        
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        return f"哎呀，連線好像有點小情緒... 晚點再試試看好嗎？（錯誤訊息：{str(e)}）"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if data and "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            
            # 取得充滿正能量的回覆
            reply = get_ai_response(user_text)
            
            # 傳回給 Telegram
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )
    except:
        pass
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI 少女機器人正在運行中喔！✨"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
