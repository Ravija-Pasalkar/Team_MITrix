import cv2
import numpy as np
from difflib import SequenceMatcher
from skimage.metrics import structural_similarity as ssim
from pyzbar.pyzbar import decode
import os

# ---------- CONFIG ----------
REAL_DIR = "real_aadhar_images"
FAKE_IMAGE_PATH = "test2.jpg"

def extract_text(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    qr_text, _, _ = cv2.QRCodeDetector().detectAndDecode(gray)
    return qr_text or "No QR Text"

def get_text_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def calculate_ssim(img1_path, img2_path):
    img1 = cv2.imread(img1_path, 0)
    img2 = cv2.imread(img2_path, 0)
    img1 = cv2.resize(img1, (500, 300))
    img2 = cv2.resize(img2, (500, 300))
    score, _ = ssim(img1, img2, full=True)
    return score

def orb_keypoint_match(img1_path, img2_path):
    img1 = cv2.imread(img1_path, 0)
    img2 = cv2.imread(img2_path, 0)
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    if des1 is None or des2 is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches) / max(len(kp1), 1)  # normalize over number of keypoints

def histogram_similarity(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    img1_hist = cv2.calcHist([img1], [0], None, [256], [0,256])
    img2_hist = cv2.calcHist([img2], [0], None, [256], [0,256])
    similarity = cv2.compareHist(img1_hist, img2_hist, cv2.HISTCMP_CORREL)
    return similarity

def qr_code_match(img_path):
    img = cv2.imread(img_path)
    qr_codes = decode(img)
    if qr_codes:
        return qr_codes[0].data.decode('utf-8')
    return "No QR Text"

# ---------- EVALUATION ----------
print("🔍 Evaluating Aadhaar Verification...\n")

fake_qr = qr_code_match(FAKE_IMAGE_PATH)
fake_text = extract_text(FAKE_IMAGE_PATH)

text_sims, ssim_scores, kp_scores, hist_sims, qr_matches = [], [], [], [], []

for file in os.listdir(REAL_DIR):
    if file.lower().endswith((".jpg", ".png", ".jpeg")):
        real_path = os.path.join(REAL_DIR, file)
        real_qr = qr_code_match(real_path)
        real_text = extract_text(real_path)

        text_sims.append(get_text_similarity(real_text, fake_text))
        ssim_scores.append(calculate_ssim(real_path, FAKE_IMAGE_PATH))
        kp_scores.append(orb_keypoint_match(real_path, FAKE_IMAGE_PATH))
        hist_sims.append(histogram_similarity(real_path, FAKE_IMAGE_PATH))
        qr_matches.append(1 if fake_qr == real_qr and fake_qr != "No QR Text" else 0)

# ---------- VOTE LOGIC ----------
# Average scores
avg_text_sim = np.mean(text_sims)
avg_ssim = np.mean(ssim_scores)
avg_kp = np.mean(kp_scores)
avg_hist_sim = np.mean(hist_sims)
avg_qr_match = np.mean(qr_matches)

# Adjusted Thresholds — slightly relaxed
thresholds = {
    "text_sim": 0.70,       # was 0.75
    "ssim": 0.70,           # was 0.75
    "kp": 0.12,             # was 0.15
    "hist_sim": 0.85,       # was 0.90
    "qr_match": 0.7         # was 0.8
}

# Weighted importance (out of 1.0)
weights = {
    "Text Match": 0.3,
    "Visual SSIM": 0.35,
    "Keypoint Match": 0.15,
    "Histogram Match": 0.1,
    "QR Match": 0.1
}

# Voting result (as before)
votes = {
    "Text Match": avg_text_sim >= thresholds["text_sim"],
    "Visual SSIM": avg_ssim >= thresholds["ssim"],
    "Keypoint Match": avg_kp >= thresholds["kp"],
    "Histogram Match": avg_hist_sim >= thresholds["hist_sim"],
    "QR Match": avg_qr_match >= thresholds["qr_match"]
}

# Weighted Vote Score
final_score = sum(weights[key] for key, passed in votes.items() if passed)

# Decision threshold: balanced around 0.6 (60% of total weight needed)
final_decision = "REAL" if final_score >= 0.6 else "FAKE"

# ---------- RESULT ----------
print("📝 Average Scores:")
print(f" - Text Similarity: {avg_text_sim:.2f}")
print(f" - Visual SSIM:     {avg_ssim:.2f}")
print(f" - Keypoint Match:  {avg_kp:.2f}")
print(f" - Histogram Match: {avg_hist_sim:.2f}")
print(f" - QR Code Match:   {avg_qr_match:.2f}")

print("\n📊 Voting Results:")
for k, v in votes.items():
    print(f" - {k}: {'✅' if v else '❌'}")

"""print(f"\n⚖️ Final Weighted Score: {final_score:.2f}")
print(f"✅ Final Decision: {final_decision}")
"""