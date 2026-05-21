import os
from flask import Flask, request, send_file
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr # 新增：語音轉文字

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/ask', methods=['POST'])
def ask_gemini():
    try:
        # 🌟 修正：接收來自 ESP32 的檔案 (multipart/form-data)
        audio_file = request.files['audio']
        audio_path = "/tmp/input.wav"
        audio_file.save(audio_path)
        
        # 1. 語音轉文字 (STT)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data, language="zh-TW")
        
        print(f"📥 辨識到的文字: {user_text}")
        
        # 2. Gemini 生成回應
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(user_text)
        reply_text = response.text
        
        # 3. 合成語音 (TTS)
        tts = gTTS(text=reply_text, lang='zh-tw')
        output_path = "/tmp/output.mp3"
        tts.save(output_path)
        
        return send_file(output_path, mimetype="audio/mp3")
        
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
