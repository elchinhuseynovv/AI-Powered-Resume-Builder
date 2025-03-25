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


if __name__ == "__main__":
    main()
