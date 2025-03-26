from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import re
from weasyprint import HTML
import openai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

def sanitize_input(text):
    """Remove any potentially harmful characters"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def validate_input(data):
    required_fields = ['name', 'email', 'phone', 'job_title', 'company', 'education', 'experience', 'skills']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(data['email']):
        raise ValueError("Invalid email format")
    
    phone = re.sub(r'\D', '', data['phone'])
    if len(phone) < 10:
        raise ValueError("Phone number must have at least 10 digits")
    
    return True

def enhance_experience_with_ai(raw_experience):
    if not raw_experience:
        return "No experience provided"
    
    sanitized_experience = sanitize_input(raw_experience)
    
    prompt = f"""
You are a professional resume assistant.
Rewrite the following work experience into bullet points using strong action verbs and a professional tone:

\"\"\"{sanitized_experience}\"\"\"
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
        print(f"AI Enhancement Error: {str(e)}")
        return raw_experience

def analyze_resume_keywords(text, job_description=None):
    """Analyze resume content for keyword optimization"""
    # Tokenize text
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Get keyword frequency
    keyword_freq = {}
    for word in keywords:
        keyword_freq[word] = keyword_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    
    # If job description provided, analyze keyword match
    job_match_score = None
    if job_description:
        job_tokens = word_tokenize(job_description.lower())
        job_keywords = [word for word in job_tokens if word.isalnum() and word not in stop_words]
        matching_keywords = set(keywords) & set(job_keywords)
        job_match_score = len(matching_keywords) / len(set(job_keywords)) * 100
    
    return {
        'top_keywords': sorted_keywords[:10],
        'keyword_count': len(set(keywords)),
        'job_match_score': job_match_score
    }

def score_resume(data):
    """Score the resume based on various factors"""
    score = 0
    feedback = []
    
    # Check experience length
    exp_words = len(data['experience'].split())
    if exp_words < 50:
        feedback.append("Experience section is too brief. Add more details.")
    elif exp_words > 300:
        feedback.append("Experience section might be too long. Consider condensing.")
    score += min(exp_words / 100, 30)
    
    # Check skills count
    skills_count = len(data['skills'])
    if skills_count < 5:
        feedback.append("Add more skills to strengthen your profile.")
    elif skills_count > 15:
        feedback.append("Consider focusing on your most relevant skills.")
    score += min(skills_count * 2, 20)
    
    # Check education
    if len(data['education']) > 20:
        score += 20
    else:
        feedback.append("Add more details to your education section.")
    
    # Check contact information
    if all([data['email'], data['phone']]):
        score += 10
    else:
        feedback.append("Ensure all contact information is provided.")
    
    # Analyze keywords
    keyword_analysis = analyze_resume_keywords(data['experience'])
    score += min(keyword_analysis['keyword_count'] * 0.5, 20)
    
    return {
        'score': min(score, 100),
        'feedback': feedback,
        'keyword_analysis': keyword_analysis
    }

def parse_linkedin_profile(url):
    """Parse LinkedIn profile URL for data extraction"""
    try:
        # This is a placeholder - actual LinkedIn scraping would require authentication
        # and compliance with LinkedIn's terms of service
        return {
            'success': False,
            'message': 'LinkedIn profile parsing is currently not available.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

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
        print(f"Cover Letter Generation Error: {str(e)}")
        return f"Error generating cover letter. Please try again later."

def save_files(data, html_content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('output', exist_ok=True)
    
    try:
        # Generate resume score
        resume_score = score_resume(data)
        data['resume_score'] = resume_score
        
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
        
        # Save resume analysis
        analysis_path = f"output/analysis_{timestamp}.json"
        with open(analysis_path, 'w') as f:
            json.dump(resume_score, f, indent=2)
        
        return {
            'timestamp': timestamp,
            'paths': {
                'json': json_path,
                'html': html_path,
                'pdf': pdf_path,
                'cover_letter': cover_letter_path,
                'analysis': analysis_path
            },
            'analysis': resume_score
        }
    except Exception as e:
        print(f"File Save Error: {str(e)}")
        raise Exception(f"Error saving files: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_resume', methods=['POST'])
def create_resume():
    try:
        data = {
            key: sanitize_input(value)
            for key, value in request.form.to_dict().items()
        }
        
        validate_input(data)
        
        data['skills'] = [
            skill.strip() 
            for skill in data.get('skills', '').split(',') 
            if skill.strip()
        ]
        
        if not data['skills']:
            raise ValueError("At least one skill is required")
        
        data['experience'] = enhance_experience_with_ai(data['experience'])
        
        html_content = render_template('resume_template.html', **data)
        
        file_info = save_files(data, html_content)
        
        return jsonify({
            'success': True,
            'message': 'Resume created successfully!',
            'timestamp': file_info['timestamp'],
            'analysis': file_info['analysis']
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"Resume Creation Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error creating resume: {str(e)}'
        }), 500

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")
        
        analysis = score_resume(data)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/download/<timestamp>/<file_type>')
def download_file(timestamp, file_type):
    if not re.match(r'^\d{8}_\d{6}$', timestamp):
        return 'Invalid timestamp format', 400
        
    file_mapping = {
        'pdf': f'output/resume_{timestamp}.pdf',
        'html': f'output/resume_{timestamp}.html',
        'json': f'output/resume_{timestamp}.json',
        'cover_letter': f'output/cover_letter_{timestamp}.txt',
        'analysis': f'output/analysis_{timestamp}.json'
    }
    
    if file_type not in file_mapping:
        return 'Invalid file type', 400
    
    file_path = file_mapping[file_type]
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    except Exception as e:
        print(f"File Download Error: {str(e)}")
        return 'Error downloading file', 500

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
    app.run(debug=True)