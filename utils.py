import openai
from weasyprint import HTML
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def enhance_experience_with_ai(raw_experience):
    """Enhance work experience using OpenAI GPT-3.5"""
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
    """Generate a cover letter using OpenAI GPT-3.5"""
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

def generate_pdf(html_content, output_path):
    """Generate PDF from HTML content"""
    try:
        HTML(string=html_content).write_pdf(output_path)
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False