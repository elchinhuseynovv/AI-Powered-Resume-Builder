import json
from datetime import datetime
import os
from weasyprint import HTML
import openai
from dotenv import load_dotenv

# 🔐 Load .env file for API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_user_input():
    print("🧾 Welcome to the Resume Builder!")
    name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    job_title = input("Job Title (e.g., Software Developer): ")
    company = input("Target Company (for cover letter): ")
    education = input("Education: ")
    experience = input("Work Experience: ")
    skills = input("Skills (comma-separated): ")

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "job_title": job_title,
        "company": company,
        "education": education,
        "experience": experience,
        "skills": [skill.strip() for skill in skills.split(",")]
    }

def enhance_experience_with_ai(raw_experience):
    print("\n🤖 Enhancing your experience section with AI...")
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
        print(f"❌ Error enhancing experience: {e}")
        return raw_experience

def generate_cover_letter(data, timestamp):
    print("\n📝 Generating AI-powered cover letter...")
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
        cover_letter = response['choices'][0]['message']['content'].strip()

        filename = f"cover_letter_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)

        print(f"✅ Cover letter saved as {filename}")
        return cover_letter

    except Exception as e:
        print(f"❌ Error generating cover letter: {e}")
        return ""

def save_resume_to_json(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_{timestamp}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Resume data saved as {filename}")
        return timestamp
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")
        return None

def generate_html_resume(data, timestamp):
    try:
        with open('resume_template.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Replace placeholders
        html_content = template.replace('{{ name }}', data['name'])
        html_content = html_content.replace('{{ email }}', data['email'])
        html_content = html_content.replace('{{ phone }}', data['phone'])
        html_content = html_content.replace('{{ education }}', data['education'])
        html_content = html_content.replace('{{ experience }}', data['experience'])

        # Skills HTML
        skills_html = '\n'.join([f'<li class="skill-item">{skill}</li>' for skill in data['skills']])
        html_content = html_content.replace(
            '{% for skill in skills %}\n          <li class="skill-item">{{ skill }}</li>\n          {% endfor %}',
            skills_html
        )

        html_filename = f"resume_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML resume saved as {html_filename}")

        # PDF
        pdf_filename = f"resume_{timestamp}.pdf"
        HTML(string=html_content).write_pdf(pdf_filename)
        print(f"✅ PDF resume saved as {pdf_filename}")

        # Open HTML in browser
        os.system(f"python -m webbrowser {html_filename}")

    except Exception as e:
        print(f"❌ Error creating HTML/PDF: {e}")

def render_resume(data):
    print("\n✨ Your Resume:\n")
    print(f"{data['name']} — {data['job_title']}")
    print(f"Email: {data['email']} | Phone: {data['phone']}")
    print("\n🎓 Education\n" + data['education'])
    print("\n💼 Experience\n" + data['experience'])
    print("\n🛠 Skills\n" + ", ".join(data['skills']))

def main():
    resume = get_user_input()
    resume["experience"] = enhance_experience_with_ai(resume["experience"])
    render_resume(resume)
    timestamp = save_resume_to_json(resume)
    if timestamp:
        generate_html_resume(resume, timestamp)
        generate_cover_letter(resume, timestamp)

if __name__ == "__main__":
    main()
