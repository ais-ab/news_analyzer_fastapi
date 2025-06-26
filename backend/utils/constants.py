import os

# Database path - updated for new structure
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "analyzer.db")

# Performance Configuration
PERFORMANCE_CONFIG = {
    # LLM Settings
    'MAX_CONCURRENT_LLM_CALLS': 10,
    'BATCH_SIZE': 5,
    'LLM_TIMEOUT': 30,
    'CACHE_TTL': 3600,  # 1 hour
    
    # Scraping Settings
    'CONCURRENT_REQUESTS': 16,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'DOWNLOAD_DELAY': 0.05,
    'DOWNLOAD_TIMEOUT': 10,
    'RETRY_TIMES': 2,
    'MAX_ARTICLES_PER_SITE': 5,
    'MAX_RELEVANT_ARTICLES': 5,
    
    # Content Settings
    'MIN_CONTENT_LENGTH': 100,
    'MAX_DAYS_OLD': 2,
    
    # Caching
    'ENABLE_CACHING': True,
    'CACHE_SIZE': 1000,
    
    # Monitoring
    'ENABLE_PERFORMANCE_MONITORING': True,
    'LOG_PERFORMANCE': True,
}

# Model Configuration
MODEL_CONFIG = {
    'FILTER_MODEL': 'gpt-4o',
    'SUMMARIZE_MODEL': 'gpt-4o',
    'TEMPERATURE': 0,
    'MAX_TOKENS': 4000,
}

# File Paths - updated for new structure
PATHS = {
    'SOURCES_FILE': os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "sources.json"),
    'OUTPUT_FILE': os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "output.json"),
    'SPIDER_FILE': os.path.join(os.path.dirname(__file__), "trafilatura_spider.py"),
}
