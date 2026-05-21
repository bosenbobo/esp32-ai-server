import os
import google.generativeai as genai
from flask import Flask, request, send_file
from gtts import gTTS

app = Flask(__name__)

# 從環境變數讀取 API Key (部署在 Render 時，請記得在後台設定這個環境變數)
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@app.route('/ask', methods=['POST'])
def ask_ai():
    try:
        # ✨ 正確解析 ESP32 傳過來的 JSON 文字資料
        data = request.get_json()
        if not data:
            return {"error": "未收到有效的 JSON 資料"}, 400
            
        # 取得 ESP32 傳過來的文字（例如："有什麼需要服務" 或 "午安"）
        user_text = data.get("text", "")
        print(f"📥 收到來自 ESP32 的文字請求: {user_text}")
        
        if not user_text:
            return {"error": "請求中缺乏 text 欄位"}, 400

        # ✨ 加入嚴格的字數限制提示詞，防止語音檔太大導致 ESP32 下載超時當機
        prompt = f"請用繁體中文回答以下問題，語氣要溫暖自然，且字數『嚴格限制在 30 字以內』：{user_text}"
        
        # 2. 呼叫 Gemini 模型進行動態思考
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        ai_reply = response.text.strip()
        print(f"🤖 Gemini 生成的回應: {ai_reply}")
        
        # 3. 將 AI 動態生成的文字轉成語音檔 (繁體中文台灣音調)
        tts = gTTS(text=ai_reply, lang='zh-tw')
        tts.save("output.mp3")
        
        print("💾 語音轉檔完成，準備發送給 ESP32...")
        return send_file("output.mp3", mimetype="audio/mpeg")
        
    except Exception as e:
        print(f"❌ 後端發生錯誤: {str(e)}")
        return {"error": str(e)}, 500

# ✨ 新增首頁檢查路由：方便直接用瀏覽器點網址測試伺服器是否活著
@app.route('/', methods=['GET'])
def index():
    return {"status": "AI語音伺服器正完美運行中！大腦已成功解鎖！"}

# 🌟 修正重點：外放主機與通訊埠設定，讓 Render 雲端平台與 gunicorn 更好辨識與載入
host = '0.0.0.0'
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host=host, port=port)
