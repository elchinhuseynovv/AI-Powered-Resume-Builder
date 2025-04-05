"""Resume analysis module for enhanced resume evaluation."""
import re
from typing import Dict, List, Union, Optional
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import logging
from collections import Counter

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
            'software': ['python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes', 'microservices'],
            'data_science': ['python', 'machine learning', 'ai', 'deep learning', 'tensorflow', 'pytorch', 'nlp'],
            'devops': ['aws', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd'],
            'frontend': ['react', 'vue', 'angular', 'javascript', 'typescript', 'css', 'html'],
            'backend': ['python', 'java', 'node.js', 'sql', 'rest api', 'microservices', 'redis'],
            'marketing': ['seo', 'analytics', 'social media', 'content', 'campaign', 'marketing automation'],
            'finance': ['accounting', 'budget', 'financial analysis', 'forecasting', 'risk management'],
            'sales': ['revenue', 'sales', 'negotiation', 'client', 'business development', 'crm']
        }
        
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem-solving',
            'analytical', 'creativity', 'adaptability', 'time management'
        ]

    def analyze_resume(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Perform comprehensive resume analysis."""
        try:
            analysis = {
                'keyword_analysis': self._analyze_keywords(data),
                'content_score': self._score_content(data),
                'improvement_suggestions': self._generate_suggestions(data),
                'ats_compatibility': self._check_ats_compatibility(data),
                'industry_alignment': self._analyze_industry_alignment(data),
                'action_verbs_usage': self._analyze_action_verbs(data['experience']),
                'readability_score': self._calculate_readability_score(data),
                'soft_skills_analysis': self._analyze_soft_skills(data),
                'technical_skills_depth': self._analyze_technical_skills(data),
                'experience_impact': self._analyze_experience_impact(data)
            }
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            return {'error': str(e)}

    def _analyze_keywords(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze keyword usage and relevance with improved metrics."""
        try:
            text = f"{data['experience']} {' '.join(data['skills'])}"
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Extract keywords with POS tagging
            tagged_words = pos_tag(tokens)
            keywords = [
                word.lower() for word, tag in tagged_words 
                if word.isalnum() and word not in stop_words 
                and tag in ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'VB', 'VBD', 'VBG', 'VBN']
            ]
            
            # Calculate keyword frequency and density
            keyword_freq = Counter(keywords)
            total_words = len(tokens)
            keyword_density = len(set(keywords)) / total_words if total_words > 0 else 0
            
            # Identify key phrases (bigrams)
            bigrams = list(zip(keywords[:-1], keywords[1:]))
            bigram_freq = Counter(bigrams)
            
            return {
                'top_keywords': sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10],
                'top_phrases': sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)[:5],
                'keyword_density': keyword_density,
                'unique_keywords': len(set(keywords)),
                'total_keywords': len(keywords)
            }
        except Exception as e:
            logger.error(f"Keyword analysis error: {e}")
            return {
                'top_keywords': [],
                'top_phrases': [],
                'keyword_density': 0,
                'unique_keywords': 0,
                'total_keywords': 0
            }

    def _calculate_readability_score(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Calculate readability metrics for the resume."""
        try:
            text = data['experience']
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Calculate basic metrics
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Calculate Flesch Reading Ease score
            total_syllables = sum(self._count_syllables(word) for word in words)
            if len(sentences) > 0 and len(words) > 0:
                flesch_score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (total_syllables / len(words))
            else:
                flesch_score = 0
                
            return {
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_word_length': round(avg_word_length, 2),
                'flesch_score': round(flesch_score, 2),
                'readability_level': self._get_readability_level(flesch_score)
            }
        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return {
                'avg_sentence_length': 0,
                'avg_word_length': 0,
                'flesch_score': 0,
                'readability_level': 'Error calculating readability'
            }

    def _count_syllables(self, word: str) -> int:
        """Count the number of syllables in a word."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        on_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
            
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2:
            count += 1
        if count == 0:
            count = 1
            
        return count

    def _get_readability_level(self, score: float) -> str:
        """Convert Flesch score to readability level."""
        if score >= 90:
            return 'Very Easy'
        elif score >= 80:
            return 'Easy'
        elif score >= 70:
            return 'Fairly Easy'
        elif score >= 60:
            return 'Standard'
        elif score >= 50:
            return 'Fairly Difficult'
        elif score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'

    def _analyze_soft_skills(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze presence and usage of soft skills."""
        try:
            text = data['experience'].lower()
            found_skills = []
            
            for skill in self.soft_skills:
                if skill in text:
                    found_skills.append(skill)
            
            coverage = len(found_skills) / len(self.soft_skills) * 100
            
            return {
                'identified_skills': found_skills,
                'coverage_percentage': round(coverage, 2),
                'missing_important_skills': list(set(self.soft_skills) - set(found_skills)),
                'recommendations': self._generate_soft_skills_recommendations(found_skills)
            }
        except Exception as e:
            logger.error(f"Soft skills analysis error: {e}")
            return {
                'identified_skills': [],
                'coverage_percentage': 0,
                'missing_important_skills': [],
                'recommendations': []
            }

    def _analyze_technical_skills(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze technical skills depth and relevance."""
        try:
            skills = data['skills'] if isinstance(data['skills'], list) else data['skills'].split(',')
            skills = [skill.strip().lower() for skill in skills]
            
            # Categorize skills
            categories = {
                'programming_languages': [],
                'frameworks': [],
                'tools': [],
                'databases': [],
                'cloud': [],
                'other': []
            }
            
            for skill in skills:
                if skill in ['python', 'java', 'javascript', 'c++', 'ruby', 'php']:
                    categories['programming_languages'].append(skill)
                elif skill in ['react', 'angular', 'vue', 'django', 'flask', 'spring']:
                    categories['frameworks'].append(skill)
                elif skill in ['git', 'docker', 'kubernetes', 'jenkins']:
                    categories['tools'].append(skill)
                elif skill in ['mysql', 'postgresql', 'mongodb', 'redis']:
                    categories['databases'].append(skill)
                elif skill in ['aws', 'azure', 'gcp', 'heroku']:
                    categories['cloud'].append(skill)
                else:
                    categories['other'].append(skill)
            
            return {
                'categorized_skills': categories,
                'skill_distribution': {
                    category: len(skills) 
                    for category, skills in categories.items()
                },
                'total_skills': len(skills),
                'skill_balance_score': self._calculate_skill_balance(categories)
            }
        except Exception as e:
            logger.error(f"Technical skills analysis error: {e}")
            return {
                'categorized_skills': {},
                'skill_distribution': {},
                'total_skills': 0,
                'skill_balance_score': 0
            }

    def _calculate_skill_balance(self, categories: Dict[str, List[str]]) -> float:
        """Calculate balance score for technical skills distribution."""
        total_skills = sum(len(skills) for skills in categories.values())
        if total_skills == 0:
            return 0
            
        # Calculate ideal distribution percentages
        ideal_distribution = {
            'programming_languages': 0.25,
            'frameworks': 0.25,
            'tools': 0.20,
            'databases': 0.15,
            'cloud': 0.10,
            'other': 0.05
        }
        
        # Calculate actual distribution
        actual_distribution = {
            category: len(skills) / total_skills
            for category, skills in categories.items()
        }
        
        # Calculate balance score (100 = perfect balance, 0 = completely unbalanced)
        balance_score = 100 - sum(
            abs(ideal_distribution[cat] - actual_distribution.get(cat, 0)) * 100
            for cat in ideal_distribution
        )
        
        return max(0, min(100, balance_score))

    def _analyze_experience_impact(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Analyze the impact and effectiveness of experience descriptions."""
        try:
            experience = data['experience']
            sentences = sent_tokenize(experience)
            
            # Metrics tracking
            metrics = {
                'quantified_achievements': 0,
                'leadership_indicators': 0,
                'technical_implementations': 0,
                'impact_statements': 0
            }
            
            # Patterns for analysis
            patterns = {
                'quantified': r'\d+%|\$\d+|\d+ [a-zA-Z]+',
                'leadership': r'led|managed|supervised|mentored|coordinated|directed',
                'technical': r'implemented|developed|built|designed|architected',
                'impact': r'improved|increased|reduced|enhanced|optimized|streamlined'
            }
            
            for sentence in sentences:
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, sentence, re.IGNORECASE):
                        if pattern_name == 'quantified':
                            metrics['quantified_achievements'] += 1
                        elif pattern_name == 'leadership':
                            metrics['leadership_indicators'] += 1
                        elif pattern_name == 'technical':
                            metrics['technical_implementations'] += 1
                        elif pattern_name == 'impact':
                            metrics['impact_statements'] += 1
            
            # Calculate impact score
            total_sentences = len(sentences)
            if total_sentences > 0:
                impact_score = sum(metrics.values()) / (total_sentences * 2) * 100  # Normalize to 100
            else:
                impact_score = 0
            
            return {
                'metrics': metrics,
                'impact_score': round(min(100, impact_score), 2),
                'recommendations': self._generate_impact_recommendations(metrics, total_sentences)
            }
        except Exception as e:
            logger.error(f"Experience impact analysis error: {e}")
            return {
                'metrics': {},
                'impact_score': 0,
                'recommendations': []
            }

    def _generate_impact_recommendations(self, metrics: Dict[str, int], total_sentences: int) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []
        
        if metrics['quantified_achievements'] / total_sentences < 0.3:
            recommendations.append("Add more quantifiable achievements (numbers, percentages, or dollar amounts)")
        
        if metrics['leadership_indicators'] == 0:
            recommendations.append("Include examples of leadership or team coordination experience")
        
        if metrics['technical_implementations'] / total_sentences < 0.25:
            recommendations.append("Add more specific technical implementation details")
        
        if metrics['impact_statements'] / total_sentences < 0.4:
            recommendations.append("Focus more on the impact and results of your work")
        
        return recommendations

    def _generate_soft_skills_recommendations(self, found_skills: List[str]) -> List[str]:
        """Generate recommendations for soft skills improvement."""
        critical_skills = {'leadership', 'communication', 'problem-solving'}
        recommendations = []
        
        missing_critical = critical_skills - set(found_skills)
        if missing_critical:
            recommendations.append(
                f"Consider adding examples demonstrating: {', '.join(missing_critical)}"
            )
        
        if len(found_skills) < 5:
            recommendations.append(
                "Include more soft skills and provide specific examples of their application"
            )
        
        return recommendations

    def _check_ats_compatibility(self, data: Dict[str, Union[str, List[str]]]) -> Dict:
        """Check resume compatibility with ATS systems."""
        try:
            issues = []
            score = 100
            
            # Check content length
            if len(data['experience'].split()) < 50:
                issues.append('Experience section might be too brief for ATS parsing')
                score -= 20
            
            # Check skills format
            if isinstance(data['skills'], str):
                if ',' not in data['skills']:
                    issues.append('Skills should be comma-separated for better ATS parsing')
                    score -= 15
            
            # Check for common formatting issues
            if any(char in data['experience'] for char in ['•', '►', '→']):
                issues.append('Replace special characters with standard bullet points')
                score -= 10
            
            # Check for proper section headings
            if not all(section in data['experience'].lower() 
                      for section in ['experience', 'education', 'skills']):
                issues.append('Ensure all major sections have clear headings')
                score -= 15
            