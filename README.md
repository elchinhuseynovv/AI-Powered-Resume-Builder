# Author

Elchin Huseynov

# AI-Powered Resume Builder

An intelligent resume builder that uses AI to enhance your work experience descriptions and automatically generate personalized cover letters.

## Features

- AI-powered experience enhancement using GPT-3.5
- Automatic cover letter generation
- Multiple export formats (PDF, HTML, JSON)
- Professional resume template
- Real-time preview
- Mobile-responsive design

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Fill out the form with your information
2. Submit to generate your resume
3. Download your resume in various formats:
   - PDF (print-ready)
   - HTML (web version)
   - JSON (data backup)
   - Cover Letter (text format)

## Development

- Built with Flask and TailwindCSS
- Uses OpenAI's GPT-3.5 for AI features
- WeasyPrint for PDF generation