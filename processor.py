#!/usr/bin/env python3
"""
OSINT Processor - Uses Google Gemini to analyze and classify articles
"""

import google.generativeai as genai
import json
import logging
import time
import random
from typing import List, Dict, Any
from config import Config
from google.api_core import exceptions as google_exceptions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSINTProcessor:
    def __init__(self):
        """Initialize the OSINT processor with Gemini configuration"""
        self.config = Config()
        genai.configure(api_key=self.config.google_api_key)
        self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
        
        # Rate limiting settings
        self.requests_per_minute = 15  # Free tier limit
        self.delay_between_requests = 60 / self.requests_per_minute  # 4 seconds
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to respect API quotas"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay_between_requests:
            sleep_time = self.delay_between_requests - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _analyze_article_with_retries(self, prompt: str, retries: int = 3, delay: int = 5) -> Dict[str, Any]:
        """Call the Gemini API with retries for rate limit errors"""
        for attempt in range(retries):
            try:
                self._rate_limit()
                response = self.model.generate_content(prompt)
                return response
            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                break
        raise Exception("Failed to get a response from the API after multiple retries.")

    def _analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single article using Gemini"""
        try:
            self._rate_limit()  # Apply rate limiting
            
            # Prepare the prompt
            prompt = f"""
            Analyze this news article for OSINT purposes and provide a structured analysis.
            
            Article Title: {article.get('title', 'N/A')}
            Article Description: {article.get('description', 'N/A')}
            Source: {article.get('source', 'N/A')}
            
            Please analyze this article and provide a JSON response with the following structure:
            {{
                "summary": "Brief 2-3 sentence summary of the key intelligence",
                "region": "Primary geographic region affected (Europe, North America, Asia-Pacific, Middle East, South America, Africa, Global)",
                "topic": "Primary topic category (Cybersecurity, Geopolitics, Technology, Military, Terrorism, Disasters, Economics, Health)",
                "urgency": "Urgency level (low, medium, high) based on potential impact",
                "confidence": "Confidence in analysis (low, medium, high)"
            }}
            
            Focus on:
            - Geographic scope and impact
            - Security or intelligence implications
            - Potential threats or opportunities
            - Reliability of the information
            
            Respond only with valid JSON, no additional text.
            """
            
            # Generate response with retries
            response = self._analyze_article_with_retries(prompt)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            
            # Find the JSON object within the response text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                try:
                    analysis = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ['summary', 'region', 'topic', 'urgency', 'confidence']
                    for field in required_fields:
                        if field not in analysis:
                            logger.warning(f"Missing field '{field}' in response, using default")
                            analysis[field] = 'Unknown' if field in ['region', 'topic'] else 'medium'
                    
                    return analysis
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse extracted JSON: {e}")
                    logger.error(f"Extracted string: {json_str}")
            
            logger.error("Could not find a valid JSON object in the response.")
            logger.error(f"Raw response: {response.text}")

        except Exception as e:
            logger.error(f"Error analyzing article: {e}")

        # Return default analysis on failure
        return {
            "summary": f"Analysis failed for: {article.get('title', 'Unknown article')}",
            "region": "Global",
            "topic": "Technology",
            "urgency": "medium",
            "confidence": "low"
        }
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of articles and return analyzed reports"""
        processed_articles = []
        
        logger.info(f"Processing {len(articles)} articles...")
        
        for i, article in enumerate(articles):
            try:
                logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")
                
                # Analyze the article
                analysis = self._analyze_article(article)
                
                # Create report
                report = {
                    "id": f"report_{i+1}_{int(time.time())}",
                    "summary": analysis["summary"],
                    "region": analysis["region"],
                    "topic": analysis["topic"],
                    "urgency": analysis["urgency"],
                    "confidence": analysis["confidence"],
                    "analyzed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "original_article": article
                }
                
                processed_articles.append(report)
                
                # Add small random delay to avoid rate limits
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.error(f"Error processing article {i+1}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_articles)} articles")
        return processed_articles
    
    def get_analysis_summary(self, processed_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the analysis results"""
        if not processed_articles:
            return {
                "total_articles": 0,
                "urgency_distribution": {"high": 0, "medium": 0, "low": 0},
                "top_topics": {},
                "top_regions": {}
            }
        
        # Calculate distributions
        urgency_distribution = {"high": 0, "medium": 0, "low": 0}
        topic_distribution = {}
        region_distribution = {}
        
        for article in processed_articles:
            urgency = article.get("urgency", "medium")
            urgency_distribution[urgency] = urgency_distribution.get(urgency, 0) + 1
            
            topic = article.get("topic", "Unknown")
            topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
            
            region = article.get("region", "Global")
            region_distribution[region] = region_distribution.get(region, 0) + 1
        
        # Get top topics and regions (limit to top 5)
        top_topics = dict(sorted(topic_distribution.items(), key=lambda x: x[1], reverse=True)[:5])
        top_regions = dict(sorted(region_distribution.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return {
            "total_articles": len(processed_articles),
            "urgency_distribution": urgency_distribution,
            "top_topics": top_topics,
            "top_regions": top_regions
        } 