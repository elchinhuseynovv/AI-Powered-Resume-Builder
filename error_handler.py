"""Error handling module for the resume builder application."""
import logging
from typing import Dict, Union
from flask import jsonify

logger = logging.getLogger(__name__)

class ResumeBuilderError(Exception):
    """Base exception class for resume builder errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ValidationError(ResumeBuilderError):
    """Raised when input validation fails."""
    pass

class FileGenerationError(ResumeBuilderError):
    """Raised when file generation fails."""
    pass

class AIServiceError(ResumeBuilderError):
    """Raised when AI service encounters an error."""
    pass

def handle_error(error: Exception) -> Dict[str, Union[bool, str, int]]:
    """Handle different types of errors and return appropriate responses."""
    if isinstance(error, ResumeBuilderError):
        status_code = error.status_code
        message = error.message
    elif isinstance(error, ValueError):
        status_code = 400
        message = str(error)
    else:
        status_code = 500
        message = "An unexpected error occurred"
        logger.error(f"Unexpected error: {str(error)}")
    
    response = {
        'success': False,
        'message': message,
        'error_type': error.__class__.__name__
    }
    