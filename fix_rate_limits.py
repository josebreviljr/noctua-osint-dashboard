#!/usr/bin/env python3
"""
Fix Rate Limits - Helper script for managing Google Gemini API quotas
"""

import time
import json
from datetime import datetime

def create_rate_limited_collector():
    """Create a rate-limited version of the collector"""
    
    print("🦉 Noctua Rate Limit Manager")
    print("=" * 40)
    print("This script helps you collect data while respecting API limits.")
    print()
    
    # Get user preferences
    try:
        max_articles = int(input("How many articles per feed? (1-5 recommended): ") or "3")
        delay_between_batches = int(input("Delay between batches in seconds? (60+ recommended): ") or "60")
        max_batches = int(input("How many batches to collect? (1-3 recommended): ") or "1")
    except ValueError:
        print("Using default values: 3 articles, 60s delay, 1 batch")
        max_articles = 3
        delay_between_batches = 60
        max_batches = 1
    
    print(f"\n📊 Collection Plan:")
    print(f"   • {max_articles} articles per feed")
    print(f"   • {delay_between_batches}s delay between batches")
    print(f"   • {max_batches} batch(es) total")
    print(f"   • Estimated time: {max_batches * delay_between_batches}s")
    print()
    
    # Import modules
    from collector import RSSCollector
    from processor import OSINTProcessor
    from storage import DataStorage
    
    collector = RSSCollector()
    processor = OSINTProcessor()
    storage = DataStorage()
    
    feeds = collector.load_feeds()
    print(f"📡 Found {len(feeds)} RSS feeds")
    
    total_processed = 0
    
    for batch in range(max_batches):
        print(f"\n🔄 Batch {batch + 1}/{max_batches}")
        print("-" * 30)
        
        # Collect articles
        print("📥 Collecting articles...")
        articles = collector.collect_all_feeds(feeds, max_articles)
        
        if not articles:
            print("❌ No articles collected")
            continue
        
        print(f"✅ Collected {len(articles)} articles")
        
        # Process articles
        print("🧠 Processing with Gemini...")
        processed_articles = processor.process_articles(articles)
        
        if processed_articles:
            # Generate summary
            analysis_summary = processor.get_analysis_summary(processed_articles)
            
            # Save results
            storage.save_reports(processed_articles, analysis_summary)
            
            total_processed += len(processed_articles)
            print(f"✅ Processed {len(processed_articles)} articles")
            print(f"📊 High urgency: {analysis_summary['urgency_distribution']['high']}")
            print(f"🌍 Top topic: {list(analysis_summary['top_topics'].keys())[0] if analysis_summary['top_topics'] else 'None'}")
        else:
            print("❌ No articles processed successfully")
        
        # Wait before next batch
        if batch < max_batches - 1:
            print(f"⏳ Waiting {delay_between_batches} seconds before next batch...")
            time.sleep(delay_between_batches)
    
    print(f"\n🎯 Collection Complete!")
    print(f"📈 Total articles processed: {total_processed}")
    print(f"📊 Dashboard available at: http://localhost:8080")

def check_api_status():
    """Check Google Gemini API status and quotas"""
    
    print("🔍 Checking Google Gemini API Status")
    print("=" * 40)
    
    try:
        from config import Config
        import google.generativeai as genai
        
        config = Config()
        genai.configure(api_key=config.google_api_key)
        
        # Test API with a simple request
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        test_prompt = "Respond with 'API working' if you can see this message."
        response = model.generate_content(test_prompt)
        
        if "API working" in response.text:
            print("✅ Google Gemini API is working")
            print("✅ API key is valid")
            print("✅ Model is accessible")
        else:
            print("⚠️  API responded but not as expected")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has GOOGLE_API_KEY set")
        print("2. Verify your API key is valid")
        print("3. Check your Google Cloud billing/quota")
        print("4. Try again in a few minutes")

def main():
    """Main function"""
    print("🦉 Noctua Rate Limit Manager")
    print("=" * 40)
    print("1. Check API Status")
    print("2. Collect Data (Rate Limited)")
    print("3. Exit")
    print()
    
    try:
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            check_api_status()
        elif choice == "2":
            create_rate_limited_collector()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 