#!/usr/bin/env python3
"""
Noctua OSINT Collector & Classifier
A command-line tool for collecting and analyzing open source intelligence from RSS feeds.
"""

import argparse
import sys
import logging
from typing import Optional

from config import Config
from utils import setup_logging
from collector import RSSCollector
from processor import OSINTProcessor
from storage import DataStorage

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Noctua OSINT Collector & Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --max-articles 10  # Collect 10 articles per feed
  python main.py --feeds custom_feeds.txt  # Use custom feeds file
  python main.py --output custom_data.json  # Custom output file
  python main.py --verbose          # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=Config.MAX_ARTICLES_PER_FEED,
        help=f'Maximum articles to collect per feed (default: {Config.MAX_ARTICLES_PER_FEED})'
    )
    
    parser.add_argument(
        '--feeds',
        type=str,
        default=Config.FEEDS_FILE,
        help=f'Path to feeds file (default: {Config.FEEDS_FILE})'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=Config.OUTPUT_FILE,
        help=f'Output file path (default: {Config.OUTPUT_FILE})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Collect articles without processing with Gemini'
    )
    
    parser.add_argument(
        '--export-csv',
        action='store_true',
        help='Export results to CSV after processing'
    )
    
    return parser.parse_args()

def validate_configuration():
    """Validate that all required configuration is present"""
    try:
        Config.validate()
        return True
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with your Google API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False

def run_pipeline(args):
    """Run the complete OSINT pipeline"""
    logger = logging.getLogger(__name__)
    
    print("🦉 Noctua OSINT Collector & Classifier")
    print("=" * 50)
    
    # Step 1: Collect articles from RSS feeds
    logger.info("Starting RSS feed collection...")
    collector = RSSCollector()
    
    try:
        feeds = collector.load_feeds(args.feeds)
        if not feeds:
            logger.error("No feeds loaded. Please check your feeds file.")
            return False
        
        articles = collector.collect_all_feeds(feeds, args.max_articles)
        if not articles:
            logger.warning("No articles collected from feeds.")
            return False
        
        print(f"✅ Collected {len(articles)} articles from {len(feeds)} feeds")
        
    except Exception as e:
        logger.error(f"Error during collection: {e}")
        return False
    
    # Step 2: Process articles with Gemini (unless dry-run)
    if args.dry_run:
        print("🔍 Dry run mode - skipping Gemini processing")
        processed_articles = []
        analysis_summary = {}
    else:
        logger.info("Starting Gemini analysis...")
        processor = OSINTProcessor()
        
        try:
            processed_articles = processor.process_articles(articles)
            analysis_summary = processor.get_analysis_summary(processed_articles)
            
            if processed_articles:
                print(f"✅ Processed {len(processed_articles)} articles with Gemini")
                print(f"📊 Urgency distribution: {analysis_summary.get('urgency_distribution', {})}")
            else:
                logger.warning("No articles were successfully processed.")
                return False
                
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            return False
    
    # Step 3: Save results
    logger.info("Saving results...")
    storage = DataStorage(args.output)
    
    try:
        storage.save_reports(processed_articles, analysis_summary)
        print(f"✅ Saved results to {args.output}")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return False
    
    # Step 4: Export to CSV if requested
    if args.export_csv and processed_articles:
        try:
            storage.export_to_csv()
            print("✅ Exported results to CSV")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    # Step 5: Display summary
    if processed_articles:
        print("\n📈 Analysis Summary:")
        print(f"   Total articles: {len(processed_articles)}")
        
        if analysis_summary:
            urgency_dist = analysis_summary.get('urgency_distribution', {})
            print(f"   High urgency: {urgency_dist.get('high', 0)}")
            print(f"   Medium urgency: {urgency_dist.get('medium', 0)}")
            print(f"   Low urgency: {urgency_dist.get('low', 0)}")
            
            top_topics = analysis_summary.get('top_topics', {})
            if top_topics:
                print(f"   Top topic: {list(top_topics.keys())[0]} ({list(top_topics.values())[0]} articles)")
    
    print("\n🎉 Pipeline completed successfully!")
    return True

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Run the pipeline
    success = run_pipeline(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 