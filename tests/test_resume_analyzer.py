"""Tests for the resume analyzer module."""
import pytest
from resume_analyzer import ResumeAnalyzer

@pytest.fixture
def analyzer():
    return ResumeAnalyzer()

@pytest.fixture
def sample_data():
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '123-456-7890',
        'job_title': 'Software Developer',
        'company': 'Tech Corp',
        'education': 'BS Computer Science - University (2020)',
        'experience': '''
        • Developed and maintained web applications using React and Node.js
        • Increased system performance by 40% through optimization
        • Led a team of 5 developers on critical projects
        ''',
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS']
    }

def test_analyze_resume(analyzer, sample_data):
    """Test complete resume analysis."""
    analysis = analyzer.analyze_resume(sample_data)
    
    assert isinstance(analysis, dict)
    assert 'keyword_analysis' in analysis
    assert 'content_score' in analysis
    assert 'improvement_suggestions' in analysis
    assert 'ats_compatibility' in analysis

def test_keyword_analysis(analyzer, sample_data):
    """Test keyword analysis functionality."""
    analysis = analyzer._analyze_keywords(sample_data)
    
    assert isinstance(analysis, dict)
    assert 'top_keywords' in analysis
    assert 'keyword_density' in analysis
    assert isinstance(analysis['top_keywords'], list)
    assert 0 <= analysis['keyword_density'] <= 1

def test_score_experience(analyzer):
    """Test experience scoring."""
    experience = '''
    • Increased revenue by 25% through strategic initiatives
    • Managed a team of 10 employees
    • Developed new software features
    '''
    score = analyzer._score_experience(experience)
    
    assert isinstance(score, int)
    assert 0 <= score <= 100

def test_ats_compatibility(analyzer, sample_data):
    """Test ATS compatibility check."""
    ats_analysis = analyzer._check_ats_compatibility(sample_data)
    
    assert isinstance(ats_analysis, dict)
    assert 'score' in ats_analysis
    assert 'issues' in ats_analysis
    assert 'is_ats_friendly' in ats_analysis
    assert isinstance(ats_analysis['score'], int)
    assert isinstance(ats_analysis['issues'], list)
    assert isinstance(ats_analysis['is_ats_friendly'], bool)

def test_industry_alignment(analyzer, sample_data):
    """Test industry alignment analysis."""
    alignment = analyzer._analyze_industry_alignment(sample_data)
    
    assert isinstance(alignment, dict)
    assert 'industry_matches' in alignment
    assert 'best_match' in alignment
    assert isinstance(alignment['best_match']['score'], int)

def test_action_verbs_analysis(analyzer, sample_data):
    """Test action verbs analysis."""
    verbs_analysis = analyzer._analyze_action_verbs(sample_data['experience'])
    
    assert isinstance(verbs_analysis, dict)
    assert 'total_used' in verbs_analysis
    assert 'unique_used' in verbs_analysis
    assert 'verbs_found' in verbs_analysis
    assert 'suggestions' in verbs_analysis
