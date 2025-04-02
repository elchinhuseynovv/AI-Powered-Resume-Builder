"""Module for formatting and styling resume content."""
import re
from typing import Dict, List, Union
import logging

logger = logging.getLogger(__name__)

class ResumeFormatter:
    """Class for formatting and styling resume content."""
    
    def __init__(self):
        self.date_formats = {
            'full': '%B %Y',
            'short': '%b %Y',
            'numeric': '%m/%Y'
        }

    def format_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict[str, Union[str, List[str]]]:
        """Format all sections of the resume."""
        try:
            formatted_data = data.copy()
            formatted_data['experience'] = self._format_experience(data['experience'])
            formatted_data['education'] = self._format_education(data['education'])
            formatted_data['skills'] = self._format_skills(data['skills'])
            return formatted_data
        except Exception as e:
            logger.error(f"Error formatting resume: {e}")
            return data

    def _format_experience(self, experience: str) -> str:
        """Format the experience section with improved structure."""
        # Split into bullet points if not already
        if not experience.strip().startswith('•'):
            points = experience.split('\n')
            formatted_points = []
            
            for point in points:
                point = point.strip()
                if point:
                    # Capitalize first letter
                    point = point[0].upper() + point[1:]
                    # Add bullet point if not present
                    if not point.startswith('•'):
                        point = f'• {point}'
                    # Add period if missing
                    if not point.endswith(('.', '!', '?')):
                        point += '.'
                    formatted_points.append(point)
            
            experience = '\n'.join(formatted_points)
        