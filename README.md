# Team_MITrix
# AI-Powered Digital KYC System

A secure, intelligent, and automated digital Know Your Customer (KYC) solution that leverages AI for document tampering detection, liveness verification, and face matching — ensuring user identity authenticity while adhering to data protection regulations like GDPR and India's DPDP Act.

---

## Project Purpose

This system enables seamless, remote KYC verification by:

- Collecting user details and identity documents (Aadhaar + PAN/Passport)
- Verifying contact information via OTP
- Detecting forged/tampered documents using AI
- Performing liveness detection through voice + face from a dynamic spoken prompt
- Matching the user’s live face with the document image
- Ensuring data privacy compliance through user consent

Designed for industries like fintech, telecom, and government services, the platform reduces fraud while improving the customer onboarding experience.

---

## System Flow

1. User enters details and uploads identity documents  
2. OTP verification is performed on phone/email  
3. AI checks uploaded documents for forgery using OCR and image comparison  
4. A dynamic sentence is generated using **GenAI**, which the user must read aloud  
5. The system records video + audio and checks:
   - Whether the sentence was read correctly (via speech-to-text) to ensure liveliness
   - Whether the face in the video matches the document image 
6. User provides consent by checking GDPR/DPDP agreement boxes  
7. If all checks pass, KYC is approved