from flask import Flask, request, jsonify
import opennsfw2 as n2
from PIL import Image
import io
import os
import tempfile
import cv2
import numpy as np

app = Flask(__name__)

# عتبة الكشف (0.0 - 1.0) - كلما ارتفع الرقم، أقل حساسية
NSFW_THRESHOLD = 0.6

@app.route('/')
def home():
    return """
    <h1>NSFW Detection API (محلي - 2025)</h1>
    <p>استخدم الـ endpoints:</p>
    <ul>
        <li>POST /detect/image - للصور</li>
        <li>POST /detect/video - للفيديوهات</li>
    </ul>
    <p>أرسل الملف في حقل 'file'</p>
    """

@app.route('/detect/image', methods=['POST'])
def detect_image():
    if 'file' not in request.files:
        return jsonify({"error": "لا يوجد ملف مرفوع"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "اسم الملف فارغ"}), 400
    
    try:
        # قراءة الصورة
        img_bytes = file.read()
        pil_image = Image.open(io.BytesIO(img_bytes))
        
        # الكشف
        probability = n2.predict_image(pil_image)
        is_nsfw = probability > NSFW_THRESHOLD
        
        return jsonify({
            "filename": file.filename,
            "nsfw_probability": round(probability, 4),
            "is_nsfw": is_nsfw,
            "threshold": NSFW_THRESHOLD,
            "message": "NSFW" if is_nsfw else "آمن (SFW)"
        })
    
    except Exception as e:
        return jsonify({"error": f"خطأ في معالجة الصورة: {str(e)}"}), 500

@app.route('/detect/video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return jsonify({"error": "لا يوجد ملف مرفوع"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "اسم الملف فارغ"}), 400
    
    try:
        # حفظ الفيديو مؤقتًا
        temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1])
        file.save(temp_path)
        
        # الكشف في الفيديو (فحص إطارات منتظمة)
        elapsed, probabilities = n2.predict_video_frames(temp_path, frame_interval=16)  # كل ~0.5 ثانية
        avg_probability = float(np.mean(probabilities)) if probabilities else 0.0
        is_nsfw = avg_probability > NSFW_THRESHOLD
        
        # حذف الملف المؤقت
        os.close(temp_fd)
        os.remove(temp_path)
        
        return jsonify({
            "filename": file.filename,
            "average_nsfw_probability": round(avg_probability, 4),
            "frames_analyzed": len(probabilities),
            "is_nsfw": is_nsfw,
            "threshold": NSFW_THRESHOLD,
            "message": "NSFW" if is_nsfw else "آمن (SFW)"
        })
    
    except Exception as e:
        return jsonify({"error": f"خطأ في معالجة الفيديو: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 NSFW Detection API يعمل الآن على http://127.0.0.1:5000")
    print("استخدم /detect/image أو /detect/video")
    app.run(host='0.0.0.0', port=5000, debug=True)