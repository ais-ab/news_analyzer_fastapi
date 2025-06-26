import scrapy
import json
import os
import trafilatura
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = openai_key

class TrafilaturaSpider(scrapy.Spider):

    name = "trafilatura_spider"
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_TIMEOUT': 15,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
    }

    def __init__(self, sources=None, sources_path='tmp/sources.json', output_path='tmp/output.json', *args, **kwargs):
        super(TrafilaturaSpider, self).__init__(*args, **kwargs)
        self.sources_path = sources_path
        self.output_path = output_path
        self.articles = []
        self.max_articles_per_source = 50
        self.max_age_days = 7
        self.max_depth = 3
        self.max_pages_per_source = 10
        
        # Enhanced logging (using different name to avoid conflict)
        self.log_handler = logging.getLogger(self.name)
        self.log_handler.setLevel(logging.INFO)
        
        # Add custom headers for better compatibility
        self.custom_settings = {
            'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 0.5,
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'DOWNLOAD_TIMEOUT': 15,
            'RETRY_TIMES': 3,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429, 403],
            'COOKIES_ENABLED': True,
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
                'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            }
        }
        
        # Always parse self.sources as JSON if it exists and is a string
        if hasattr(self, 'sources') and self.sources:
            try:
                self.sources_to_scrape = json.loads(self.sources)
                self.debug_info(f"[DEBUG] Parsed sources from command line: {self.sources_to_scrape}")
                self.debug_info(f"[DEBUG] Type of sources_to_scrape: {type(self.sources_to_scrape)}")
            except Exception as e:
                self.debug_info(f"[DEBUG] Error parsing sources argument: {e}")
                self.sources_to_scrape = []
        elif sources is not None:
            self.sources_to_scrape = sources
            self.debug_info(f"[DEBUG] Sources from parameter: {self.sources_to_scrape}")
        else:
            self.sources_to_scrape = []
            self.debug_info("[DEBUG] No sources provided, will read from file")
        
        self.site_article_count = {}  # domain -> count
        self.site_page_count = {}  # domain -> page count
        self.processed_urls = set()  # Track processed URLs to avoid duplicates
        self.crawl_depth = {}  # Track crawl depth for each domain

    def get_domain(self, url):
        """Extract domain from URL"""
        return urlparse(url).netloc

    def debug_info(self, message):
        """Debug logging with reduced overhead"""
        print(f"[DEBUG] {message}")

    def start_requests(self):
        self.debug_info("Spider started: start_requests called")
        
        # Ensure self.sources_to_scrape is a list
        if isinstance(self.sources_to_scrape, str):
            try:
                urls = json.loads(self.sources_to_scrape)
                self.debug_info(f"[DEBUG] start_requests parsed sources_to_scrape: {urls}")
                self.debug_info(f"[DEBUG] Type of urls: {type(urls)}")
            except Exception as e:
                self.debug_info(f"[DEBUG] Error parsing sources_to_scrape in start_requests: {e}")
                urls = []
        else:
            urls = self.sources_to_scrape
            self.debug_info(f"[DEBUG] sources_to_scrape is already a list: {urls}")
        
        # If no provided sources, fallback to file
        if not urls:
            try:
                with open(self.sources_path, "r") as f:
                    urls = json.load(f)
                self.debug_info(f"Loaded {len(urls)} URLs from sources file")
                self.debug_info(f"Sources from file: {urls}")
            except Exception as e:
                self.log_handler.error(f"Error reading sources file: {e}")
                return

        self.debug_info(f"Final URLs to scrape: {urls}")
        for url in urls:
            # Ensure URL has a scheme and is properly formatted
            if not url.startswith(('http://', 'https://')):
                url = "https://" + url
            
            # Clean the URL to prevent parsing errors
            url = url.strip()
            if not url or len(url) < 10:
                self.debug_info(f"Skipping invalid URL: {url}")
                continue
                
            self.debug_info(f"Requesting URL: {url}")
            try:
                # Add to processed URLs to avoid duplicates
                self.processed_urls.add(url)
                
                yield scrapy.Request(
                    url=url, 
                    callback=self.parse,
                    meta={'dont_cache': False, 'dont_redirect': False, 'depth': 0},
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    },
                    errback=self.handle_error
                )
            except Exception as e:
                self.debug_info(f"Error creating request for {url}: {e}")

    def handle_error(self, failure):
        """Enhanced error handling"""
        self.debug_info(f"Request failed: {failure.value}")
        if hasattr(failure.value, 'response'):
            self.debug_info(f"Response status: {failure.value.response.status}")

    def parse(self, response):
        domain = self.get_domain(response.url)
        self.site_article_count.setdefault(domain, 0)
        self.site_page_count.setdefault(domain, 0)
        
        # Track crawl depth
        current_depth = response.meta.get('depth', 0)
        self.crawl_depth[domain] = current_depth
        
        self.debug_info(f"Parsing {response.url} for domain {domain} at depth {current_depth}")
        self.debug_info(f"Page count for {domain}: {self.site_page_count[domain]}")

        # Increment page count
        self.site_page_count[domain] += 1
        
        # Stop if we've reached max pages for this source
        if self.site_page_count[domain] > self.max_pages_per_source:
            self.debug_info(f"Reached max pages ({self.max_pages_per_source}) for {domain}, stopping")
            return

        links = self.extract_links(response, domain)
        self.debug_info(f"Found {len(links)} links on {response.url}")

        article_count = 0
        internal_links = []
        category_links = []
        pagination_links = []
        
        for link in links:
            if article_count >= self.max_articles_per_source:
                self.debug_info(f"Reached limit for {domain}, stopping")
                break
                
            if self.is_likely_article_url(link, domain):
                self.debug_info(f"Crawling article {article_count + 1} for {domain}: {link}")
                article_count += 1
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_article,
                    meta={'domain': domain, 'depth': current_depth},
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                )
            elif self.is_category_page(link, domain):
                category_links.append(link)
            elif self.is_pagination_link(link, domain):
                pagination_links.append(link)
            elif self.is_internal_link(link, domain):
                internal_links.append(link)
        
        # Follow category pages (priority 1)
        if category_links and current_depth < self.max_depth:
            for category_link in category_links[:3]:  # Limit to 3 category pages
                if category_link not in self.processed_urls:
                    self.processed_urls.add(category_link)
                    self.debug_info(f"Crawling category page at depth {current_depth + 1}: {category_link}")
                    yield scrapy.Request(
                        url=category_link,
                        callback=self.parse,
                        meta={'domain': domain, 'depth': current_depth + 1},
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
        
        # Follow pagination links (priority 2)
        if pagination_links and current_depth < self.max_depth:
            for pagination_link in pagination_links[:2]:  # Limit to 2 pagination pages
                if pagination_link not in self.processed_urls:
                    self.processed_urls.add(pagination_link)
                    self.debug_info(f"Crawling pagination page at depth {current_depth + 1}: {pagination_link}")
                    yield scrapy.Request(
                        url=pagination_link,
                        callback=self.parse,
                        meta={'domain': domain, 'depth': current_depth + 1},
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )
        
        # Follow internal links (priority 3)
        if internal_links and current_depth < self.max_depth:
            for internal_link in internal_links[:2]:  # Limit to 2 internal pages
                if internal_link not in self.processed_urls:
                    self.processed_urls.add(internal_link)
                    self.debug_info(f"Crawling internal page at depth {current_depth + 1}: {internal_link}")
                    yield scrapy.Request(
                        url=internal_link,
                        callback=self.parse,
                        meta={'domain': domain, 'depth': current_depth + 1},
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        }
                    )

    def extract_links(self, response, domain):
        """Enhanced link extraction with multiple methods"""
        links = set()
        
        # Method 1: Standard link extraction
        links.update(response.css('a::attr(href)').getall())
        
        # Method 2: Look for article-specific selectors
        article_selectors = [
            'a[href*="/article/"]',
            'a[href*="/story/"]',
            'a[href*="/news/"]',
            'a[href*="/business/"]',
            'a[href*="/finance/"]',
            'a[href*="/markets/"]',
            'a[href*="/economy/"]',
            'a[href*="/technology/"]',
            'a[href*="/earnings/"]',
            'a[href*="/analysis/"]',
            '.article-link a',
            '.story-link a',
            '.news-link a',
            '[data-testid*="article"] a',
            '[class*="article"] a',
            '[class*="story"] a',
            '[class*="news"] a'
        ]
        
        for selector in article_selectors:
            links.update(response.css(selector + '::attr(href)').getall())
        
        # Convert to absolute URLs and filter
        absolute_links = []
        for link in links:
            if link:
                absolute_link = urljoin(response.url, link)
                if self.is_valid_url(absolute_link, domain):
                    absolute_links.append(absolute_link)
        
        return list(set(absolute_links))  # Remove duplicates

    def is_valid_url(self, url, domain):
        """Enhanced URL validation"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == domain or 
                parsed.netloc.endswith('.' + domain) or
                domain.endswith('.' + parsed.netloc)
            )
        except:
            return False

    def is_category_page(self, url, domain):
        """Identify category pages that contain multiple articles"""
        category_patterns = [
            r'/business/', r'/finance/', r'/markets/', r'/economy/', r'/technology/',
            r'/news/', r'/world/', r'/politics/', r'/opinion/', r'/analysis/',
            r'/earnings/', r'/stocks/', r'/commodities/', r'/currencies/',
            r'/cryptocurrency/', r'/crypto/', r'/blockchain/', r'/ai/', r'/artificial-intelligence/',
            r'/startups/', r'/venture-capital/', r'/ipo/', r'/mergers/', r'/acquisitions/',
            r'/regulation/', r'/policy/', r'/trade/', r'/tariffs/', r'/inflation/',
            r'/interest-rates/', r'/federal-reserve/', r'/central-bank/', r'/monetary-policy/'
        ]
        
        for pattern in category_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False

    def is_likely_article_url(self, url, domain):
        """Enhanced article URL detection"""
        # Skip obvious non-article URLs
        skip_patterns = [
            r'/login', r'/signup', r'/subscribe', r'/advertise', r'/contact',
            r'/about', r'/privacy', r'/terms', r'/cookie', r'/sitemap',
            r'/search', r'/tag/', r'/category/', r'/author/', r'/user/',
            r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$', r'\.mp4$', r'\.mp3$',
            r'/video/', r'/gallery/', r'/slideshow/', r'/interactive/',
            r'/newsletter', r'/rss', r'/feed', r'/api/', r'/ajax/',
            r'#', r'\?utm_', r'\?fbclid', r'\?ref=', r'\?source='
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Look for article indicators
        article_patterns = [
            r'/article/', r'/story/', r'/news/', r'/business/', r'/finance/',
            r'/markets/', r'/economy/', r'/technology/', r'/earnings/',
            r'/analysis/', r'/commentary/', r'/opinion/', r'/report/',
            r'\d{4}/\d{2}/\d{2}', r'\d{4}-\d{2}-\d{2}',  # Date patterns
            r'[a-z-]+-\d+',  # Slug with ID
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check URL length (articles tend to be longer)
        return len(url) > 50

    def parse_article(self, response):
        """Enhanced article parsing with multiple extraction methods"""
        self.debug_info(f"Parsing article: {response.url}")
        
        # Method 1: Trafilatura (primary method)
        content = self.extract_with_trafilatura(response)
        
        # Method 2: Fallback to CSS selectors if trafilatura fails
        if not content or len(content.strip()) < 100:
            content = self.extract_with_css(response)
        
        # Method 3: Basic text extraction as last resort
        if not content or len(content.strip()) < 100:
            content = self.extract_basic_text(response)
        
        if content and len(content.strip()) > 100:
            # Extract metadata
            title = self.extract_title(response)
            publish_date = self.extract_publish_date(response)
            
            # Check if article is recent enough
            if self.is_recent_article(publish_date):
                # Convert publish_date to string format safely
                if publish_date:
                    if hasattr(publish_date, 'isoformat'):
                        # It's a datetime object
                        publish_date_str = publish_date.isoformat()
                    else:
                        # It's already a string or other type
                        publish_date_str = str(publish_date)
                else:
                    publish_date_str = None
                
                article_data = {
                    'url': response.url,
                    'title': title,
                    'content': content,
                    'publish_date': publish_date_str,
                    'domain': response.meta.get('domain', ''),
                    'extraction_method': 'trafilatura'
                }
                
                self.articles.append(article_data)
                self.debug_info(f"Added article: {response.url} (total: {len(self.articles)})")
                self.log_handler.info(f"Extracted content from {response.url}")
            else:
                self.debug_info(f"Skipping old article: {response.url} ({self.get_days_old(publish_date)} days old)")
        else:
            self.debug_info(f"No content extracted from: {response.url}")

    def extract_with_trafilatura(self, response):
        """Extract content using trafilatura with enhanced settings"""
        try:
            # Enhanced trafilatura settings
            extracted = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                output_format='text',
                with_metadata=True,
                date_extraction_params={
                    'extensive_search': True,
                    'original_date': True
                }
            )
            return extracted
        except Exception as e:
            self.debug_info(f"Trafilatura extraction failed: {e}")
            return None

    def extract_with_css(self, response):
        """Fallback CSS extraction for common article selectors"""
        selectors = [
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
            '.post__content'
        ]
        
        for selector in selectors:
            content = response.css(selector).get()
            if content and len(content.strip()) > 100:
                return content
        
        return None

    def extract_basic_text(self, response):
        """Basic text extraction as last resort"""
        # Remove script and style elements
        text = response.css('body').get()
        if text:
            # Basic cleaning
            text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text if len(text) > 100 else None
        return None

    def extract_title(self, response):
        """Enhanced title extraction"""
        # Try multiple title selectors
        title_selectors = [
            'h1',
            '.article-title',
            '.story-title',
            '.post-title',
            '.entry-title',
            '[data-testid="article-title"]',
            'title'
        ]
        
        for selector in title_selectors:
            title = response.css(selector + '::text').get()
            if title and len(title.strip()) > 5:
                return title.strip()
        
        return None

    def extract_publish_date(self, response):
        """Enhanced date extraction"""
        try:
            # Try trafilatura date extraction first
            metadata = trafilatura.extract_metadata(response.text)
            if metadata and metadata.date:
                # Handle case where trafilatura returns a string
                if isinstance(metadata.date, str):
                    try:
                        return datetime.fromisoformat(metadata.date.replace('Z', '+00:00'))
                    except:
                        pass
                elif hasattr(metadata.date, 'isoformat'):
                    # It's already a datetime object
                    return metadata.date
            
            # Fallback to CSS selectors
            date_selectors = [
                'time::attr(datetime)',
                '.publish-date::text',
                '.article-date::text',
                '.story-date::text',
                '.post-date::text',
                '[data-testid="publish-date"]::text',
                'meta[property="article:published_time"]::attr(content)',
                'meta[name="publish_date"]::attr(content)'
            ]
            
            for selector in date_selectors:
                date_str = response.css(selector).get()
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
            
            # Default to current date if no date found
            return datetime.now()
            
        except Exception as e:
            self.debug_info(f"Date extraction failed: {e}")
            return datetime.now()

    def is_recent_article(self, publish_date):
        """Check if article is within the age limit"""
        if not publish_date:
            return True  # If no date, assume recent
        
        days_old = self.get_days_old(publish_date)
        return days_old <= self.max_age_days

    def get_days_old(self, publish_date):
        """Calculate how many days old an article is"""
        if not publish_date:
            return 0
        
        if isinstance(publish_date, str):
            try:
                publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except:
                return 0
        
        return (datetime.now() - publish_date).days

    def is_pagination_link(self, url, domain):
        """Identify pagination links"""
        pagination_patterns = [
            r'/page/\d+', r'/p/\d+', r'/page\d+', r'/p\d+',
            r'\?page=\d+', r'\&page=\d+', r'\?p=\d+', r'\&p=\d+',
            r'/news/page/\d+', r'/business/page/\d+', r'/technology/page/\d+',
            r'/finance/page/\d+', r'/markets/page/\d+', r'/economy/page/\d+',
            r'page=\d+', r'p=\d+', r'offset=\d+', r'start=\d+'
        ]
        
        for pattern in pagination_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False

    def is_internal_link(self, url, domain):
        """Identify internal navigation links"""
        # Skip obvious non-internal links
        skip_patterns = [
            r'/login', r'/signup', r'/subscribe', r'/advertise', r'/contact',
            r'/about', r'/privacy', r'/terms', r'/cookie', r'/sitemap',
            r'/search', r'/tag/', r'/category/', r'/author/', r'/user/',
            r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$', r'\.mp4$', r'\.mp3$',
            r'/video/', r'/gallery/', r'/slideshow/', r'/interactive/',
            r'/newsletter', r'/rss', r'/feed', r'/api/', r'/ajax/',
            r'#', r'\?utm_', r'\?fbclid', r'\?ref=', r'\?source='
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Check if it's a valid internal link
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == domain or 
                parsed.netloc.endswith('.' + domain) or
                domain.endswith('.' + parsed.netloc)
            )
        except:
            return False

    def closed(self, reason):
        """Enhanced spider closing"""
        self.debug_info(f"Spider closing. Reason: {reason}")
        self.debug_info(f"Total articles collected: {len(self.articles)}")
        
        # Save results
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, indent=2, ensure_ascii=False, default=str)
            self.log_handler.info(f"Spider closed. Processed {len(self.articles)} articles. Saved to {self.output_path}")
        except Exception as e:
            self.log_handler.error(f"Error saving results: {e}")
