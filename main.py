import json
from datetime import datetime
import os
from weasyprint import HTML
import openai

# 🔐 Set your OpenAI API key here (or use environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")  # or write directly: openai.api_key = "sk-..."

def get_user_input():
    print("🧾 Welcome to the Resume Builder!")
    name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    education = input("Education: ")
    experience = input("Work Experience (describe in your own words): ")
    skills = input("Skills (comma-separated): ")

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": [skill.strip() for skill in skills.split(",")]
    }

def enhance_experience_with_ai(raw_experience):
    print("\n🤖 Enhancing your experience section with AI...")

    prompt = f"""You are a professional resume assistant. 
Given the following plain-text work experience description, rewrite it in a polished, bullet-pointed, professional format suitable for a resume.

Original:
\"\"\"{raw_experience}\"\"\"

Improved:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        improved_text = response['choices'][0]['message']['content'].strip()
        print("✅ AI-enhanced experience received!")
        return improved_text

    except Exception as e:
        print(f"❌ Error during AI enhancement: {str(e)}")
        return raw_experience  # fallback

def save_resume_to_json(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_{timestamp}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Resume saved successfully to {filename}")
        return timestamp
    except Exception as e:
        print(f"\n❌ Error saving resume: {str(e)}")
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

        # Generate skills HTML
        skills_html = '\n'.join([f'<li class="skill-item">{skill}</li>' for skill in data['skills']])
        html_content = html_content.replace(
            '{% for skill in skills %}\n          <li class="skill-item">{{ skill }}</li>\n          {% endfor %}',
            skills_html
        )

        # Save HTML file
        html_filename = f"resume_{timestamp}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML resume generated: {html_filename}")

        # Convert to PDF
        pdf_filename = f"resume_{timestamp}.pdf"
        HTML(string=html_content).write_pdf(pdf_filename)
        print(f"✅ PDF resume generated: {pdf_filename}")

        # Open in browser
        os.system(f"python -m webbrowser {html_filename}")

    except Exception as e:
        print(f"❌ Error generating HTML/PDF: {str(e)}")

def render_resume(data):
    print("\n✨ Your Resume:\n")
    print(f"{data['name']}")
    print(f"Email: {data['email']} | Phone: {data['phone']}\n")
    print("🎓 Education\n" + data['education'] + "\n")
    print("💼 Experience\n" + data['experience'] + "\n")
    print("🛠 Skills\n" + ", ".join(data['skills']))

def main():
    resume = get_user_input()
    resume["experience"] = enhance_experience_with_ai(resume["experience"])
    render_resume(resume)
    timestamp = save_resume_to_json(resume)
    if timestamp:
        generate_html_resume(resume, timestamp)

if __name__ == "__main__":
    main()
