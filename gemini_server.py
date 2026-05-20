import os
import google.generativeai as genai
from flask import Flask, request, send_file
from gtts import gTTS

app = Flask(__name__)

# 從環境變數讀取 API Key (這是雲端部署的標準作法)
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@app.route('/ask', methods=['POST'])
def ask_ai():
    # 1. 取得 ESP32 傳來的錄音內容
    audio_data = request.data
    # 這裡你可以加上轉錄邏輯 (Speech-to-Text)，目前我們先簡化
    user_text = "1+1" # 假設這裡是辨識出的文字
    
    # 2. 呼叫 Gemini
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(user_text)
    
    # 3. 將回答轉成語音
    tts = gTTS(text=response.text, lang='zh-tw')
    tts.save("output.mp3")
    
    return send_file("output.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    # 雲端平台會自動分配 PORT，如果不指定則用 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
