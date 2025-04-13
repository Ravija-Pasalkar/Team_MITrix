from flask import Flask, request, jsonify, render_template_string, send_from_directory
import mysql.connector
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables (if using dotenv)
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyBhTnXB19ZFgInm8BUwidq8Ct5fRWYKvq8"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'M@n!sh_21',  # Add your DB password here
    'database': 'kyc_system'
}

DB_SCHEMA = """
Table: users
- user_id (INT, Primary Key)
- name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- registration_date (DATE)

Table: documents
- document_id (INT, Primary Key)
- user_id (INT, Foreign Key to users)
- document_type (VARCHAR)
- document_number (VARCHAR)
- document_status (VARCHAR: pending, verified, rejected)

Table: liveness_checks
- check_id (INT, Primary Key)
- user_id (INT, Foreign Key to users)
- check_date (DATE)
- result (VARCHAR: passed, failed)
"""

def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def natural_language_to_sql(query):
    prompt = f"""
    You are an expert SQL query generator for a KYC (Know Your Customer) system. Your task is to convert a natural language query into a valid SQL SELECT query, based on the database schema provided below.

    Database schema:

    Table: users
    - user_id INT PRIMARY KEY AUTO_INCREMENT
    - full_name VARCHAR(100) NOT NULL
    - dob DATE NOT NULL
    - gender ENUM('Male', 'Female', 'Other') NOT NULL
    - phone VARCHAR(15) UNIQUE NOT NULL
    - email VARCHAR(100) UNIQUE
    - address TEXT
    - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    Table: kyc_documents
    - document_id INT PRIMARY KEY AUTO_INCREMENT
    - user_id INT
    - document_type ENUM('PAN', 'DrivingLicense', 'Passport') NOT NULL
    - document_front_url TEXT
    - ocr_data JSON
    - status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending'
    - submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    - FOREIGN KEY (user_id) REFERENCES users(user_id)

    Table: kyc_face_verification
    - face_verification_id INT PRIMARY KEY AUTO_INCREMENT
    - user_id INT
    - profile_photo_url TEXT
    - face_match_score DECIMAL(5,2)
    - liveness_check_passed BOOLEAN
    - FOREIGN KEY (user_id) REFERENCES users(user_id)

    Table: user_consent
    - consent_id INT PRIMARY KEY AUTO_INCREMENT
    - user_id INT
    - user_consent_given BOOLEAN DEFAULT FALSE
    - consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    - FOREIGN KEY (user_id) REFERENCES users(user_id)

    Your job is to return only the SQL query for the following natural language query:

    Natural language query: "{query}"

    Your response should be ONLY the SQL SELECT query with correct syntax, without any explanation or extra text.
    """

    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()

        # Clean the SQL query to remove any extra characters (like code blocks or backticks)
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        return sql_query, None
    except Exception as e:
        return None, f"Error generating SQL: {str(e)}"



@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return render_template_string(f.read())

@app.route('/styles.css')
def serve_styles():
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def serve_script():
    return send_from_directory('.', 'script.js')

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    natural_query = data.get('query', '')
    
    if not natural_query:
        return jsonify({'error': 'Query is empty'}), 400

    sql_query, error = natural_language_to_sql(natural_query)
    
    if error:
        return jsonify({'error': error}), 400

    conn = connect_to_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Clean up database resources
        cursor.close()
        conn.close()

        return jsonify({
            'sql_query': sql_query,
            'columns': columns,
            'results': results
        })
    except mysql.connector.Error as err:
        print(f"SQL execution error: {err}")
        return jsonify({'error': f"Database error: {str(err)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
