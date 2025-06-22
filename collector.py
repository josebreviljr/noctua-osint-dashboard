import feedparser
import requests
import logging
from typing import List, Dict, Any
from tqdm import tqdm
import time

from config import Config
from utils import clean_text, truncate_text

logger = logging.getLogger(__name__)

class RSSCollector:
    """Collects articles from RSS feeds"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Noctua OSINT Collector/1.0'
        })
    
    def load_feeds(self, feeds_file: str = None) -> List[str]:
        """Load RSS feed URLs from file"""
        feeds_file = feeds_file or Config.FEEDS_FILE
        
        try:
            with open(feeds_file, 'r') as f:
                feeds = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            logger.info(f"Loaded {len(feeds)} feeds from {feeds_file}")
            return feeds
        except FileNotFoundError:
            logger.error(f"Feeds file not found: {feeds_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading feeds: {e}")
            return []
    
    def fetch_feed(self, feed_url: str, max_articles: int = None) -> List[Dict[str, Any]]:
        """Fetch articles from a single RSS feed"""
        if max_articles is None:
            max_articles = Config.MAX_ARTICLES_PER_FEED
        articles = []
        
        try:
            logger.info(f"Fetching feed: {feed_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {feed_url}: {feed.bozo_exception}")
            
            # Extract articles
            for i, entry in enumerate(feed.entries[:max_articles]):
                article = {
                    'title': clean_text(entry.get('title', '')),
                    'description': clean_text(entry.get('summary', '')),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': feed_url,
                    'feed_title': feed.feed.get('title', 'Unknown'),
                    'collected_at': time.time()
                }
                
                # Combine title and description for analysis
                content = f"{article['title']}\n\n{article['description']}"
                article['content'] = truncate_text(content, 2000)
                
                articles.append(article)
                logger.debug(f"Collected article: {article['title'][:50]}...")
            
            logger.info(f"Collected {len(articles)} articles from {feed_url}")
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
        
        return articles
    
    def collect_all_feeds(self, feeds: List[str] = None, max_articles: int = None) -> List[Dict[str, Any]]:
        """Collect articles from all feeds"""
        if feeds is None:
            feeds = self.load_feeds()
        
        if not feeds:
            logger.error("No feeds to process")
            return []
        
        all_articles = []
        
        logger.info(f"Starting collection from {len(feeds)} feeds...")
        
        for feed_url in tqdm(feeds, desc="Collecting feeds"):
            articles = self.fetch_feed(feed_url, max_articles)
            all_articles.extend(articles)
            
            # Small delay to be respectful to servers
            time.sleep(1)
        
        logger.info(f"Total articles collected: {len(all_articles)}")
        return all_articles
    
    def get_article_content(self, article: Dict[str, Any]) -> str:
        """Get the full content for analysis"""
        content_parts = []
        
        if article.get('title'):
            content_parts.append(article['title'])
        
        if article.get('description'):
            content_parts.append(article['description'])
        
        return "\n\n".join(content_parts) 