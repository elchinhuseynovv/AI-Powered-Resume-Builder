from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
from weasyprint import HTML
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

def validate_input(data):
    required_fields = ['name', 'email', 'phone', 'job_title', 'company', 'education', 'experience', 'skills']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    # Validate email format
    if '@' not in data['email']:
        raise ValueError("Invalid email format")
    
    return True

def enhance_experience_with_ai(raw_experience):
    if not raw_experience:
        return "No experience provided"
        
    prompt = f"""
You are a professional resume assistant.
Rewrite the following work experience into bullet points using strong action verbs and a professional tone:

\"\"\"{raw_experience}\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error enhancing experience: {str(e)}"

def generate_cover_letter(data):
    prompt = f"""
Write a professional and personalized cover letter for a {data['job_title']} position at {data['company']}.
Use the following candidate info:
- Name: {data['name']}
- Email: {data['email']}
- Phone: {data['phone']}
- Education: {data['education']}
- Experience: {data['experience']}
- Skills: {', '.join(data['skills'])}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def save_files(data, html_content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    try:
        # Save JSON
        json_path = f"output/resume_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Save HTML
        html_path = f"output/resume_{timestamp}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_path = f"output/resume_{timestamp}.pdf"
        HTML(string=html_content).write_pdf(pdf_path)
        
        # Save cover letter
        cover_letter = generate_cover_letter(data)
        cover_letter_path = f"output/cover_letter_{timestamp}.txt"
        with open(cover_letter_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        return {
            'timestamp': timestamp,
            'paths': {
                'json': json_path,
                'html': html_path,
                'pdf': pdf_path,
                'cover_letter': cover_letter_path
            }
        }
    except Exception as e:
        raise Exception(f"Error saving files: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_resume', methods=['POST'])
def create_resume():
    try:
        data = request.form.to_dict()
        
        # Validate input
        validate_input(data)
        
        # Process skills
        data['skills'] = [skill.strip() for skill in data.get('skills', '').split(',') if skill.strip()]
        
        if not data['skills']:
            raise ValueError("At least one skill is required")
        
        # Enhance experience with AI
        data['experience'] = enhance_experience_with_ai(data['experience'])
        
        # Generate HTML from template
        html_content = render_template('resume_template.html', **data)
        
        # Save all files
        file_info = save_files(data, html_content)
        
        return jsonify({
            'success': True,
            'message': 'Resume created successfully!',
            'timestamp': file_info['timestamp']
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating resume: {str(e)}'
        }), 500

@app.route('/download/<timestamp>/<file_type>')
def download_file(timestamp, file_type):
    file_mapping = {
        'pdf': f'output/resume_{timestamp}.pdf',
        'html': f'output/resume_{timestamp}.html',
        'json': f'output/resume_{timestamp}.json',
        'cover_letter': f'output/cover_letter_{timestamp}.txt'
    }
    
    if file_type not in file_mapping:
        return 'Invalid file type', 400
    
    file_path = file_mapping[file_type]
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
    app.run(debug=True)