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
