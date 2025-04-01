import json
from datetime import datetime
import os
from weasyprint import HTML
import openai
from dotenv import load_dotenv
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables and NLTK data
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class ResumeBuilder:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_user_input(self) -> Dict[str, Union[str, List[str]]]:
        """Get user input for resume creation with improved validation."""
        print("🧾 Welcome to the Enhanced Resume Builder!")
        
        inputs = {
            "name": self._get_validated_input("Full Name: ", self._validate_name),
            "email": self._get_validated_input("Email: ", self._validate_email),
            "phone": self._get_validated_input("Phone: ", self._validate_phone),
            "job_title": input("Job Title (e.g., Software Developer): ").strip(),
            "company": input("Target Company (for cover letter): ").strip(),
            "education": self._get_education_input(),
            "experience": input("Work Experience: ").strip(),
            "skills": self._get_skills_input()
        }
        
        return inputs

    def _get_validated_input(self, prompt: str, validator_func) -> str:
        """Get user input with validation."""
        while True:
            value = input(prompt).strip()
            try:
                validator_func(value)
                return value
            except ValueError as e:
                print(f"❌ {str(e)}")

    def _validate_name(self, name: str) -> None:
        """Validate name input."""
        if not name:
            raise ValueError("Name cannot be empty")
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")

    def _validate_email(self, email: str) -> None:
        """Validate email format."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")

    def _validate_phone(self, phone: str) -> None:
        """Validate phone number."""
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise ValueError("Phone number must have at least 10 digits")

    def _get_education_input(self) -> str:
        """Get structured education input."""
        print("\n📚 Education Information")
        education_entries = []
        
        while True:
            degree = input("Degree (or 'done' to finish): ").strip()
            if degree.lower() == 'done':
                break
                
            institution = input("Institution: ").strip()
            year = input("Year: ").strip()
            
            entry = f"{degree} - {institution} ({year})"
            education_entries.append(entry)
            
        return "\n".join(education_entries)

    def _get_skills_input(self) -> List[str]:
        """Get and validate skills input."""
        while True:
            skills_input = input("Skills (comma-separated): ").strip()
            skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            
            if not skills:
                print("❌ Please enter at least one skill")
                continue
                
            return skills

    def enhance_experience_with_ai(self, raw_experience: str) -> str:
        """Enhance work experience using AI with improved prompt."""
        print("\n🤖 Enhancing your experience section with AI...")
        
        prompt = f"""
