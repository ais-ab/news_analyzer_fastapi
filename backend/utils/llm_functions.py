import os
import asyncio
import aiohttp
from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from typing import TypedDict, List, Dict
import traceback
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import lru_cache

# Load .env
load_dotenv()
openai_key = os.getenv("OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = openai_key

# Define State
class MyState(TypedDict):
    business_interest: str
    sources: list
    articles: list
    relevant_articles: list
    summary: str

# Performance configuration
MAX_CONCURRENT_REQUESTS = 10
BATCH_SIZE = 5  # Process articles in batches for LLM calls
CACHE_TTL = 3600  # 1 hour cache

# Cache for LLM responses
@lru_cache(maxsize=1000)
def cached_llm_response(business_interest: str, content_hash: str) -> str:
    """Cache LLM responses to avoid duplicate API calls"""
    return content_hash  # Placeholder - will be replaced with actual LLM call

# Define format_output tool
@tool
def format_output(formatted_text: str) -> str:
    """
    Fetch news articles from a given source and date.
    """
    return formatted_text

def clear_scraper_cache():
    """Clear the scraper cache to force fresh scraping"""
    if hasattr(run_scraper, '_cache'):
        run_scraper._cache.clear()
        print("[DEBUG] Scraper cache cleared")

# Run Scraper - Keep synchronous for now to ensure it works
def run_scraper(sources, force_fresh=False):
    # Simple cache to prevent duplicate scraping
    if force_fresh:
        clear_scraper_cache()
    
    cache_key = tuple(sorted(sources))
    if hasattr(run_scraper, '_cache') and cache_key in run_scraper._cache:
        print(f"[DEBUG] Using cached results for {len(sources)} sources")
        return run_scraper._cache[cache_key]
    
    print(f"[DEBUG] run_scraper called with sources: {sources}")
    print(f"[DEBUG] Number of sources: {len(sources)}")
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "output.json")

    spider_path = os.path.join(os.path.dirname(__file__), "trafilatura_spider.py")

    # Pass sources directly as JSON string to the spider
    sources_json = json.dumps(sources)
    print(f"[DEBUG] Sources JSON: {sources_json}")

    # Run spider with sources as command line argument
    result = subprocess.run([
        "scrapy", "runspider", spider_path, "-a", f"sources={sources_json}"
    ], capture_output=True, text=True)

    print("SCRAPY STDOUT:")
    print(result.stdout)
    print("SCRAPY STDERR:")
    print(result.stderr)

    # Load articles
    try:
        with open(output_path, "r") as f:
            articles = json.load(f)
        print(f"[DEBUG] Loaded {len(articles)} articles from output file")
    except FileNotFoundError:
        print("No output file found - spider may have failed")
        articles = []
    except json.JSONDecodeError:
        print("Invalid JSON in output file")
        articles = []

    # Cache the results
    if not hasattr(run_scraper, '_cache'):
        run_scraper._cache = {}
    run_scraper._cache[cache_key] = articles

    return articles

# Pre-filter articles to remove obviously irrelevant content before LLM processing
def pre_filter_articles(articles: List[Dict], business_interest: str) -> List[Dict]:
    """Pre-filter articles to remove obviously irrelevant content before LLM processing"""
    if not articles:
        return []
    
    business_interest_lower = business_interest.lower()
    filtered_articles = []
    
    # Extract geographic keywords from business interest
    geographic_keywords = []
    if 'qatar' in business_interest_lower:
        geographic_keywords.extend(['qatar', 'doha', 'gulf', 'middle east'])
    if 'usa' in business_interest_lower or 'united states' in business_interest_lower:
        geographic_keywords.extend(['usa', 'united states', 'america', 'american'])
    if 'uk' in business_interest_lower or 'britain' in business_interest_lower:
        geographic_keywords.extend(['uk', 'britain', 'england', 'london'])
    if 'china' in business_interest_lower:
        geographic_keywords.extend(['china', 'chinese', 'beijing', 'shanghai'])
    
    # Extract topic keywords
    topic_keywords = []
    if 'economy' in business_interest_lower or 'economic' in business_interest_lower:
        topic_keywords.extend(['economy', 'economic', 'finance', 'financial', 'business', 'market'])
    if 'politics' in business_interest_lower or 'political' in business_interest_lower:
        topic_keywords.extend(['politics', 'political', 'government', 'policy'])
    if 'technology' in business_interest_lower or 'tech' in business_interest_lower:
        topic_keywords.extend(['technology', 'tech', 'digital', 'innovation'])
    
    for article in articles:
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        # Skip obvious sports/entertainment content unless specifically requested
        sports_keywords = ['football', 'soccer', 'basketball', 'tennis', 'golf', 'sport', 'match', 'game', 'player', 'team']
        entertainment_keywords = ['movie', 'film', 'celebrity', 'actor', 'actress', 'music', 'concert', 'show']
        
        # Check if article is sports/entertainment focused
        is_sports = any(keyword in title or keyword in content[:200] for keyword in sports_keywords)
        is_entertainment = any(keyword in title or keyword in content[:200] for keyword in entertainment_keywords)
        
        # If business interest doesn't mention sports/entertainment, skip these articles
        if (is_sports or is_entertainment) and not any(keyword in business_interest_lower for keyword in ['sport', 'entertainment', 'football', 'movie', 'music']):
            continue
        
        # If geographic keywords are specified, article must mention them
        if geographic_keywords:
            has_geographic_match = any(keyword in title or keyword in content[:500] for keyword in geographic_keywords)
            if not has_geographic_match:
                continue
        
        # If topic keywords are specified, article should mention them (but be less strict)
        if topic_keywords:
            has_topic_match = any(keyword in title or keyword in content[:500] for keyword in topic_keywords)
            # Only require topic match if business interest is very specific
            if len(topic_keywords) > 2 and not has_topic_match:
                continue
        
        filtered_articles.append(article)
    
    print(f"[PreFilter] Filtered {len(articles)} articles down to {len(filtered_articles)} based on geographic/topic matching")
    return filtered_articles

# Batch LLM processing for filtering
async def batch_filter_articles(articles: List[Dict], business_interest: str, llm: ChatOpenAI) -> List[Dict]:
    """Process articles in batches for better performance with improved filtering"""
    if not articles:
        return []
    
    # Enhanced filtering prompt with strict criteria
    filter_prompt = """
    You are an expert news filtering agent. Your job is to identify articles that are DIRECTLY and SPECIFICALLY relevant to the user's business interest.
    
    FILTERING CRITERIA:
    1. **Direct Relevance**: The article must directly address the specific topic, location, or subject mentioned in the business interest
    2. **Geographic Specificity**: If the business interest mentions a specific country, region, or city, the article MUST mention that location
    3. **Context Match**: The article's main focus should align with the business interest's intent
    4. **Exclude**: Sports, entertainment, lifestyle, and unrelated topics unless specifically requested
    
    Business Interest: "{business_interest}"
    
    For each article below, analyze the title and content. Respond with ONLY "Yes" or "No" on a new line.
    - "Yes" = Article is DIRECTLY relevant to the business interest
    - "No" = Article is NOT relevant or only tangentially related
    
    Articles:
    {articles_text}
    
    Respond with one Yes/No per article, each on a new line.
    """
    
    relevant_articles = []
    
    # Process articles in batches
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        
        # Create batch text with both title and content for better analysis
        articles_text = ""
        for j, article in enumerate(batch):
            title = article.get('title', 'No title')
            content = article.get('content', '')[:800] if article.get('content') else ''
            articles_text += f"Article {j+1}:\nTitle: {title}\nContent: {content}...\n\n"
        
        # Single LLM call for the batch
        messages = [
            SystemMessage(content=filter_prompt.format(
                business_interest=business_interest, articles_text=articles_text
            ))
        ]
        try:
            response = llm.invoke(messages)
            if isinstance(response, AIMessage):
                # Parse batch response
                lines = response.content.strip().split('\n')
                print(f"[Filter] LLM response: {response.content.strip()}")
                for j, line in enumerate(lines):
                    if j < len(batch) and "Yes" in line.strip():
                        relevant_articles.append(batch[j])
                        if len(relevant_articles) >= 5:  # Max relevant articles
                            return relevant_articles
        except Exception as e:
            print(f"Error in batch filtering: {e}")
    
    return relevant_articles

# Preprocess node - Keep synchronous for now
def preprocess(state):
    try:
        # Check if we need fresh data (you can add logic here to determine when to force fresh)
        force_fresh = state.get("force_fresh", False)
        articles = run_scraper(state["sources"], force_fresh=force_fresh)
        print(f"[Preprocess] Fetched {len(articles)} articles")
    except Exception as e:
        print(f"[Preprocess] Error during scraping: {e}")
        print(traceback.print_exc())
        articles = []
    state["articles"] = articles
    return state

# FilterArticles node - Use async batch processing
async def filter_articles_async(state):
    if not state["articles"]:
        print("[Filter] No articles to filter")
        state["relevant_articles"] = []
        return state
        
    print(f"[Filter] Business interest: '{state['business_interest']}'")
    print(f"[Filter] Processing {len(state['articles'])} articles")
    
    # Print first few article titles for debugging
    for i, article in enumerate(state["articles"][:3]):
        title = article.get('title', 'No title')
        print(f"[Filter] Article {i+1}: {title}")
    
    # Step 1: Pre-filter articles based on geographic and topic matching
    pre_filtered_articles = pre_filter_articles(state["articles"], state["business_interest"])
    
    if not pre_filtered_articles:
        print("[Filter] No articles passed pre-filtering")
        state["relevant_articles"] = []
        return state
    
    print(f"[Filter] {len(pre_filtered_articles)} articles passed pre-filtering, sending to LLM")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Step 2: Use LLM for final filtering
    relevant_articles = await batch_filter_articles(
        pre_filtered_articles, 
        state["business_interest"], 
        llm
    )
    
    print(f"[Filter] Selected {len(relevant_articles)} relevant articles")
    
    # Print the titles of selected articles
    for i, article in enumerate(relevant_articles):
        title = article.get('title', 'No title')
        print(f"[Filter] Selected article {i+1}: {title}")
    
    state["relevant_articles"] = relevant_articles
    return state

# SummarizeArticles node
async def summarize_articles_async(state):
    if not state["relevant_articles"]:
        state["summary"] = "No relevant information found for this topic."
        return state

    # Filter articles to exclude unwanted content
    filtered_articles = []
    print(f"[Summarize] Processing {len(state['relevant_articles'])} articles from filter step")
    
    for i, article in enumerate(state["relevant_articles"]):
        print(f"[Summarize] Article {i+1}: {article.get('title', 'No title')}")
        
        # Skip very short content (likely not real articles)
        if len(article.get('content', '')) < 100:
            print(f"[Summarize] Filtered out article {i+1} due to short content ({len(article.get('content', ''))} chars)")
            continue
            
        print(f"[Summarize] Keeping article {i+1}")
        filtered_articles.append(article)
    
    print(f"[Summarize] Final filtered articles: {len(filtered_articles)}")
    
    if not filtered_articles:
        state["summary"] = "No relevant articles found after filtering out generic content."
        return state

    # Initialize LLM for summarization
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Create a well-formatted summary with proper sections and metadata
    summary_lines = []
    
    # Header
    summary_lines.append("# 📰 Latest News Summary")
    summary_lines.append("")
    summary_lines.append(f"**Topic:** {state['business_interest']}")
    summary_lines.append(f"**Articles Found:** {len(filtered_articles)}")
    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")
    
    # Process each article with summarization
    for i, article in enumerate(filtered_articles, 1):
        # Article header
        summary_lines.append(f"## 📄 Article {i}")
        summary_lines.append("")
        
        # Title
        title = article.get('title', 'No title available')
        if title:
            summary_lines.append(f"**Title:** {title}")
            summary_lines.append("")
        
        # Source and publish date
        url = article.get('url', 'N/A')
        publish_date = article.get('publish_date')
        
        summary_lines.append("**Source:** " + url)
        if publish_date:
            summary_lines.append(f"**Published:** {publish_date}")
        summary_lines.append("")
        
        # Generate summary for the content
        content = article.get('content', '')
        if content:
            try:
                # Create summary prompt
                summary_prompt = f"""
                Create a concise, informative summary of this news article in 2-3 sentences.
                Focus on the key facts, main points, and any important implications.
                Write in a clear, professional tone suitable for a business news summary.
                
                Title: {title}
                Content: {content[:2000]}  # Limit content length for efficiency
                
                Summary:
                """
                
                messages = [
                    SystemMessage(content="You are a professional news summarizer. Create concise, accurate summaries."),
                    HumanMessage(content=summary_prompt)
                ]
                
                response = llm.invoke(messages)
                summary = response.content.strip()
                
                # Clean up the summary
                if summary.startswith("Summary:"):
                    summary = summary[8:].strip()
                
                summary_lines.append("**Summary:**")
                summary_lines.append("")
                summary_lines.append(summary)
                
            except Exception as e:
                print(f"Error generating summary for article {i}: {e}")
                # Fallback: use first few sentences
                sentences = content.split('.')[:3]
                fallback_summary = '. '.join(sentences) + '.' if sentences else content[:200] + "..."
                summary_lines.append("**Summary:**")
                summary_lines.append("")
                summary_lines.append(fallback_summary)
        
        # Separator between articles
        summary_lines.append("")
        summary_lines.append("---")
        summary_lines.append("")
    
    # Footer
    summary_lines.append("*Generated by News Analyzer*")
    
    state["summary"] = "\n".join(summary_lines)
    return state

# ShowSummary node
def show_summary(state):
    return state

# Main Workflow with async support
async def get_news_async(business_interest="", sources=[]):
    workflow = StateGraph(state_schema=MyState)

    workflow.add_node("Preprocess", preprocess)  # Keep synchronous
    workflow.add_node("FilterArticles", filter_articles_async)
    workflow.add_node("SummarizeArticles", summarize_articles_async)
    workflow.add_node("ShowSummary", show_summary)

    workflow.set_entry_point("Preprocess")
    workflow.add_edge("Preprocess", "FilterArticles")
    workflow.add_edge("FilterArticles", "SummarizeArticles")
    workflow.add_edge("SummarizeArticles", "ShowSummary")
    workflow.add_edge("ShowSummary", END)

    graph = workflow.compile()

    final_state = await graph.ainvoke({
        "business_interest": business_interest,
        "sources": sources,
        "articles": [],
        "relevant_articles": [],
        "summary": ""
    })

    return final_state["summary"]

# Synchronous wrapper for backward compatibility
def get_news(business_interest="", sources=[]):
    """Synchronous wrapper for the async get_news function"""
    return asyncio.run(get_news_async(business_interest, sources))

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.step_times = {}
    
    def start(self):
        self.start_time = time.time()
    
    def log_step(self, step_name: str):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.step_times[step_name] = elapsed
            print(f"[Performance] {step_name}: {elapsed:.2f}s")
    
    def get_summary(self):
        total_time = time.time() - self.start_time if self.start_time else 0
        return {
            "total_time": total_time,
            "step_times": self.step_times
        }

# Enhanced version with performance monitoring
async def get_news_with_monitoring(business_interest="", sources=[]):
    """Enhanced version with performance monitoring"""
    monitor = PerformanceMonitor()
    monitor.start()
    
    try:
        result = await get_news_async(business_interest, sources)
        monitor.log_step("Total Processing")
        print(f"[Performance] Summary: {monitor.get_summary()}")
        return result
    except Exception as e:
        print(f"Error in get_news: {e}")
        return f"Error: {str(e)}"
