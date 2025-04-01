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

    def _analyze_keywords(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze keyword usage and relevance."""
        text = f"{data['experience']} {' '.join(data['skills'])}"
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
        keyword_freq = {}
        
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
            
        return {
            'top_keywords': sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10],
            'keyword_density': len(set(keywords)) / len(keywords) if keywords else 0,
            'unique_keywords': len(set(keywords))
        }

    def _score_content(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Score different aspects of the resume."""
        scores = {
            'experience': self._score_experience(data['experience']),
            'skills': min(len(data['skills']) * 10, 100),
            'education': len(data['education'].split('\n')) * 20,
            'overall_quality': self._calculate_overall_quality(data)
        }
        
        return scores

    def _score_experience(self, experience: str) -> int:
        """Score the experience section based on various factors."""
        words = experience.split()
        metrics = re.findall(r'\d+%|\$\d+|\d+ years?', experience.lower())
        action_verbs_used = sum(1 for word in words if word.lower() in self.action_verbs)
        
        length_score = min(len(words) / 10, 50)
        action_verbs_score = min(action_verbs_used * 5, 30)
        metrics_score = min(len(metrics) * 10, 20)
        
        total_score = length_score + action_verbs_score + metrics_score
        return min(int(total_score), 100)

    def _calculate_overall_quality(self, data: Dict[str, Union[str, List[str]]]) -> int:
        """Calculate overall resume quality score."""
        scores = []
        
        # Experience quality
        exp_score = self._score_experience(data['experience'])
        scores.append(exp_score * 0.4)  # 40% weight
        
        # Skills breadth
        skills_score = min(len(data['skills']) * 10, 100)
        scores.append(skills_score * 0.3)  # 30% weight
        
        # Education completeness
        edu_score = min(len(data['education'].split('\n')) * 25, 100)
        scores.append(edu_score * 0.2)  # 20% weight
        
        # Contact information completeness
        contact_score = 100 if all([data['email'], data['phone']]) else 50
        scores.append(contact_score * 0.1)  # 10% weight
        
        return min(int(sum(scores)), 100)
