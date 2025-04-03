"""Core resume builder functionality."""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging
from weasyprint import HTML
import openai
from utils import sanitize_input, validate_input, enhance_experience_with_ai
from resume_analyzer import ResumeAnalyzer
from resume_formatter import ResumeFormatter

logger = logging.getLogger(__name__)

class ResumeBuilder:
    """Main resume builder class."""
    
    def __init__(self, config):
        """Initialize resume builder with configuration."""
        self.config = config
        self.analyzer = ResumeAnalyzer()
        self.formatter = ResumeFormatter()
        self.output_dir = config.OUTPUT_FOLDER
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize OpenAI
        openai.api_key = config.OPENAI_API_KEY

    def create_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Create a complete resume package."""
        try:
            # Validate and sanitize input
            sanitized_data = self._sanitize_data(data)
            validate_input(sanitized_data)
            
            # Format and enhance content
            formatted_data = self.formatter.format_resume(sanitized_data)
            formatted_data['experience'] = enhance_experience_with_ai(formatted_data['experience'])
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            formatted_data['timestamp'] = timestamp
            
            # Create resume files
            files = self._generate_files(formatted_data)
            
            # Analyze resume
            analysis = self.analyzer.analyze_resume(formatted_data)
            
            return {
                'success': True,
                'timestamp': timestamp,
                'files': files,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Resume creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _sanitize_data(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Sanitize all input data."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = sanitize_input(value)
            elif isinstance(value, list):
                sanitized[key] = [sanitize_input(item) for item in value]
            else:
                sanitized[key] = value
        return sanitized

    def _generate_files(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Generate all resume files."""
        timestamp = data['timestamp']
        output = {}
        
        try:
            # Generate HTML content
            with open('templates/resume_template.html', 'r', encoding='utf-8') as f:
                template = f.read()
            html_content = self._fill_template(template, data)
            
            # Save files
            file_paths = {
                'json': f"resume_{timestamp}.json",
                'html': f"resume_{timestamp}.html",
                'pdf': f"resume_{timestamp}.pdf",
                'cover_letter': f"cover_letter_{timestamp}.txt",
                'analysis': f"analysis_{timestamp}.json"
            }
            
            # Save JSON
            json_path = os.path.join(self.output_dir, file_paths['json'])
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            output['json'] = file_paths['json']
            
            # Save HTML
            html_path = os.path.join(self.output_dir, file_paths['html'])
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            output['html'] = file_paths['html']
            
            # Generate PDF
            pdf_path = os.path.join(self.output_dir, file_paths['pdf'])
            HTML(string=html_content).write_pdf(pdf_path)
            output['pdf'] = file_paths['pdf']
            
            # Generate cover letter
            cover_letter = self._generate_cover_letter(data)
            cover_letter_path = os.path.join(self.output_dir, file_paths['cover_letter'])
            with open(cover_letter_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter)
            output['cover_letter'] = file_paths['cover_letter']
            
            return output
            
        except Exception as e:
            logger.error(f"File generation error: {str(e)}")
            raise

    def _fill_template(self, template: str, data: Dict[str, Union[str, List[str]]]) -> str:
        """Fill HTML template with resume data."""
        html_content = template
        for key, value in data.items():
            if isinstance(value, list):
                value = ', '.join(value)
            placeholder = f"{{{{ {key} }}}}"
            html_content = html_content.replace(placeholder, str(value))
        return html_content

    def _generate_cover_letter(self, data: Dict[str, Union[str, List[str]]]) -> str:
        """Generate an AI-powered cover letter."""
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
                model=self.config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.AI_TEMPERATURE,
                max_tokens=self.config.AI_MAX_TOKENS
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error(f"Cover letter generation error: {str(e)}")
            return "Error generating cover letter. Please try again later."

    def get_file(self, timestamp: str, file_type: str) -> Optional[str]:
        """Retrieve a generated file."""
        if not self._validate_timestamp(timestamp):
            return None
            
        file_mapping = {
            'pdf': f'resume_{timestamp}.pdf',
            'html': f'resume_{timestamp}.html',
            'json': f'resume_{timestamp}.json',
            'cover_letter': f'cover_letter_{timestamp}.txt',
            'analysis': f'analysis_{timestamp}.json'
        }
        
        if file_type not in file_mapping:
            return None
            
        file_path = os.path.join(self.output_dir, file_mapping[file_type])
        if not os.path.exists(file_path):
            return None
            
        return file_path

    def _validate_timestamp(self, timestamp: str) -> bool:
        """Validate timestamp format."""
        try:
            datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            return True
        except ValueError:
            return False