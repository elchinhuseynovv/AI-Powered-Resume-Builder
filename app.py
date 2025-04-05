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
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
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
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)
CORS(app)

# Constants
MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB
ALLOWED_FILE_TYPES = {'pdf', 'html', 'json', 'txt'}
OUTPUT_DIR = 'output'
MAX_SKILLS = 20
MIN_EXPERIENCE_WORDS = 50
MAX_EXPERIENCE_WORDS = 1000

# Configure Flask app
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = OUTPUT_DIR

def sanitize_input(text):
    """Remove any potentially harmful characters"""
    if not isinstance(text, str):
        return ""
    # Remove HTML tags and scripts
    text = re.sub(r'<[^>]+>|<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()[:MAX_CONTENT_LENGTH]

def validate_input(data):
    """Validate input data with improved error messages"""
    if not isinstance(data, dict):
        raise ValueError("Invalid data format")

    required_fields = ['name', 'email', 'phone', 'job_title', 'company', 'education', 'experience', 'skills']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], (str, list)):
            raise ValueError(f"Invalid data type for field: {field}")
    
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(data['email']):
        raise ValueError("Invalid email format")
    
    phone = re.sub(r'\D', '', data['phone'])
    if len(phone) < 10:
        raise ValueError("Phone number must have at least 10 digits")
    
    # Validate content length
    for field, value in data.items():
        if isinstance(value, str):
            if len(value) > MAX_CONTENT_LENGTH:
                raise ValueError(f"Content too long for field: {field}")
            if field == 'experience':
                word_count = len(value.split())
                if word_count < MIN_EXPERIENCE_WORDS:
                    raise ValueError(f"Experience section must have at least {MIN_EXPERIENCE_WORDS} words")
                if word_count > MAX_EXPERIENCE_WORDS:
                    raise ValueError(f"Experience section cannot exceed {MAX_EXPERIENCE_WORDS} words")
    
    # Validate skills count
    if isinstance(data['skills'], list) and len(data['skills']) > MAX_SKILLS:
        raise ValueError(f"Cannot exceed {MAX_SKILLS} skills")
    
    return True

def enhance_experience_with_ai(raw_experience):
    """Enhance work experience with improved error handling"""
    if not raw_experience:
        return "No experience provided"
    
    try:
        sanitized_experience = sanitize_input(raw_experience)
        
        prompt = f"""
You are a professional resume assistant.
Rewrite the following work experience into bullet points using strong action verbs and a professional tone.
Focus on quantifiable achievements and impactful results.
Format each point to start with a bullet point (•).

Experience:
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
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return raw_experience
    except Exception as e:
        logger.error(f"AI Enhancement Error: {str(e)}")
        return raw_experience

def analyze_resume_keywords(text, job_description=None):
    """Analyze resume content with improved keyword detection"""
    try:
        if not text:
            return {
                'top_keywords': [],
                'keyword_count': 0,
                'job_match_score': None
            }

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
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        score = 0
        feedback = []
        
        # Experience scoring
        exp_words = len(data.get('experience', '').split())
        if exp_words < MIN_EXPERIENCE_WORDS:
            feedback.append(f"Experience section should have at least {MIN_EXPERIENCE_WORDS} words")
        elif exp_words > MAX_EXPERIENCE_WORDS:
            feedback.append(f"Experience section should not exceed {MAX_EXPERIENCE_WORDS} words")
        score += min(exp_words / 100, 30)
        
        # Skills scoring
        skills = data.get('skills', [])
        skills_count = len(skills) if isinstance(skills, list) else len(skills.split(','))
        if skills_count < 5:
            feedback.append("Add more skills to strengthen your profile (aim for 5-15 skills)")
        elif skills_count > MAX_SKILLS:
            feedback.append(f"Limit skills to {MAX_SKILLS} most relevant ones")
        score += min(skills_count * 2, 20)
        
        # Education scoring
        education = data.get('education', '')
        if len(education) > 20:
            score += 20
        else:
            feedback.append("Add more details to your education section")
        
        # Contact information scoring
        if all([data.get('email'), data.get('phone')]):
            score += 10
        else:
            feedback.append("Ensure all contact information is provided")
        
        # Keyword analysis scoring
        keyword_analysis = analyze_resume_keywords(data.get('experience', ''))
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
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        prompt = f"""
Write a professional and personalized cover letter for a {data['job_title']} position at {data['company']}.
Use the following candidate info:
- Name: {data['name']}
- Email: {data['email']}
- Phone: {data['phone']}
- Education: {data['education']}
- Experience: {data['experience']}
- Skills: {', '.join(data['skills']) if isinstance(data['skills'], list) else data['skills']}

Guidelines:
1. Keep it concise and professional (max 400 words)
2. Highlight relevant experience and skills
3. Show enthusiasm for the role and company
4. Include a strong call to action
5. Format with proper paragraphs and spacing
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return "Error generating cover letter. Please try again later."
    except Exception as e:
        logger.error(f"Cover Letter Generation Error: {str(e)}")
        return "Error generating cover letter. Please try again later."

def save_files(data, html_content):
    """Save files with improved error handling and security"""
    if not isinstance(data, dict) or not isinstance(html_content, str):
        raise ValueError("Invalid input data")

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
        
        # Validate all file paths
        for path in file_paths.values():
            if not os.path.abspath(path).startswith(os.path.abspath(OUTPUT_DIR)):
                raise ValueError("Invalid file path")
        
        # Save JSON
        with open(file_paths['json'], 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
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
        with open(file_paths['analysis'], 'w', encoding='utf-8') as f:
            json.dump(resume_score, f, indent=2, ensure_ascii=False)
        
        return {
            'timestamp': timestamp,
            'paths': file_paths,
            'analysis': resume_score
        }
    except Exception as e:
        logger.error(f"File Save Error: {str(e)}")
        # Clean up any partially created files
        for path in file_paths.values():
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
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
        
        # Process skills
        skills_input = data.get('skills', '')
        data['skills'] = [
            skill.strip() 
            for skill in (skills_input.split(',') if isinstance(skills_input, str) else skills_input)
            if skill.strip()
        ]
        
        if not data['skills']:
            raise ValueError("At least one skill is required")
        
        if len(data['skills']) > MAX_SKILLS:
            raise ValueError(f"Cannot exceed {MAX_SKILLS} skills")
        
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
        
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")
        
        # Validate required fields
        required_fields = ['experience', 'skills']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not data[field]:
                raise ValueError(f"Empty field: {field}")
        
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
        
        # Secure the filename
        safe_timestamp = secure_filename(timestamp)
        
        file_mapping = {
            'pdf': f'resume_{safe_timestamp}.pdf',
            'html': f'resume_{safe_timestamp}.html',
            'json': f'resume_{safe_timestamp}.json',
            'cover_letter': f'cover_letter_{safe_timestamp}.txt',
            'analysis': f'analysis_{safe_timestamp}.json'
        }
        
