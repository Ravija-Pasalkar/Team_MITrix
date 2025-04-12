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

def extract_info(text, doc_type, image_path, output_folder, csv_path):
    """Extract relevant information (Name, Date of Birth, Document Number) based on document type."""
    
    info = {
        "Document Type": doc_type,
        "Name": None,
        "Date of Birth": None,
        "Document Number": None,
        "Image Path": image_path
    }

    lines = text.split('\n')

    # PAN Card
    if doc_type.lower() == "pan":
        pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
        dob_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)

        name = None
        for i, line in enumerate(lines):
            if 'name' in line.lower():
                if i+1 < len(lines):
                    possible_name = lines[i+1].strip()
                    if re.match(r'^[A-Z\s]+$', possible_name):
                        name = possible_name

        info.update({
            "Document Number": pan_match.group(0) if pan_match else None,
            "Date of Birth": dob_match.group(1) if dob_match else None,
            "Name": name
        })

    # Driving License
    # Driving License
    elif doc_type.lower() == "driving license":
        dl_match = re.search(r'\b[A-Z]{2}\d{2} \d{11}\b', text)
        dob_match = None
        cov, doi, pin, address = None, None, None, None
        name = None

        for i, line in enumerate(lines):
            # DOB — assuming in DD-MM-YYYY
            if re.search(r'\d{2}-\d{2}-\d{4}', line):
                dob_match = re.search(r'(\d{2}-\d{2}-\d{4})', line)
                if dob_match:
                    dob_match = dob_match.group(1)
                    # After finding DOB, get the next line as Name
                    if i + 1 < len(lines):
                        name = lines[i + 1].strip()  # Name is on the line immediately after DOB

            # COV
            if 'COV' in line:
                if i + 1 < len(lines):
                    cov = lines[i + 1].strip()

            # DOI
            if 'DOI' in line:
                doi_match = re.search(r'(\d{2}-\d{2}-\d{4})', lines[i + 1]) if (i + 1) < len(lines) else None
                if doi_match:
                    doi = doi_match.group(1)

            # Address
            address_search = re.search(r'(?:Add|Address)\s*[:\-]?\s*(.*)', line, re.IGNORECASE)
            if address_search:
                address = address_search.group(1).strip()
                # Look ahead if it's split across lines
                if i + 1 < len(lines):
                    address += ' ' + lines[i + 1].strip()

            # PIN
            pin_search = re.search(r'\b\d{6}\b', line)
            if pin_search:
                pin = pin_search.group(0)

        info.update({
            "Document Number": dl_match.group(0) if dl_match else None,
            "Date of Birth": dob_match,
            "Name": name,
            "COV": cov,
            "DOI": doi,
            "PIN": pin,
            "Address": address,
            "Gender": "NA"
        })


    # Passport
    elif doc_type.lower() == "passport":
        passport_match = re.search(r'\b[A-Z]{1}-?\d{7}\b', text)

        name, dob = None, None

        for i, line in enumerate(lines):
            lower_line = line.lower()
            if 'name' in lower_line and i+1 < len(lines):
                name = lines[i+1].strip()
            if 'date of birth' in lower_line and i+1 < len(lines):
                dob_match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[i+1])
                if dob_match:
                    dob = dob_match.group(1)

        info.update({
            "Document Number": passport_match.group(0) if passport_match else None,
            "Date of Birth": dob,
            "Name": name
        })

    # Image Cropping (Face Detection)
    img = cv2.imread(image_path)
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Load OpenCV's pre-trained Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_img = img[y:y+h, x:x+w]

                person_folder = os.path.join(output_folder, info["Name"] if info["Name"] else "unidentified")
                os.makedirs(person_folder, exist_ok=True)

                cropped_image_path = os.path.join(person_folder, f"face_{os.path.basename(image_path)}")
                cv2.imwrite(cropped_image_path, face_img)

                info["Image Path"] = cropped_image_path
                break  # Save only the first detected face
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
        ("test_docs/pan_card.png", "pan"),
        ("test_docs/driving_license.png", "driving license"),
        ("test_docs/passport.jpg", "passport"),
    ]

    output_folder = "output_folder"  # Define output folder
    csv_path = "extracted_documents.csv"  # Define the CSV file path

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