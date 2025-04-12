import re

def extract_driving_license_info(text, image_path, output_folder, csv_path):
    info = {
        "Document Type": "driving license",
        "Name": None,
        "Date of Birth": None,
        "Document Number": None,
        "COV": None,
        "DOI": None,
        "PIN": None,
        "Address": None,
        "Image Path": image_path
    }

    lines = text.split('\n')

    dl_match = re.search(r'\b[A-Z]{2}\d{2} \d{11}\b', text)
    dob_match = None
    name = None
    for i, line in enumerate(lines):
        # Extract DOB, COV, DOI, and other fields...
        # (implementation from original code)

    info.update({
        "Document Number": dl_match.group(0) if dl_match else None,
        "Date of Birth": dob_match,
        "Name": name
        # Include other extracted fields
    })

    # Process image cropping (if required)

    return info
