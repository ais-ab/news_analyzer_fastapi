"""
Enhanced scraping utilities for better article extraction
"""
import requests
import time
import random
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
import json

class ScrapingEnhancer:
    """Enhanced scraping utilities"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Content quality filters
        self.min_content_length = 200
        self.max_content_length = 50000
        self.min_title_length = 10
        self.max_title_length = 200
        
        # Common spam/ad patterns
        self.spam_patterns = [
            r'\b(sponsored|advertisement|advertorial|promoted)\b',
            r'\b(click here|read more|subscribe now|sign up)\b',
            r'\b(free trial|limited time|act now|don\'t miss)\b',
            r'\b(earn money|make money|work from home|get rich)\b',
            r'\b(weight loss|diet pills|miracle cure|secret formula)\b'
        ]
        
        # Quality indicators
        self.quality_indicators = [
            r'\b(analysis|report|study|research|survey)\b',
            r'\b(earnings|revenue|profit|loss|quarterly)\b',
            r'\b(policy|regulation|legislation|government)\b',
            r'\b(technology|innovation|development|launch)\b',
            r'\b(market|trading|investment|portfolio)\b'
        ]

    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)

    def add_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def is_quality_content(self, content: str, title: str = "") -> bool:
        """Check if content meets quality standards"""
        if not content or len(content.strip()) < self.min_content_length:
            return False
            
        if len(content) > self.max_content_length:
            return False
            
        # Check for spam patterns
        content_lower = content.lower()
        for pattern in self.spam_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return False
        
        # Check for quality indicators
        quality_score = 0
        for pattern in self.quality_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                quality_score += 1
        
        # Require at least one quality indicator
        return quality_score > 0

    def clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted patterns
        content = re.sub(r'Share this article|Follow us|Subscribe|Newsletter', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Read more|Continue reading|Full story', '', content, flags=re.IGNORECASE)
        
        # Remove social media links
        content = re.sub(r'https?://(www\.)?(facebook|twitter|linkedin|instagram)\.com/[^\s]+', '', content)
        
        return content.strip()

    def extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from content"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter and count
        word_count = {}
        for word in words:
            if word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]

    def categorize_content(self, content: str, title: str = "") -> str:
        """Categorize content based on keywords"""
        text = f"{title} {content}".lower()
        
        categories = {
            'earnings': ['earnings', 'revenue', 'profit', 'quarterly', 'financial', 'results'],
            'markets': ['market', 'trading', 'stock', 'investor', 'portfolio', 'index'],
            'economy': ['economy', 'economic', 'gdp', 'inflation', 'unemployment', 'fed'],
            'technology': ['technology', 'tech', 'software', 'digital', 'innovation', 'startup'],
            'politics': ['politics', 'political', 'government', 'policy', 'regulation', 'law'],
            'cryptocurrency': ['crypto', 'bitcoin', 'blockchain', 'ethereum', 'digital currency'],
            'real_estate': ['real estate', 'housing', 'property', 'mortgage', 'construction'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind', 'fossil fuel']
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Return category with highest score
        if scores:
            return max(scores, key=scores.get)
        return 'general'

class ContentFilter:
    """Content filtering utilities"""
    
    def __init__(self):
        self.generic_titles = [
            'latest updates', 'breaking news', 'top stories', 'news roundup',
            'from our experts', 'politics explained', 'market update',
            'daily briefing', 'morning report', 'evening update'
        ]
        
        self.generic_content_patterns = [
            r'^[A-Z\s]+$',  # All caps titles
            r'^\d+\.\s*$',  # Just numbers
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # Two word titles
        ]

    def is_generic_content(self, title: str, content: str) -> bool:
        """Check if content is too generic"""
        title_lower = title.lower().strip()
        content_lower = content.lower().strip()
        
        # Check for generic titles
        for generic in self.generic_titles:
            if generic in title_lower:
                return True
        
        # Check for generic patterns
        for pattern in self.generic_content_patterns:
            if re.match(pattern, title):
                return True
        
        # Check for very short content
        if len(content.strip()) < 100:
            return True
        
        # Check for repetitive content
        words = content_lower.split()
        if len(set(words)) < len(words) * 0.3:  # Less than 30% unique words
            return True
        
        return False

class ProxyManager:
    """Proxy management for scraping"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.proxy_rotation = 0
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the pool"""
        self.proxies.append(proxy)
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        self.current_proxy = self.proxies[self.proxy_rotation % len(self.proxies)]
        self.proxy_rotation += 1
        return self.current_proxy
    
    def test_proxy(self, proxy: str) -> bool:
        """Test if proxy is working"""
        try:
            response = requests.get(
                'https://httpbin.org/ip',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

def enhance_article_data(article: Dict) -> Dict:
    """Enhance article data with additional processing"""
    enhancer = ScrapingEnhancer()
    filter = ContentFilter()
    
    # Clean content
    article['content'] = enhancer.clean_content(article.get('content', ''))
    article['title'] = enhancer.clean_content(article.get('title', ''))
    
    # Extract keywords
    article['keywords'] = enhancer.extract_keywords(article['content'])
    
    # Categorize content
    article['category'] = enhancer.categorize_content(article['content'], article['title'])
    
    # Check quality
    article['is_quality'] = enhancer.is_quality_content(article['content'], article['title'])
    article['is_generic'] = filter.is_generic_content(article['title'], article['content'])
    
    # Add metadata
    article['word_count'] = len(article['content'].split())
    article['processed_at'] = time.time()
    
    return article 