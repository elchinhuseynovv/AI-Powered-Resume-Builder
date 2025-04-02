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
        
        # Standardize date formats
        experience = self._standardize_dates(experience)
        
        return experience

    def _format_education(self, education: str) -> str:
        """Format the education section with consistent structure."""
        entries = education.split('\n')
        formatted_entries = []
        
        for entry in entries:
            if entry.strip():
                # Extract and format components
                parts = entry.split('-')
                if len(parts) >= 2:
                    degree = parts[0].strip()
                    institution = parts[1].strip()
                    
                    # Extract year if present
                    year_match = re.search(r'\((\d{4})\)', institution)
                    if year_match:
                        year = year_match.group(1)
                        institution = institution.replace(f'({year})', '').strip()
                        formatted_entry = f"{degree} - {institution} ({year})"
                    else:
                        formatted_entry = entry
                        
                    formatted_entries.append(formatted_entry)
                else:
                    formatted_entries.append(entry)
        
        return '\n'.join(formatted_entries)

    def _format_skills(self, skills: List[str]) -> List[str]:
        """Format and organize skills."""
        formatted_skills = []
        
        for skill in skills:
            # Remove extra spaces and capitalize appropriately
            skill = skill.strip()
            
            # Handle special cases (e.g., programming languages, frameworks)
            if skill.lower() in ['javascript', 'typescript', 'python', 'java', 'c++']:
                formatted_skills.append(skill.capitalize())
            elif skill.lower() in ['react', 'vue', 'angular']:
                formatted_skills.append(skill[0].upper() + skill[1:])
            elif skill.lower().startswith('ms '):
                formatted_skills.append(f"Microsoft {skill[3:].capitalize()}")
            else:
                formatted_skills.append(skill.capitalize())
        
        return sorted(formatted_skills)

    def _standardize_dates(self, text: str) -> str:
        """Standardize date formats in text."""
        # Match common date patterns
        date_patterns = [
            (r'(\d{1,2})/(\d{4})', r'\2'),  # MM/YYYY -> YYYY
            (r'(\w+)\s+(\d{4})', r'\1 \2'),  # Month YYYY
            (r'(\d{4})-(\d{4})', r'\1 - \2'),  # YYYY-YYYY -> YYYY - YYYY
        ]
        
        formatted_text = text
        for pattern, replacement in date_patterns:
            formatted_text = re.sub(pattern, replacement, formatted_text)
        
        return formatted_text
