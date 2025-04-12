import re

def extract_pan_info(text, image_path, output_folder, csv_path):
    info = {
        "Document Type": "pan",
        "Name": None,
        "Date of Birth": None,
        "Document Number": None,
        "Image Path": image_path
    }

    lines = text.split('\n')

    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    dob_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)

    name = None
    for i, line in enumerate(lines):
        if 'name' in line.lower():
            if i + 1 < len(lines):
                possible_name = lines[i + 1].strip()
                if re.match(r'^[A-Z\s]+$', possible_name):
                    name = possible_name

    info.update({
        "Document Number": pan_match.group(0) if pan_match else None,
        "Date of Birth": dob_match.group(1) if dob_match else None,
        "Name": name
    })

    # Process image cropping (if required)

    return info
