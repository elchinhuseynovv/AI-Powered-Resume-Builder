"""Tests for the resume formatter module."""
import pytest
from resume_formatter import ResumeFormatter

@pytest.fixture
def formatter():
    return ResumeFormatter()

@pytest.fixture
def sample_data():
    return {
        'name': 'john doe',
        'email': 'JOHN@EXAMPLE.COM',
        'phone': '1234567890',
        'job_title': 'software developer',
        'education': 'BS Computer Science - University (2020)',
        'experience': '''developed web applications
        managed team projects
        implemented new features''',
        'skills': ['python', 'Javascript', 'REACT', 'node.js', 'AWS']
    }

def test_format_resume(formatter, sample_data):
    """Test complete resume formatting."""
    formatted = formatter.format_resume(sample_data)
    
    assert isinstance(formatted, dict)
    assert all(key in formatted for key in sample_data.keys())
    assert formatted['experience'].startswith('•')

def test_format_experience(formatter):
    """Test experience formatting."""
    experience = '''developed web applications
    managed team projects'''
    
    formatted = formatter._format_experience(experience)
    
    assert formatted.startswith('•')
    assert all(line.strip().startswith('•') for line in formatted.split('\n') if line.strip())
    assert all(line.strip().endswith('.') for line in formatted.split('\n') if line.strip())

def test_format_education(formatter):
    """Test education formatting."""
    education = '''BS Computer Science - University (2020)
    MS Data Science - Tech University (2022)'''
    
    formatted = formatter._format_education(education)
    
    assert isinstance(formatted, str)
    assert '2020' in formatted
    assert '2022' in formatted
    assert 'University' in formatted

def test_format_skills(formatter):
    """Test skills formatting."""
    skills = ['python', 'Javascript', 'REACT', 'ms excel']
    
    formatted = formatter._format_skills(skills)
    
    assert isinstance(formatted, list)
    assert 'Python' in formatted
    assert 'JavaScript' in formatted
    assert 'React' in formatted
    assert 'Microsoft Excel' in formatted

def test_standardize_dates(formatter):
    """Test date standardization."""
    text = '''01/2020 to 12/2021
    January 2020
    2020-2021'''
    
    formatted = formatter._standardize_dates(text)
    
    assert '2020' in formatted
    assert '2021' in formatted
    assert '01/2020' not in formatted

def test_apply_style_guide(formatter, sample_data):
    """Test style guide application."""
    styled = formatter.apply_style_guide(sample_data)
    
    assert styled['name'] == 'John Doe'
    assert styled['email'] == 'john@example.com'
    assert styled['job_title'] == 'Software Developer'
    assert '(' in styled['phone'] and ')' in styled['phone']

def test_format_phone_number(formatter):
    """Test phone number formatting."""
    assert formatter._format_phone_number('1234567890') == '(123) 456-7890'
    assert formatter._format_phone_number('11234567890') == '+1 (123) 456-7890'
    assert formatter._format_phone_number('123-456-7890') == '(123) 456-7890'

def test_generate_section_headers(formatter):
    """Test section header generation."""
    headers = formatter.generate_section_headers()
    
    assert isinstance(headers, dict)
    assert 'education' in headers
    assert 'experience' in headers
    assert 'skills' in headers
    assert all(isinstance(header, str) for header in headers.values())

def test_format_dates(formatter):
    """Test date formatting."""
    assert 'January' in formatter.format_dates('2020-01-15', 'full')
    assert '01/' in formatter.format_dates('2020-01-15', 'numeric')
    
    # Test invalid date handling
    assert formatter.format_dates('invalid-date') == 'invalid-date'

def test_empty_inputs(formatter):
    """Test handling of empty inputs."""
    assert formatter._format_experience('') == ''
    assert formatter._format_education('') == ''
    assert formatter._format_skills([]) == []

def test_invalid_inputs(formatter):
    """Test handling of invalid inputs."""
    with pytest.raises(Exception):
        formatter.format_resume(None)
    
    with pytest.raises(Exception):
        formatter.apply_style_guide(None)