import os
from flask import Flask, request, send_file
import google.generativeai as genai
from gtts import gTTS

app = Flask(__name__)

# 1. 初始化 Gemini 金鑰
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/ask', methods=['POST'])
def ask_gemini():
    try:
        data = request.get_json()
        user_text = data.get('text', '')
        print(f"📥 收到來自 ESP32 的文字請求: {user_text}")
        
        # 🌟 核心修正：與時俱進！使用網路上最新的 2.5 版 Flash 模型
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 讓最新大腦生成回應
        response = model.generate_content(user_text)
        reply_text = response.text
        print(f"🤖 Gemini 2.5 回應: {reply_text}")
        
        # 轉成繁體中文語音檔
        tts = gTTS(text=reply_text, lang='zh-tw')
        output_path = "/tmp/output.mp3"
        tts.save(output_path)
        
        return send_file(output_path, mimetype="audio/mp3")
        
    except Exception as e:
        print(f"❌ 後端發生錯誤: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
