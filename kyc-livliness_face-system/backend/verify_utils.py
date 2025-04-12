import subprocess
import whisper
import cv2
from deepface import DeepFace
import difflib
import os

def extract_audio(video_path, audio_path):
    subprocess.call(['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', audio_path])

def extract_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    mid_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    ret, frame = cap.read()
    frame_path = video_path.replace('.webm', '.jpg')
    if ret:
        cv2.imwrite(frame_path, frame)
    cap.release()
    return frame_path

def compare_texts(transcribed, expected):
    ratio = difflib.SequenceMatcher(None, transcribed.lower(), expected.lower()).ratio()
    return ratio

def process_video_and_verify(video_path, doc_path, challenge_text):
    audio_path = video_path.replace('.webm', '.wav')
    extract_audio(video_path, audio_path)

    model = whisper.load_model("medium")
    result = model.transcribe(audio_path)
    spoken_text = result['text']

    print("\n--- 🔍 Speech-to-Text Debug ---")
    print("🎯 Expected:", challenge_text)
    print("🗣️ Transcribed:", spoken_text)
    print("----------------------------------\n")

    sim_score = compare_texts(spoken_text, challenge_text)
    if sim_score < 0.9:
        return { "verified": False, "reason": f"Liveness failed. Similarity: {sim_score:.2f}" }

    face_frame = extract_frame(video_path)
    try:
        match = DeepFace.verify(img1_path=doc_path, img2_path=face_frame, model_name="ArcFace")
        return { "verified": match["verified"], "reason": "Face match passed" if match["verified"] else "Face mismatch" }
    except Exception as e:
        return { "verified": False, "reason": str(e) }
