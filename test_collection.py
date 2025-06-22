#!/usr/bin/env python3
"""
Test script to verify Noctua collection functionality
"""

import os
import sys
from config import Config
from collector import RSSCollector
from processor import OSINTProcessor
from storage import DataStorage

def test_collection():
    """Test the collection pipeline"""
    print("🧪 Testing Noctua Collection Pipeline")
    print("=" * 40)
    
    # Test 1: Check configuration
    print("1. Testing configuration...")
    try:
        Config.validate(require_api_key=False)
        print("   ✅ Configuration loaded successfully")
        
        if Config.GOOGLE_API_KEY:
            print("   ✅ Google API key found")
        else:
            print("   ⚠️  Google API key not found (collection will fail)")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Test RSS collection
    print("\n2. Testing RSS collection...")
    try:
        collector = RSSCollector()
        feeds = collector.load_feeds()
        print(f"   ✅ Loaded {len(feeds)} feeds")
        
        # Test with just 1 article per feed
        articles = collector.collect_all_feeds(feeds, max_articles=1)
        print(f"   ✅ Collected {len(articles)} articles (expected: {len(feeds)})")
        
        if articles:
            print(f"   📰 Sample article: {articles[0]['title'][:50]}...")
        else:
            print("   ⚠️  No articles collected")
            
        # Test with 2 articles per feed
        articles2 = collector.collect_all_feeds(feeds, max_articles=2)
        print(f"   ✅ Collected {len(articles2)} articles with max_articles=2 (expected: {len(feeds) * 2})")
            
    except Exception as e:
        print(f"   ❌ Collection error: {e}")
        return False
    
    # Test 3: Test processing (if API key available)
    if Config.GOOGLE_API_KEY:
        print("\n3. Testing AI processing...")
        try:
            processor = OSINTProcessor()
            
            # Test with just 1 article
            if articles:
                test_article = articles[0]
                processed = processor.process_articles([test_article])
                print(f"   ✅ Processed {len(processed)} articles")
                
                if processed:
                    report = processed[0]
                    print(f"   📊 Sample analysis: {report['topic']} - {report['urgency']} urgency")
            else:
                print("   ⚠️  No articles to process")
                
        except Exception as e:
            print(f"   ❌ Processing error: {e}")
            return False
    else:
        print("\n3. Skipping AI processing (no API key)")
    
    # Test 4: Test storage
    print("\n4. Testing storage...")
    try:
        storage = DataStorage()
        data = storage.load_existing_data()
        print(f"   ✅ Storage loaded successfully")
        print(f"   📁 Current reports: {len(data.get('reports', []))}")
        
    except Exception as e:
        print(f"   ❌ Storage error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ All tests completed successfully!")
    print("\nTo use the full pipeline:")
    print("1. Add your Google API key to .env file")
    print("2. Run: python main.py")
    print("3. Or use the dashboard: python start_dashboard.py")
    
    return True

if __name__ == "__main__":
    test_collection() 