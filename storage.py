import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

from config import Config
from utils import format_timestamp

logger = logging.getLogger(__name__)

class DataStorage:
    """Handles storage and retrieval of OSINT analysis data"""
    
    def __init__(self, output_file: str = None):
        self.output_file = output_file or Config.OUTPUT_FILE
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.output_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
    
    def load_existing_data(self) -> Dict[str, Any]:
        """Load existing data from the output file"""
        if not os.path.exists(self.output_file):
            logger.info(f"Output file does not exist, starting fresh: {self.output_file}")
            return {
                'metadata': {
                    'created_at': format_timestamp(),
                    'version': '1.0',
                    'description': 'Noctua OSINT Analysis Data'
                },
                'reports': [],
                'summary': {}
            }
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded existing data from {self.output_file}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing existing data file: {e}")
            return self._create_new_data_structure()
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            return self._create_new_data_structure()
    
    def _create_new_data_structure(self) -> Dict[str, Any]:
        """Create a new data structure"""
        return {
            'metadata': {
                'created_at': format_timestamp(),
                'version': '1.0',
                'description': 'Noctua OSINT Analysis Data'
            },
            'reports': [],
            'summary': {}
        }
    
    def save_reports(self, processed_articles: List[Dict[str, Any]], analysis_summary: Dict[str, Any] = None):
        """Save processed articles and summary to the output file"""
        try:
            from processor import OSINTProcessor
            # Load existing data
            data = self.load_existing_data()
            
            # Add new reports
            for article in processed_articles:
                article['id'] = self._generate_article_id(article)
                data['reports'].append(article)
            
            # Always recalculate summary using all reports
            processor = OSINTProcessor()
            data['summary'] = processor.get_analysis_summary(data['reports'])
            
            # Update metadata
            data['metadata']['last_updated'] = format_timestamp()
            data['metadata']['total_reports'] = len(data['reports'])
            
            # Save to file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(processed_articles)} reports to {self.output_file}")
            
        except Exception as e:
            logger.error(f"Error saving reports: {e}")
            raise
    
    def _generate_article_id(self, article: Dict[str, Any]) -> str:
        """Generate a unique ID for an article"""
        title = article.get('original_article', {}).get('title', '')
        timestamp = article.get('analyzed_at', '')
        
        # Create a simple hash-based ID
        import hashlib
        content = f"{title}{timestamp}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:12]
    
    def get_reports_by_urgency(self, urgency: str) -> List[Dict[str, Any]]:
        """Get all reports with a specific urgency level"""
        data = self.load_existing_data()
        return [report for report in data['reports'] if report.get('urgency') == urgency]
    
    def get_reports_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all reports with a specific topic"""
        data = self.load_existing_data()
        return [report for report in data['reports'] if report.get('topic') == topic]
    
    def get_reports_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get all reports with a specific region"""
        data = self.load_existing_data()
        return [report for report in data['reports'] if report.get('region') == region]
    
    def get_latest_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent reports"""
        data = self.load_existing_data()
        sorted_reports = sorted(data['reports'], 
                              key=lambda x: x.get('analyzed_at', ''), 
                              reverse=True)
        return sorted_reports[:limit]
    
    def export_to_csv(self, output_file: str = None):
        """Export reports to CSV format"""
        import csv
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/noctua_export_{timestamp}.csv"
        
        data = self.load_existing_data()
        
        if not data['reports']:
            logger.warning("No reports to export")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'title', 'summary', 'region', 'topic', 'urgency', 
                    'confidence', 'link', 'source', 'published', 'analyzed_at'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for report in data['reports']:
                    row = {
                        'id': report.get('id', ''),
                        'title': report.get('original_article', {}).get('title', ''),
                        'summary': report.get('summary', ''),
                        'region': report.get('region', ''),
                        'topic': report.get('topic', ''),
                        'urgency': report.get('urgency', ''),
                        'confidence': report.get('confidence', ''),
                        'link': report.get('original_article', {}).get('link', ''),
                        'source': report.get('original_article', {}).get('source', ''),
                        'published': report.get('original_article', {}).get('published', ''),
                        'analyzed_at': report.get('analyzed_at', '')
                    }
                    writer.writerow(row)
            
            logger.info(f"Exported {len(data['reports'])} reports to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise 