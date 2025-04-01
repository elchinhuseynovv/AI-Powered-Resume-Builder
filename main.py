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
As a professional resume writer, enhance the following work experience:
1. Use strong action verbs
2. Quantify achievements where possible
3. Focus on impact and results
4. Use industry-specific keywords
5. Format in clear bullet points

Experience:
\"\"\"{raw_experience}\"\"\"
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
            logger.error(f"AI Enhancement Error: {e}")
            return raw_experience

    def analyze_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze resume content and provide insights."""
        print("\n📊 Analyzing resume...")
        
        analysis = {
            "keyword_analysis": self._analyze_keywords(data),
            "content_score": self._score_content(data),
            "improvement_suggestions": self._generate_suggestions(data)
        }
        
        return analysis

    def _analyze_keywords(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze keyword usage and relevance."""
        text = f"{data['experience']} {' '.join(data['skills'])}"
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
        keyword_freq = {}
        
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
            
        return {
            "top_keywords": sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10],
            "keyword_density": len(set(keywords)) / len(keywords) if keywords else 0
        }

    def _score_content(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Score different aspects of the resume."""
        scores = {
            "experience": self._score_experience(data['experience']),
            "skills": min(len(data['skills']) * 10, 100),
            "education": len(data['education'].split('\n')) * 20
        }
        
        return {
            "section_scores": scores,
            "overall_score": sum(scores.values()) / len(scores)
        }

    def _score_experience(self, experience: str) -> int:
        """Score the experience section based on various factors."""
        words = experience.split()
        action_verbs = ['developed', 'implemented', 'managed', 'created', 'led']
        metrics = re.findall(r'\d+%|\$\d+|\d+ years?', experience.lower())
        
        score = min(len(words) / 10, 50)  # Base score for length
        score += sum(1 for word in words if word.lower() in action_verbs) * 5  # Action verbs
        score += len(metrics) * 10  # Metrics and quantifiable results
        
        return min(int(score), 100)

    def _generate_suggestions(self, data: Dict[str, Union[str, List[str]]]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if len(data['experience'].split()) < 100:
            suggestions.append("Add more detail to your work experience")
        if len(data['skills']) < 5:
            suggestions.append("Consider adding more relevant skills")
        if not re.search(r'\d+%|\$\d+|\d+ years?', data['experience']):
            suggestions.append("Try to quantify your achievements with metrics")
            
        return suggestions

    def generate_cover_letter(self, data: Dict[str, Union[str, List[str]]], timestamp: str) -> str:
        """Generate an AI-powered cover letter with improved structure."""
        print("\n📝 Generating AI-powered cover letter...")
        
        prompt = f"""
Write a compelling cover letter for a {data['job_title']} position at {data['company']}.
Include:
1. Strong opening paragraph
2. Skills and experience alignment
3. Company-specific details
4. Professional closing

Candidate Info:
- Name: {data['name']}
- Experience: {data['experience']}
- Skills: {', '.join(data['skills'])}
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            cover_letter = response['choices'][0]['message']['content'].strip()
            
            filename = f"cover_letter_{timestamp}.txt"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(cover_letter)
                
            print(f"✅ Cover letter saved as {filename}")
            return cover_letter
            
        except Exception as e:
            logger.error(f"Cover Letter Generation Error: {e}")
            return ""

    def save_resume(self, data: Dict[str, Union[str, List[str]]]) -> Optional[str]:
        """Save resume in multiple formats with error handling."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON
            json_path = os.path.join(self.output_dir, f"resume_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Generate and save HTML
            with open('resume_template.html', 'r', encoding='utf-8') as f:
                template = f.read()
            
            html_content = self._fill_template(template, data)
            html_path = os.path.join(self.output_dir, f"resume_{timestamp}.html")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate PDF
            pdf_path = os.path.join(self.output_dir, f"resume_{timestamp}.pdf")
            HTML(string=html_content).write_pdf(pdf_path)
            
            print(f"\n✅ Resume saved in multiple formats with timestamp: {timestamp}")
            return timestamp
            
        except Exception as e:
            logger.error(f"Error saving resume: {e}")
            return None

    def _fill_template(self, template: str, data: Dict[str, Union[str, List[str]]]) -> str:
        """Fill HTML template with resume data."""
        html_content = template
        for key, value in data.items():
            if isinstance(value, list):
                value = ', '.join(value)
            placeholder = f"{{{{ {key} }}}}"
            html_content = html_content.replace(placeholder, str(value))
            
        return html_content

def main():
    builder = ResumeBuilder()
    
    try:
        # Get and validate input
        resume_data = builder.get_user_input()
        
        # Enhance experience with AI
        resume_data['experience'] = builder.enhance_experience_with_ai(resume_data['experience'])
        
        # Save resume
        timestamp = builder.save_resume(resume_data)
        if timestamp:
            # Generate cover letter
            builder.generate_cover_letter(resume_data, timestamp)
            
            # Analyze resume
            analysis = builder.analyze_resume(resume_data)
            
            # Save analysis
            analysis_path = os.path.join(builder.output_dir, f"analysis_{timestamp}.json")
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2)
            
            print("\n📊 Resume Analysis:")
            print(f"Overall Score: {analysis['content_score']['overall_score']:.1f}/100")
            print("\nTop Keywords:")
            for keyword, count in analysis['keyword_analysis']['top_keywords'][:5]:
                print(f"- {keyword}: {count} occurrences")
            
            if analysis['improvement_suggestions']:
                print("\n💡 Suggestions for Improvement:")
                for suggestion in analysis['improvement_suggestions']:
                    print(f"- {suggestion}")
                    
    except Exception as e:
        logger.error(f"Error in resume creation: {e}")
        print("\n❌ An error occurred while creating your resume. Please try again.")

if __name__ == "__main__":
    main()