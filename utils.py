"""Utility functions for the resume builder."""
import os
import re
import logging
from typing import Dict, List, Union, Optional
import openai
from weasyprint import HTML
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def sanitize_input(text: str) -> str:
    """Remove any potentially harmful characters."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def validate_input(data: Dict[str, Union[str, List[str]]]) -> bool:
    """Validate input data for resume creation."""
    required_fields = ['name', 'email', 'phone', 'job_title', 'company', 'education', 'experience', 'skills']
    
    # Check required fields
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    # Validate email format
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(data['email']):
        raise ValueError("Invalid email format")
    
    # Validate phone number
    phone = re.sub(r'\D', '', data['phone'])
    if len(phone) < 10:
        raise ValueError("Phone number must have at least 10 digits")
    
    return True

def enhance_experience_with_ai(raw_experience: str) -> str:
    """Enhance work experience using OpenAI GPT-3.5."""
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
        logger.error(f"AI Enhancement Error: {str(e)}")
        return raw_experience

def generate_cover_letter(data: Dict[str, Union[str, List[str]]]) -> str:
    """Generate a cover letter using OpenAI GPT-3.5."""
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
        logger.error(f"Cover Letter Generation Error: {str(e)}")
        return "Error generating cover letter. Please try again later."

def generate_pdf(html_content: str, output_path: str) -> bool:
    """Generate PDF from HTML content."""
    try:
        HTML(string=html_content).write_pdf(output_path)
        return True
    except Exception as e:
        logger.error(f"PDF Generation Error: {str(e)}")
        return False

def save_files(data: Dict[str, Union[str, List[str]]], html_content: str, output_dir: str = "output") -> Optional[Dict]:
    """Save resume files in multiple formats."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = data.get('timestamp', '')
        
        # Save JSON
        json_path = os.path.join(output_dir, f"resume_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(data, f, indent=2)
        
        # Save HTML
        html_path = os.path.join(output_dir, f"resume_{timestamp}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_path = os.path.join(output_dir, f"resume_{timestamp}.pdf")
        if not generate_pdf(html_content, pdf_path):
            raise Exception("Failed to generate PDF")
        
        # Generate and save cover letter
        cover_letter = generate_cover_letter(data)
        cover_letter_path = os.path.join(output_dir, f"cover_letter_{timestamp}.txt")
        with open(cover_letter_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        return {
            'json_path': json_path,
            'html_path': html_path,
            'pdf_path': pdf_path,
            'cover_letter_path': cover_letter_path
        }
    except Exception as e:
        logger.error(f"File Save Error: {str(e)}")
        return None

def format_phone_number(phone: str) -> str:
    """Format phone number consistently."""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone

def validate_file_path(file_path: str) -> bool:
    """Validate file path for security."""
    if not file_path:
        return False
    
    # Check for directory traversal attempts
    if '..' in file_path or '//' in file_path:
        return False
    
    # Check for absolute paths
    if os.path.isabs(file_path):
        return False
    
    # Check allowed extensions
    allowed_extensions = {'.pdf', '.html', '.json', '.txt'}
    if not any(file_path.lower().endswith(ext) for ext in allowed_extensions):
        return False