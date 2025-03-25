import json
from datetime import datetime
import os

def save_resume_to_json(data):
    """Save resume data to a JSON file with timestamp in filename"""
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
    """Generate HTML resume from template and data"""
    try:
        # Read the HTML template
        with open('resume_template.html', 'r') as f:
            template = f.read()

        # Replace placeholders with actual data
        html_content = template.replace('{{ name }}', data['name'])
        html_content = html_content.replace('{{ email }}', data['email'])
        html_content = html_content.replace('{{ phone }}', data['phone'])
        html_content = html_content.replace('{{ education }}', data['education'])
        html_content = html_content.replace('{{ experience }}', data['experience'])

        # Handle skills list
        skills_html = ''
        for skill in data['skills']:
            skills_html += f'<li class="skill-item">{skill}</li>\n'
        html_content = html_content.replace('{% for skill in skills %}\n                <li class="skill-item">{{ skill }}</li>\n                {% endfor %}', skills_html)

        # Save the HTML file
        filename = f"resume_{timestamp}.html"
        with open(filename, 'w') as f:
            f.write(html_content)
        print(f"✅ HTML resume generated successfully as {filename}")
        
        # Open the HTML file in the default browser
        print("📂 Opening resume in your default web browser...")
        os.system(f"python -m webbrowser {filename}")
        
    except Exception as e:
        print(f"❌ Error generating HTML resume: {str(e)}")

def get_user_input():
    print("🧾 Welcome to the Resume Builder!")
    name = input("Full Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    education = input("Education: ")
    experience = input("Work Experience: ")
    skills = input("Skills (comma-separated): ")

    resume_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": [skill.strip() for skill in skills.split(",")]
    }

    return resume_data

def render_resume(data):
    print("\n✨ Your Resume:\n")
    print(f"{data['name']}")
    print(f"Email: {data['email']} | Phone: {data['phone']}\n")

    print("🎓 Education")
    print(data['education'], "\n")

    print("💼 Experience")
    print(data['experience'], "\n")

    print("🛠 Skills")
    print(", ".join(data['skills']))

def main():
    resume = get_user_input()
    render_resume(resume)
    timestamp = save_resume_to_json(resume)
    if timestamp:
        generate_html_resume(resume, timestamp)

if __name__ == "__main__":
    main()