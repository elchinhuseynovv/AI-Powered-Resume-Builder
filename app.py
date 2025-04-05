from flask import Flask, render_template, request, send_file, jsonify, abort
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
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK data: {e}")

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Constants
MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB
ALLOWED_FILE_TYPES = {'pdf', 'html', 'json', 'txt'}
OUTPUT_DIR = 'output'

def sanitize_input(text):
    """Remove any potentially harmful characters"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()[:MAX_CONTENT_LENGTH]

def validate_input(data):
    """Validate input data with improved error messages"""
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
    
    # Additional validation for content length
    for field, value in data.items():
        if isinstance(value, str) and len(value) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content too long for field: {field}")
    
    return True

def enhance_experience_with_ai(raw_experience):
    """Enhance work experience with improved error handling"""
    if not raw_experience:
        return "No experience provided"
    
    try:
        sanitized_experience = sanitize_input(raw_experience)
        
        prompt = f"""
You are a professional resume assistant.
Rewrite the following work experience into bullet points using strong action verbs and a professional tone:

\"\"\"{sanitized_experience}\"\"\"
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        enhanced_content = response['choices'][0]['message']['content'].strip()
        return enhanced_content if enhanced_content else raw_experience
    except Exception as e:
        logger.error(f"AI Enhancement Error: {str(e)}")
        return raw_experience

def analyze_resume_keywords(text, job_description=None):
    """Analyze resume content with improved keyword detection"""
    try:
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and normalize
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
        
        # Get keyword frequency with improved counting
        keyword_freq = {}
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate job match score if description provided
        job_match_score = None
        if job_description:
            job_tokens = word_tokenize(job_description.lower())
            job_keywords = [word for word in job_tokens if word.isalnum() and word not in stop_words]
            if job_keywords:
                matching_keywords = set(keywords) & set(job_keywords)
                job_match_score = (len(matching_keywords) / len(set(job_keywords))) * 100
        
        return {
            'top_keywords': sorted_keywords[:10],
            'keyword_count': len(set(keywords)),
            'job_match_score': job_match_score
        }
    except Exception as e:
        logger.error(f"Keyword analysis error: {str(e)}")
        return {
            'top_keywords': [],
            'keyword_count': 0,
            'job_match_score': None
        }

def score_resume(data):
    """Score resume with improved scoring algorithm"""
    try:
        score = 0
        feedback = []
        
        # Experience scoring
        exp_words = len(data['experience'].split())
        if exp_words < 50:
            feedback.append("Experience section is too brief. Add more details.")
        elif exp_words > 300:
            feedback.append("Experience section might be too long. Consider condensing.")
        score += min(exp_words / 100, 30)
        
        # Skills scoring
        skills_count = len(data['skills'])
        if skills_count < 5:
            feedback.append("Add more skills to strengthen your profile.")
        elif skills_count > 15:
            feedback.append("Consider focusing on your most relevant skills.")
        score += min(skills_count * 2, 20)
        
        # Education scoring
        if len(data['education']) > 20:
            score += 20
        else:
            feedback.append("Add more details to your education section.")
        
        # Contact information scoring
        if all([data['email'], data['phone']]):
            score += 10
        else:
            feedback.append("Ensure all contact information is provided.")
        
        # Keyword analysis scoring
        keyword_analysis = analyze_resume_keywords(data['experience'])
        score += min(keyword_analysis['keyword_count'] * 0.5, 20)
        
        return {
            'score': min(round(score, 1), 100),
            'feedback': feedback,
            'keyword_analysis': keyword_analysis
        }
    except Exception as e:
        logger.error(f"Resume scoring error: {str(e)}")
        return {
            'score': 0,
            'feedback': ["Error analyzing resume"],
            'keyword_analysis': None
        }

def generate_cover_letter(data):
    """Generate cover letter with improved prompt"""
    try:
        prompt = f"""
Write a professional and personalized cover letter for a {data['job_title']} position at {data['company']}.
Use the following candidate info:
- Name: {data['name']}
- Email: {data['email']}
- Phone: {data['phone']}
- Education: {data['education']}
- Experience: {data['experience']}
- Skills: {', '.join(data['skills'])}

Guidelines:
1. Keep it concise and professional
2. Highlight relevant experience and skills
3. Show enthusiasm for the role and company
4. Include a strong call to action
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"Cover Letter Generation Error: {str(e)}")
        return "Error generating cover letter. Please try again later."

def save_files(data, html_content):
    """Save files with improved error handling and security"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # Generate resume score
        resume_score = score_resume(data)
        data['resume_score'] = resume_score
        
        file_paths = {
            'json': os.path.join(OUTPUT_DIR, f"resume_{timestamp}.json"),
            'html': os.path.join(OUTPUT_DIR, f"resume_{timestamp}.html"),
            'pdf': os.path.join(OUTPUT_DIR, f"resume_{timestamp}.pdf"),
            'cover_letter': os.path.join(OUTPUT_DIR, f"cover_letter_{timestamp}.txt"),
            'analysis': os.path.join(OUTPUT_DIR, f"analysis_{timestamp}.json")
        }
        
        # Save JSON
        with open(file_paths['json'], 'w') as f:
            json.dump(data, f, indent=2)
        
        # Save HTML
        with open(file_paths['html'], 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF
        HTML(string=html_content).write_pdf(file_paths['pdf'])
        
        # Save cover letter
        cover_letter = generate_cover_letter(data)
        with open(file_paths['cover_letter'], 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        # Save resume analysis
        with open(file_paths['analysis'], 'w') as f:
            json.dump(resume_score, f, indent=2)
        
        return {
            'timestamp': timestamp,
            'paths': file_paths,
            'analysis': resume_score
        }
    except Exception as e:
        logger.error(f"File Save Error: {str(e)}")
        raise Exception(f"Error saving files: {str(e)}")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/create_resume', methods=['POST'])
def create_resume():
    """Create resume with improved error handling"""
    try:
        if not request.form:
            raise ValueError("No form data provided")
        
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
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Resume Creation Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while creating your resume'
        }), 500

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """Analyze resume with improved validation"""
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")
        
        # Validate required fields
        required_fields = ['experience', 'skills']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        analysis = score_resume(data)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Resume analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while analyzing the resume'
        }), 500

@app.route('/download/<timestamp>/<file_type>')
def download_file(timestamp, file_type):
    """Download files with improved security"""
    try:
        # Validate timestamp format
        if not re.match(r'^\d{8}_\d{6}$', timestamp):
            abort(400, description="Invalid timestamp format")
        
        # Validate file type
        if file_type not in ALLOWED_FILE_TYPES:
            abort(400, description="Invalid file type")
        
        file_mapping = {
            'pdf': f'output/resume_{timestamp}.pdf',
            'html': f'output/resume_{timestamp}.html',
            'json': f'output/resume_{timestamp}.json',
            'cover_letter': f'output/cover_letter_{timestamp}.txt',
            'analysis': f'output/analysis_{timestamp}.json'
        }
        
        file_path = file_mapping[file_type]
        
        # Validate file path
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            abort(404, description="File not found")
        
        # Ensure file is within allowed directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_DIR)):
            abort(403, description="Access denied")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )