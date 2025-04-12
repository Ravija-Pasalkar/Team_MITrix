import os
import re
import pandas as pd
import cv2
import csv
from google.cloud import vision

# Set your credentials environment variable if not set externally
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "seminar-450006-6efd453f2271.json"

# Initialize the Vision API client
client = vision.ImageAnnotatorClient()


def perform_ocr(image_path):
    """Use Google Cloud Vision to perform OCR on the image."""
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return ""


def extract_name_full_aadhaar(lines, dob_line_index):
    """Extracts probable full name from a few lines above DOB line."""
    skip_keywords = ["government", "india", "authority", "unique", "identity", "republic", "card"]

    for j in range(max(0, dob_line_index - 4), dob_line_index):
        candidate = lines[j].strip()

        # Skip header lines
        if any(word in candidate.lower() for word in skip_keywords):
            continue

        # Allow alphabetic (incl. title case), 2–4 words
        if 2 <= len(candidate.split()) <= 4:
            cleaned = re.sub(r'[^a-zA-Z\s]', '', candidate).strip()
            if cleaned and all(w.isalpha() for w in cleaned.split()):
                return cleaned
    return None



def extract_info(text, doc_type, image_path, output_folder, csv_path):
    """Extract relevant information based on document type, crop image and save info."""
    info = {
        "Document Type": doc_type,
        "Name": None,
        "Date of Birth": None,
        "Gender": None,
        "Phone": None,
        "Address": None,
        "Document Number": None,
        "Image Path": image_path
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    if doc_type.lower() == "aadhaar":
        dob_match = re.search(r'DOB[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})', text, re.IGNORECASE)
        aadhar_match = re.search(r'\b(?:\d{4}\s\d{4}\s\d{4}|[xX]{4}\s\d{4}\s\d{4}|[xX]{4}\s[xX]{4}\s\d{4}|[xX]{4}\s[xX]{4}\s[xX]{4})\b', text)
        phone_match = re.search(r'\b[6-9]\d{9}\b', text)

        name, gender, address = None, None, []
        bottom_name_found = False

        for i, line in enumerate(lines):
            # Gender detection
            if re.search(r'\b(MALE|FEMALE|Male|Female)\b', line):
                gender = re.search(r'\b(MALE|FEMALE|Male|Female)\b', line).group(0).capitalize()

            # Address block detection
            if 'S/O' in line or 'C/O' in line:
                j = i + 1
                while j < len(lines):
                    address_line = lines[j]
                    if re.search(r'\b\d{6}\b', address_line) or re.search(r'\b[6-9]\d{9}\b', address_line):
                        address.append(address_line)
                        break
                    address.append(address_line)
                    j += 1

            # Fallback: bottom-left name detection
            if not name and i > len(lines) - 5:
                possible_name = re.sub(r'[^A-Z\s]', '', line)
                if possible_name and possible_name.replace(' ', '').isalpha() and not bottom_name_found:
                    name = possible_name.strip()
                    bottom_name_found = True

        # NEW: extract name based on DOB
        if dob_match:
            dob_value = dob_match.group(1)
            dob_line_index = next((i for i, line in enumerate(lines) if dob_value in line), None)
            if dob_line_index is not None:
                extracted_name = extract_name_full_aadhaar(lines, dob_line_index)
                if extracted_name:
                    name = extracted_name

        full_address = ' '.join(address) if address else None

        info.update({
            "Name": name,
            "Date of Birth": dob_match.group(1) if dob_match else None,
            "Gender": gender,
            "Phone": phone_match.group(0) if phone_match else None,
            "Address": full_address,
            "Document Number": aadhar_match.group(0) if aadhar_match else None
        })

    # Face cropping and image saving
    img = cv2.imread(image_path)
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_img = img[y:y + h, x:x + w]
                person_folder = os.path.join(output_folder, info["Name"] if info["Name"] else "unidentified")
                os.makedirs(person_folder, exist_ok=True)
                cropped_image_path = os.path.join(person_folder, f"face_{os.path.basename(image_path)}")
                cv2.imwrite(cropped_image_path, face_img)
                info["Image Path"] = cropped_image_path
                break
        else:
            print(f"No face detected in {image_path}")
            info["Image Path"] = "No face detected"

    # Append info to CSV
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=info.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(info)

    return info


def main():
    image_paths = [
        ("test_docs/x.png", "aadhaar"),
    ]

    output_folder = "output_folder"
    csv_path = "extracted_documents.csv"

    results = []

    for image_path, doc_type in image_paths:
        print(f"Processing {image_path} ({doc_type})...")
        text = perform_ocr(image_path)
        extracted_info = extract_info(text, doc_type, image_path, output_folder, csv_path)
        results.append(extracted_info)

    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False)
    print(f"Extraction completed! Data saved to '{csv_path}'.")


if __name__ == "__main__":
    main()
