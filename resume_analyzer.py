"""Resume analysis module for enhanced resume evaluation."""
import re
from typing import Dict, List, Union
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """Class for analyzing resume content and providing insights."""
    
    def __init__(self):
        self.action_verbs = [
            'achieved', 'improved', 'developed', 'led', 'managed', 'created',
            'implemented', 'increased', 'decreased', 'negotiated', 'coordinated',
            'supervised', 'trained', 'designed', 'launched', 'spearheaded',
            'established', 'executed', 'generated', 'reduced', 'streamlined'
        ]
        
        self.industry_keywords = {
            'software': ['python', 'javascript', 'react', 'node', 'aws', 'docker'],
            'marketing': ['seo', 'analytics', 'social media', 'content', 'campaign'],
            'finance': ['accounting', 'budget', 'financial analysis', 'forecasting'],
            'sales': ['revenue', 'sales', 'negotiation', 'client', 'business development']
        }

    def analyze_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Perform comprehensive resume analysis."""
        try:
            analysis = {
                'keyword_analysis': self._analyze_keywords(data),
                'content_score': self._score_content(data),
                'improvement_suggestions': self._generate_suggestions(data),
                'ats_compatibility': self._check_ats_compatibility(data),
                'industry_alignment': self._analyze_industry_alignment(data),
                'action_verbs_usage': self._analyze_action_verbs(data['experience'])
            }
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return {'error': str(e)}

  