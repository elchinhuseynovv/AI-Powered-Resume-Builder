"""Module for formatting and styling resume content."""
import re
from typing import Dict, List, Union, Optional
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class ResumeFormatter:
    """Class for formatting and styling resume content."""
    
    def __init__(self):
        self.date_formats = {
            'full': '%B %Y',
            'short': '%b %Y',
            'numeric': '%m/%Y'
        }
        
        self.style_config = {
            'font_family': 'Inter, sans-serif',
            'primary_color': '#3498db',
            'secondary_color': '#2c3e50',
            'text_color': '#333333',
            'background_color': '#ffffff',
            'accent_color': '#e74c3c',
            'spacing': {
                'section': '2rem',
                'item': '1rem',
                'paragraph': '0.5rem'
            }
        }
        
        self.section_order = [
            'header',
            'summary',
            'experience',
            'education',
            'skills',
            'projects',
            'certifications'
        ]

    def format_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict[str, Union[str, List[str]]]:
        """Format all sections of the resume with enhanced styling."""
        try:
            formatted_data = data.copy()
            
            # Apply consistent formatting to all sections
            formatted_data['name'] = self._format_name(data.get('name', ''))
            formatted_data['contact'] = self._format_contact_info(data)
            formatted_data['experience'] = self._format_experience(data.get('experience', ''))
            formatted_data['education'] = self._format_education(data.get('education', ''))
            formatted_data['skills'] = self._format_skills(data.get('skills', []))
            
            # Add optional sections if present
            if 'summary' in data:
                formatted_data['summary'] = self._format_summary(data['summary'])
            if 'projects' in data:
                formatted_data['projects'] = self._format_projects(data['projects'])
            if 'certifications' in data:
                formatted_data['certifications'] = self._format_certifications(data['certifications'])
            
            return formatted_data
        except Exception as e:
            logger.error(f"Error formatting resume: {e}")
            return data

    def _format_name(self, name: str) -> str:
        """Format name with proper capitalization."""
        try:
            # Handle multiple parts of the name
            name_parts = name.strip().split()
            formatted_parts = []
            
            for part in name_parts:
                # Handle hyphenated names
                if '-' in part:
                    formatted_parts.append('-'.join(word.capitalize() for word in part.split('-')))
                # Handle McName or MacName
                elif part.lower().startswith(('mc', 'mac')):
                    formatted_parts.append(part[:2].capitalize() + part[2:3].capitalize() + part[3:].lower())
                else:
                    formatted_parts.append(part.capitalize())
            
            return ' '.join(formatted_parts)
        except Exception as e:
            logger.error(f"Name formatting error: {e}")
            return name

    def _format_contact_info(self, data: Dict[str, str]) -> Dict[str, str]:
        """Format contact information consistently."""
        try:
            contact_info = {}
            
            # Format email
            if 'email' in data:
                contact_info['email'] = data['email'].lower()
            
            # Format phone number
            if 'phone' in data:
                contact_info['phone'] = self._format_phone_number(data['phone'])
            
            # Format location if present
            if 'location' in data:
                contact_info['location'] = self._format_location(data['location'])
            
            # Format social links if present
            if 'linkedin' in data:
                contact_info['linkedin'] = self._format_social_link(data['linkedin'], 'linkedin')
            if 'github' in data:
                contact_info['github'] = self._format_social_link(data['github'], 'github')
            
            return contact_info
        except Exception as e:
            logger.error(f"Contact info formatting error: {e}")
            return {}

    def _format_experience(self, experience: str) -> str:
        """Format the experience section with enhanced structure."""
        try:
            if not experience:
                return ""
            
            # Split into bullet points if not already
            lines = experience.split('\n')
            formatted_lines = []
            
            current_company = None
            current_position = None
            current_date = None
            bullet_points = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a company/position header
                if ':' in line and not line.startswith('•'):
                    # Save previous entry if exists
                    if current_company and bullet_points:
                        formatted_lines.extend(self._format_experience_entry(
                            current_company, current_position, current_date, bullet_points
                        ))
                        bullet_points = []
                    
                    # Parse new entry header
                    parts = line.split(':')
                    current_company = parts[0].strip()
                    if len(parts) > 1:
                        position_parts = parts[1].split('(')
                        current_position = position_parts[0].strip()
                        current_date = position_parts[1].strip(')') if len(position_parts) > 1 else None
                else:
                    # Add bullet point
                    point = line if line.startswith('•') else f"• {line}"
                    if not point.endswith(('.', '!', '?')):
                        point += '.'
                    bullet_points.append(point)
            
            # Add last entry
            if current_company and bullet_points:
                formatted_lines.extend(self._format_experience_entry(
                    current_company, current_position, current_date, bullet_points
                ))
            
            return '\n'.join(formatted_lines)
        except Exception as e:
            logger.error(f"Experience formatting error: {e}")
            return experience

    def _format_experience_entry(self, company: str, position: str, date: str, bullets: List[str]) -> List[str]:
        """Format a single experience entry."""
        entry = []
        entry.append(f"{company}")
        if position:
            entry.append(f"{position}")
        if date:
            entry.append(f"{self._standardize_dates(date)}")
        entry.extend(bullets)
        return entry

    def _format_education(self, education: str) -> str:
        """Format the education section with consistent structure."""
        try:
            if not education:
                return ""
            
            entries = education.split('\n')
            formatted_entries = []
            
            for entry in entries:
                if not entry.strip():
                    continue
                
                # Parse education entry
                parts = entry.split('-')
                if len(parts) >= 2:
                    degree = parts[0].strip()
                    institution = parts[1].strip()
                    
                    # Extract and format year if present
                    year_match = re.search(r'\((\d{4})\)', institution)
                    if year_match:
                        year = year_match.group(1)
                        institution = institution.replace(f'({year})', '').strip()
                        formatted_entry = f"{self._format_degree(degree)} - {institution} ({year})"
                    else:
                        formatted_entry = f"{self._format_degree(degree)} - {institution}"
                    
                    formatted_entries.append(formatted_entry)
                else:
                    formatted_entries.append(entry)
            
            return '\n'.join(formatted_entries)
        except Exception as e:
            logger.error(f"Education formatting error: {e}")
            return education

    def _format_degree(self, degree: str) -> str:
        """Format degree with proper abbreviations and capitalization."""
        degree = degree.strip()
        
        # Common degree abbreviations
        abbreviations = {
            'bachelor of science': 'BS',
            'bachelor of arts': 'BA',
            'master of science': 'MS',
            'master of arts': 'MA',
            'doctor of philosophy': 'PhD',
            'master of business administration': 'MBA'
        }
        
        # Check for known abbreviations
        degree_lower = degree.lower()
        for full, abbr in abbreviations.items():
            if degree_lower.startswith(full):
                return degree.replace(full, abbr, 1)
        
        # Capitalize each word if no abbreviation found
        return ' '.join(word.capitalize() for word in degree.split())

    def _format_skills(self, skills: List[str]) -> List[str]:
        """Format and organize skills with categories."""
        try:
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',')]
            
            # Categorize skills
            categorized_skills = {
                'Programming Languages': [],
                'Frameworks & Libraries': [],
                'Tools & Technologies': [],
                'Soft Skills': [],
                'Other': []
            }
            
            for skill in skills:
                skill = skill.strip()
                
                # Determine category and format skill
                if skill.lower() in ['python', 'java', 'javascript', 'typescript', 'c++', 'ruby', 'php']:
                    formatted_skill = self._format_programming_language(skill)
                    categorized_skills['Programming Languages'].append(formatted_skill)
                elif skill.lower() in ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js']:
                    formatted_skill = self._format_framework(skill)
                    categorized_skills['Frameworks & Libraries'].append(formatted_skill)
                elif skill.lower() in ['git', 'docker', 'kubernetes', 'aws', 'azure']:
                    formatted_skill = skill.upper() if len(skill) <= 3 else skill.capitalize()
                    categorized_skills['Tools & Technologies'].append(formatted_skill)
                elif skill.lower() in ['leadership', 'communication', 'teamwork', 'problem-solving']:
                    formatted_skill = skill.capitalize()
                    categorized_skills['Soft Skills'].append(formatted_skill)
                else:
                    formatted_skill = skill.capitalize()
                    categorized_skills['Other'].append(formatted_skill)
            
            # Remove empty categories and sort skills within categories
            return {
                category: sorted(skills)
                for category, skills in categorized_skills.items()
                if skills
            }
        except Exception as e:
            logger.error(f"Skills formatting error: {e}")
            return skills

    def _format_programming_language(self, language: str) -> str:
        """Format programming language names correctly."""
        language = language.lower()
        special_cases = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'c++': 'C++',
            'c#': 'C#',
            'php': 'PHP',
            'ruby': 'Ruby'
        }
        return special_cases.get(language, language.capitalize())

    def _format_framework(self, framework: str) -> str:
        """Format framework names correctly."""
        framework = framework.lower()
        special_cases = {
            'react': 'React',
            'angular': 'Angular',
            'vue': 'Vue.js',
            'node.js': 'Node.js',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring'
        }
        return special_cases.get(framework, framework.capitalize())

    def _format_summary(self, summary: str) -> str:
        """Format professional summary section."""
        try:
            if not summary:
                return ""
            
            # Clean and normalize text
            summary = summary.strip()
            
            # Ensure proper sentence structure
            sentences = [s.strip() for s in summary.split('.') if s.strip()]
            formatted_sentences = []
            
            for sentence in sentences:
                # Capitalize first letter if needed
                if sentence and not sentence[0].isupper():
                    sentence = sentence[0].upper() + sentence[1:]
                # Add period if missing
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                formatted_sentences.append(sentence)
            
            return ' '.join(formatted_sentences)
        except Exception as e:
            logger.error(f"Summary formatting error: {e}")
            return summary

    def _format_projects(self, projects: Union[str, List[Dict]]) -> List[Dict]:
        """Format projects section with consistent structure."""
        try:
            if isinstance(projects, str):
                # Parse string into structured format
                lines = projects.split('\n')
                formatted_projects = []
                current_project = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_project:
                            formatted_projects.append(current_project)
                            current_project = {}
                        continue
                    
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.lower().strip()
                        value = value.strip()
                        
                        if key == 'name':
                            current_project['name'] = value
                        elif key in ['description', 'technologies', 'link']:
                            current_project[key] = value
                
                if current_project:
                    formatted_projects.append(current_project)
                
                return formatted_projects
            elif isinstance(projects, list):
                # Format existing structured data
                return [{
                    'name': project.get('name', '').strip(),
                    'description': project.get('description', '').strip(),
                    'technologies': project.get('technologies', '').strip(),
                    'link': project.get('link', '').strip()
                } for project in projects]
            else:
                return []
        except Exception as e:
            logger.error(f"Projects formatting error: {e}")
            return []

    def _format_certifications(self, certifications: Union[str, List[Dict]]) -> List[Dict]:
        """Format certifications section."""
        try:
            if isinstance(certifications, str):
                # Parse string into structured format
                lines = certifications.split('\n')
                formatted_certs = []
                current_cert = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_cert:
                            formatted_certs.append(current_cert)
                            current_cert = {}
                        continue
                    
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.lower().strip()
                        value = value.strip()
                        
                        if key == 'name':
                            current_cert['name'] = value
                        elif key in ['issuer', 'date', 'id']:
                            current_cert[key] = value
                
                if current_cert:
                    formatted_certs.append(current_cert)
                
                return formatted_certs
            elif isinstance(certifications, list):
                # Format existing structured data
                return [{
                    'name': cert.get('name', '').strip(),
                    'issuer': cert.get('issuer', '').strip(),
                    'date': self._standardize_dates(cert.get('date', '')),
                    'id': cert.get('id', '').strip()
                } for cert in certifications]
            else:
                return []
        except Exception as e:
            logger.error(f"Certifications formatting error: {e}")
            return []

    def _standardize_dates(self, date_str: str) -> str:
        """Standardize date formats throughout the resume."""
        try:
            # Handle date ranges
            if ' - ' in date_str:
                start, end = date_str.split(' - ')
                return f"{self._standardize_dates(start)} - {self._standardize_dates(end)}"
            
            # Handle single dates
            date_str = date_str.strip()
            
            # Try parsing common formats
            for fmt in ['%m/%Y', '%B %Y', '%b %Y', '%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%B %Y')
                except ValueError:
                    continue
            
            return date_str
        except Exception as e:
            logger.error(f"Date standardization error: {e}")
            return date_str

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number consistently."""
        try:
            # Remove all non-numeric characters
            digits = re.sub(r'\D', '', phone)
            