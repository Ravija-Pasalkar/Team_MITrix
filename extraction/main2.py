import os
import pandas as pd
from google.cloud import vision
from pan_ext import extract_pan_info
from driving_ext import extract_driving_license_info
from pass_ext import extract_passport_info

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

        if doc_type.lower() == "pan":
            extracted_info = extract_pan_info(text, image_path, output_folder, csv_path)
        elif doc_type.lower() == "driving license":
            extracted_info = extract_driving_license_info(text, image_path, output_folder, csv_path)
        elif doc_type.lower() == "passport":
            extracted_info = extract_passport_info(text, image_path, output_folder, csv_path)
        
        results.append(extracted_info)

    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False)
    print(f"Extraction completed! Data saved to '{csv_path}'.")

if __name__ == "__main__":
    main()
