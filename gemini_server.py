import os
from flask import Flask, request, send_file
import google.generativeai as genai
from gtts import gTTS

app = Flask(__name__)

# 1. 初始化 Gemini 金鑰（從 Render 的 Environment 讀取）
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/ask', methods=['POST'])
def ask_gemini():
    try:
        # 接收來自 ESP32-S3 的 JSON 請求
        data = request.get_json()
        user_text = data.get('text', '')
        print(f"📥 收到來自 ESP32 的文字請求: {user_text}")
        
        # 🌟 修正：完全移除 1.5 系列，採用與 v1beta 完美相容的標準經典模型
        model = genai.GenerativeModel('gemini-pro')
        
        # 讓大腦思考並生成文字回應
        response = model.generate_content(user_text)
        reply_text = response.text
        print(f"🤖 Gemini 回應: {reply_text}")
        
        # 使用 gTTS 將文字轉換為繁體中文語音 (.mp3)
        tts = gTTS(text=reply_text, lang='zh-tw')
        
        # 🌟 安全修正：將音訊儲存在 Render 允許自由讀寫的 /tmp 暫存目錄下
        output_path = "/tmp/output.mp3"
        tts.save(output_path)
        
        # 將語音檔案發送回傳給 ESP32-S3
        return send_file(output_path, mimetype="audio/mp3")
        
    except Exception as e:
        print(f"❌ 後端發生錯誤: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    # 綁定 Render 指派的連接埠（Port），預設為 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
