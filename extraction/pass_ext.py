import re

def extract_passport_info(text, image_path, output_folder, csv_path):
    info = {
        "Document Type": "passport",
        "Name": None,
        "Date of Birth": None,
        "Document Number": None,
        "Image Path": image_path
    }

    lines = text.split('\n')

    passport_match = re.search(r'\b[A-Z]{1}-?\d{7}\b', text)

    name, dob = None, None
    for i, line in enumerate(lines):
        lower_line = line.lower()
        if 'name' in lower_line and i + 1 < len(lines):
            name = lines[i + 1].strip()
        if 'date of birth' in lower_line and i + 1 < len(lines):
            dob_match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[i + 1])
            if dob_match:
                dob = dob_match.group(1)

    info.update({
        "Document Number": passport_match.group(0) if passport_match else None,
        "Date of Birth": dob,
        "Name": name
    })

    # Process image cropping (if required)

    return info
