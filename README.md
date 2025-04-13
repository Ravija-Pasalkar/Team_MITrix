# Team_MITrix
# AI-Powered Digital KYC System

A secure, intelligent, and automated digital Know Your Customer (KYC) solution that leverages AI for document tampering detection, liveness verification, and face matching — ensuring user identity authenticity while adhering to data protection regulations like GDPR and India's DPDP Act.

---

## Project Purpose

This system enables seamless, remote KYC verification by:

- Collecting user details and identity documents (Aadhaar + PAN/Passport)
- Detecting forged/tampered documents using AI
- Performing liveness detection through voice + face from a dynamic spoken prompt
- Matching the user’s live face with the document image
- Ensuring data privacy compliance through user consent

Designed for industries like fintech, telecom, and government services, the platform reduces fraud while improving the customer onboarding experience.

---

## System Flow

1. User enters details and uploads identity documents  
2. AI checks uploaded documents for forgery using OCR and image comparison  
3. A dynamic sentence is generated using **GenAI**, which the user must read aloud  
4. The system records video + audio and checks:
   - Whether the sentence was read correctly (via speech-to-text) to ensure liveliness
   - Whether the face in the video matches the document image 
5. User provides consent by checking GDPR/DPDP agreement boxes  
6. If all checks pass, KYC is approved

---

## Setup Instructions

### 1. **Clone the Repository**
    - git clone https://github.com/Ravija-Pasalkar/Team_MITrix.git
    - cd Team_MITrix

### 2. **Install Python Dependencies**
Ensure Python 3.8+ is installed. Then run:
    - pip install -r requirements.txt

### 3. **Set Up Gemini API (for GenAI features)**
    - Visit Google AI Studio
    - Generate your Gemini API key
    - Open app.py and paste your key like this:
        GEMINI_API_KEY = "your-api-key-here"
    - Note: The Gemini API key is not pushed to GitHub. You must manually add it where required.

### 4. ** Configure MySQL Database**
    - Log in to MySQL and create a database:
    - CREATE DATABASE kyc_verification;
    - Create a new user and grant permissions:
    - CREATE USER 'kyc_user'@'localhost' IDENTIFIED BY 'your_password';
    - GRANT ALL PRIVILEGES ON kyc_verification.* TO 'kyc_user'@'localhost';
    - FLUSH PRIVILEGES;
    - Update your DB credentials in config.py or the relevant backend file.

### 5. **Run the Flask Backend**
    - python app.py
    - Your backend should now be running at http://localhost:5000

### 6. **Launch the Frontend**
    - Open first.html in your browser using live server
    - Allow access to camera and microphone
    - Follow the flow for secure KYC verification

---

## Usage Guidelines

### For Users
    - Fill in details and upload Aadhaar + PAN/Passport
    - System verifies document authenticity
    - Read random sentence aloud for liveness check
    - Face is matched with document photo
    - Give consent to complete KYC

### For Admins
    - Access the portal 
    - Use GenAI to analyze data using plain English
    - Monitor the results
