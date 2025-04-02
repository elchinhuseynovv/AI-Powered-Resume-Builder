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
    