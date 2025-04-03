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