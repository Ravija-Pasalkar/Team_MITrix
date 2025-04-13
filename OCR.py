import pytesseract
from PIL import Image
from tkinter import filedialog, messagebox

# Your previous code goes here...
# Initialize Tkinter or other frameworks you're using

# Path to the Tesseract executable (make sure Tesseract is installed and the path is correct)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust the path as needed

# OCR function to extract text from an image
def extract_text_from_image(image_path):
    """
    Function to extract text from an image using Tesseract OCR.
    """
    try:
        # Open the image file using PIL
        image = Image.open(image_path)
        
        # Use pytesseract to do OCR on the image
        extracted_text = pytesseract.image_to_string(image)

        return extracted_text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

# Your existing form field auto-fill function (or similar)
def auto_fill_form(extracted_text):
    """
    Example function that auto-fills form fields based on extracted text.
    This should be tailored to your specific fields and form layout.
    """
    # Split the extracted text into lines or use regex to match specific fields
    form_fields = extracted_text.split('\n')
    
    # Assuming form fields are available as entry_name, entry_address, entry_email, etc.
    if len(form_fields) > 0:
        entry_name.delete(0, tk.END)
        entry_name.insert(0, form_fields[0])  # Name Field
    if len(form_fields) > 1:
        entry_address.delete(0, tk.END)
        entry_address.insert(0, form_fields[1])  # Address Field
    if len(form_fields) > 2:
        entry_email.delete(0, tk.END)
        entry_email.insert(0, form_fields[2])  # Email Field

# Function that handles the OCR process when the user uploads a document
def process_image():
    """
    Function to open the file dialog, extract text using OCR, and auto-fill the form fields.
    """
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    
    if file_path:
        try:
            # Extract text from the selected image
            extracted_text = extract_text_from_image(file_path)
            
            if extracted_text:
                # Auto-fill form fields with the extracted text
                auto_fill_form(extracted_text)

                # Show a success message
                messagebox.showinfo("OCR Success", "Form fields auto-filled with OCR data.")
            else:
                messagebox.showerror("OCR Error", "No text found in the document.")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# If you're using Tkinter or another GUI framework, initialize the app and add OCR button
# Example with Tkinter
import tkinter as tk

# Sample GUI (adjust this as per your existing GUI code)
root = tk.Tk()
root.title("OCR Form Auto-Fill")

tk.Label(root, text="Name:").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Address:").pack()
entry_address = tk.Entry(root)
entry_address.pack()

tk.Label(root, text="Email:").pack()
entry_email = tk.Entry(root)
entry_email.pack()

# Add OCR button
ocr_button = tk.Button(root, text="Upload Document", command=process_image)
ocr_button.pack()

root.mainloop()
