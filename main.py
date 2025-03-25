import json
from datetime import datetime

def save_resume_to_json(data):
    """Save resume data to a JSON file with timestamp in filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Resume saved successfully to {filename}")
    except Exception as e:
        print(f"\n❌ Error saving resume: {str(e)}")

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
    save_resume_to_json(resume)

if __name__ == "__main__":
    main()