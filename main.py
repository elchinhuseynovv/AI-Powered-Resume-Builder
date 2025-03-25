pip install weasyprint # type: ignore
import json
from datetime import datetime
import os
from weasyprint import HTML  # Make sure WeasyPrint is installed

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

        # Replace single placeholders
        html_content = template
        html_content = html_content.replace('{{ name }}', data['name'])
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

        # Optional: convert to PDF
        pdf_filename = f"resume_{timestamp}.pdf"
        HTML(string=html_content).write_pdf(pdf_filename)
        print(f"✅ PDF resume generated: {pdf_filename}")

        # Optional: open HTML in browser
        os.system(f"python -m webbrowser {html_filename}")

    except Exception as e:
        print(f"❌ Error generating HTML/PDF: {str(e)}")

def get_user_input():
    print("🧾 Welcome to the Resume Builder!")
    name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    education = input("Education: ")
    experience = input("Work Experience: ")
    skills = input("Skills (comma-separated): ")

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": [skill.strip() for skill in skills.split(",")]
    }

def render_resume(data):
    print("\n✨ Your Resume:\n")
    print(f"{data['name']}")
    print(f"Email: {data['email']} | Phone: {data['phone']}\n")
    print("🎓 Education\n" + data['education'] + "\n")
    print("💼 Experience\n" + data['experience'] + "\n")
    print("🛠 Skills\n" + ", ".join(data['skills']))

def main():
    resume = get_user_input()
    render_resume(resume)
    timestamp = save_resume_to_json(resume)
    if timestamp:
        generate_html_resume(resume, timestamp)

if __name__ == "__main__":
    main()
