from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os
import speech_recognition as sr
import cv2
import numpy as np
from deepface import DeepFace
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher
import tempfile
import uuid
import shutil
import subprocess
from google.generativeai import configure, GenerativeModel

# ==== Gemini API Key ====
configure(api_key='#####')  # Replace with your actual API key

# ==== Flask App Config ====
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==== Gemini Challenge Text Generator ====
def generate_challenge_from_language(language):
    model = GenerativeModel("gemini-2.0-flash")
    prompt = (
        f"Generate a short line of meaningful, creative, and fun text "
        f"in {language}. It should be suitable for a user to read aloud "
        f"during identity verification. Avoid any sensitive or complex content."
    )
    try:
        response = model.generate_content(prompt)
        challenge_text = response.text.strip().replace('\n', ' ')
        print(f"[🧠 Gemini Challenge Generated] Language: {language} | Text: {challenge_text}")
        return challenge_text
    except Exception as e:
        print(f"[❌ Gemini Error] {e}")
        return "Verification prompt unavailable. Please try again."

@app.route('/get-challenge')
def get_challenge():
    language = request.args.get('language', default='English')
    challenge = generate_challenge_from_language(language)
    return jsonify({'challenge': challenge})


# ==== Audio Extractor using FFmpeg ====
def extract_audio(video_path):
    audio_path = video_path.replace(".webm", ".wav")
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path, "-ab", "160k", "-ac", "1",
            "-ar", "48000", "-vn", audio_path, "-y"
        ], check=True)
        print(f"[🎙️ Audio Extracted] {audio_path}")
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"[❌ Audio Extraction Failed] {e}")
        return None


# ==== Speech Transcription ====
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        transcription = recognizer.recognize_google(audio)
        print(f"[🗣️ Transcription] {transcription}")
        return transcription
    except Exception as e:
        print(f"[❌ Transcription Error] {e}")
        return ""


# ==== Similarity ====
def similarity_score(a, b):
    score = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    print(f"[📏 Similarity Score] {score:.2f}")
    return score


# ==== Best Frame Extractor ====
def extract_best_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    best_frame = None
    max_faces = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            faces = DeepFace.extract_faces(frame, detector_backend='opencv', enforce_detection=False)
            if len(faces) > max_faces:
                best_frame = frame.copy()
                max_faces = len(faces)
        except Exception as e:
            print(f"[⚠️ Face Detection Error] {e}")
            continue
    cap.release()
    print(f"[📸 Best Frame Extracted] Faces Detected: {max_faces}")
    return best_frame


# ==== Main Verification Endpoint ====
@app.route('/verify', methods=['POST'])
def verify():
    challenge = request.form['challenge']
    video = request.files['video']
    doc_image = request.files['doc_image']

    temp_dir = tempfile.mkdtemp()
    try:
        video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.webm")
        doc_image_path = os.path.join(temp_dir, secure_filename(doc_image.filename))

        video.save(video_path)
        doc_image.save(doc_image_path)

        print(f"[📁 Files Saved] Video: {video_path}, Doc Image: {doc_image_path}")

        # === Extract and transcribe ===
        audio_path = extract_audio(video_path)
        if not audio_path:
            return jsonify({"message": "❌ Audio extraction failed"})

        spoken_text = transcribe_audio(audio_path)
        score = similarity_score(spoken_text, challenge)

        if score < 0.8:
            return jsonify({"message": f"❌ Failed: Liveness failed. Similarity: {score:.2f}"})

        # === Extract best frame and compare ===
        best_frame = extract_best_frame(video_path)
        if best_frame is None:
            return jsonify({"message": "❌ Failed: No face found in video"})

        temp_img = os.path.join(temp_dir, "frame.jpg")
        cv2.imwrite(temp_img, best_frame)

        print(f"[🔍 Face Matching Started] Comparing {temp_img} vs {doc_image_path}")
        try:
            result = DeepFace.verify(img1_path=temp_img, img2_path=doc_image_path, model_name='ArcFace')
        except Exception as e:
            return jsonify({"message": f"❌ Face matching error: {str(e)}"})

        if result["verified"]:
            print("[✅ Face Match] Identity Verified")
            return jsonify({"message": "✅ Verified Successfully!"})
        else:
            print("[❌ Face Mismatch] Faces did not match")
            return jsonify({"message": "❌ Failed: Face did not match"})

    finally:
        shutil.rmtree(temp_dir)
        print(f"[🧹 Temp Files Removed] {temp_dir}")


if __name__ == '__main__':
    app.run(debug=True)
