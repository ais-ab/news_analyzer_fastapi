"""
Configuration settings for web scraping
"""
from typing import Dict, List

# Spider Configuration
SPIDER_CONFIG = {
    'max_articles_per_source': 20,
    'max_age_days': 3,
    'download_delay': 0.5,
    'concurrent_requests': 8,
    'concurrent_requests_per_domain': 4,
    'download_timeout': 15,
    'retry_times': 3,
    'retry_http_codes': [500, 502, 503, 504, 408, 429, 403],
    'cookies_enabled': True,
    'randomize_download_delay': True,
}

# Content Quality Settings
CONTENT_QUALITY = {
    'min_content_length': 200,
    'max_content_length': 50000,
    'min_title_length': 10,
    'max_title_length': 200,
    'min_word_count': 50,
    'max_word_count': 10000,
}

# User Agents for Rotation
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
]

# Request Headers
REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# Article URL Patterns
ARTICLE_PATTERNS = {
    'positive_patterns': [
        r'/article/', r'/story/', r'/news/', r'/business/', r'/finance/',
        r'/markets/', r'/economy/', r'/technology/', r'/earnings/',
        r'/analysis/', r'/commentary/', r'/opinion/', r'/report/',
        r'/breaking/', r'/latest/', r'/update/', r'/briefing/',
        r'\d{4}/\d{2}/\d{2}', r'\d{4}-\d{2}-\d{2}',  # Date patterns
        r'[a-z-]+-\d+',  # Slug with ID
        r'[a-z-]+/\d{4}',  # Category with year
    ],
    'negative_patterns': [
        r'/login', r'/signup', r'/subscribe', r'/advertise', r'/contact',
        r'/about', r'/privacy', r'/terms', r'/cookie', r'/sitemap',
        r'/search', r'/tag/', r'/category/', r'/author/', r'/user/',
        r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$', r'\.mp4$', r'\.mp3$',
        r'/video/', r'/gallery/', r'/slideshow/', r'/interactive/',
        r'/newsletter', r'/rss', r'/feed', r'/api/', r'/ajax/',
        r'#', r'\?utm_', r'\?fbclid', r'\?ref=', r'\?source=',
        r'/live/', r'/stream/', r'/podcast/', r'/webinar/',
    ]
}

# Content Extraction Selectors
CONTENT_SELECTORS = {
    'article_content': [
        'article',
        '.article-content',
        '.story-content',
        '.post-content',
        '.entry-content',
        '.content-body',
        '.article-body',
        '.story-body',
        '[data-testid="article-content"]',
        '.article__content',
        '.story__content',
        '.post__content',
        '.content',
        '.main-content',
        '.text-content',
    ],
    'article_title': [
        'h1',
        '.article-title',
        '.story-title',
        '.post-title',
        '.entry-title',
        '[data-testid="article-title"]',
        '.headline',
        '.title',
        'title',
    ],
    'publish_date': [
        'time::attr(datetime)',
        '.publish-date::text',
        '.article-date::text',
        '.story-date::text',
        '.post-date::text',
        '[data-testid="publish-date"]::text',
        'meta[property="article:published_time"]::attr(content)',
        'meta[name="publish_date"]::attr(content)',
        '.date::text',
        '.timestamp::text',
    ]
}

# Site-Specific Configurations
SITE_CONFIGS = {
    'marketwatch.com': {
        'article_selectors': ['a[href*="/story/"]'],
        'content_selectors': ['.article__content', '.story__content'],
        'title_selectors': ['.article__headline', '.story__headline'],
        'date_selectors': ['.timestamp__date'],
        'max_articles': 25,
    },
    'finance.yahoo.com': {
        'article_selectors': ['a[href*="/news/"]', 'a[href*="/article/"]'],
        'content_selectors': ['.caas-content', '.article-content'],
        'title_selectors': ['.caas-title', '.article-title'],
        'date_selectors': ['.caas-attr-time-style'],
        'max_articles': 20,
    },
    'cnbc.com': {
        'article_selectors': ['a[href*="/2024/"]', 'a[href*="/2025/"]'],
        'content_selectors': ['.ArticleBody-articleBody', '.content'],
        'title_selectors': ['.ArticleHeader-headline', '.title'],
        'date_selectors': ['.ArticleHeader-timestamp'],
        'max_articles': 30,
    },
    'reuters.com': {
        'article_selectors': ['a[href*="/article/"]', 'a[href*="/business/"]'],
        'content_selectors': ['.article-body__content', '.content'],
        'title_selectors': ['.article-header__title', '.title'],
        'date_selectors': ['.article-header__timestamp'],
        'max_articles': 25,
    },
    'bloomberg.com': {
        'article_selectors': ['a[href*="/news/"]', 'a[href*="/politics/"]'],
        'content_selectors': ['.body-copy', '.content'],
        'title_selectors': ['.headline__text', '.title'],
        'date_selectors': ['.timestamp', '.date'],
        'max_articles': 20,
    }
}

# Content Filtering
CONTENT_FILTERS = {
    'spam_patterns': [
        r'\b(sponsored|advertisement|advertorial|promoted)\b',
        r'\b(click here|read more|subscribe now|sign up)\b',
        r'\b(free trial|limited time|act now|don\'t miss)\b',
        r'\b(earn money|make money|work from home|get rich)\b',
        r'\b(weight loss|diet pills|miracle cure|secret formula)\b',
        r'\b(buy now|order now|call now|visit our website)\b',
    ],
    'generic_titles': [
        'latest updates', 'breaking news', 'top stories', 'news roundup',
        'from our experts', 'politics explained', 'market update',
        'daily briefing', 'morning report', 'evening update',
        'weekly roundup', 'monthly summary', 'quarterly report',
    ],
    'quality_indicators': [
        r'\b(analysis|report|study|research|survey)\b',
        r'\b(earnings|revenue|profit|loss|quarterly)\b',
        r'\b(policy|regulation|legislation|government)\b',
        r'\b(technology|innovation|development|launch)\b',
        r'\b(market|trading|investment|portfolio)\b',
        r'\b(economy|economic|gdp|inflation|unemployment)\b',
        r'\b(company|corporation|business|enterprise)\b',
        r'\b(industry|sector|market|field)\b',
    ]
}

# Proxy Configuration (if needed)
PROXY_CONFIG = {
    'enabled': False,
    'proxies': [
        # Add your proxy list here
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ],
    'rotation_interval': 10,  # requests per proxy
    'test_url': 'https://httpbin.org/ip',
}

# Rate Limiting
RATE_LIMITING = {
    'enabled': True,
    'requests_per_minute': 60,
    'requests_per_hour': 1000,
    'delay_between_requests': 1.0,
    'random_delay_range': (0.5, 2.0),
}

# Output Configuration
OUTPUT_CONFIG = {
    'include_metadata': True,
    'include_keywords': True,
    'include_category': True,
    'include_quality_score': True,
    'include_word_count': True,
    'include_processing_time': True,
    'format': 'json',  # 'json' or 'csv'
    'encoding': 'utf-8',
    'pretty_print': True,
} 