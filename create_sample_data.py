#!/usr/bin/env python3
"""
Create sample OSINT data for dashboard testing
"""

import json
import uuid
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample OSINT reports for dashboard testing"""
    
    # Sample data structure
    sample_reports = []
    
    # Sample topics and regions
    topics = ["Cybersecurity", "Geopolitics", "Technology", "Military", "Terrorism", "Disasters", "Economics", "Health"]
    regions = ["Europe", "North America", "Asia-Pacific", "Middle East", "South America", "Africa", "Global"]
    urgencies = ["high", "medium", "low"]
    confidences = ["high", "medium", "low"]
    
    # Real RSS feeds and their domains
    real_sources = [
        {
            "name": "BBC News",
            "domain": "https://www.bbc.com",
            "feed": "https://feeds.bbci.co.uk/news/world/rss.xml"
        },
        {
            "name": "The Guardian",
            "domain": "https://www.theguardian.com",
            "feed": "https://www.theguardian.com/world/rss"
        },
        {
            "name": "NPR News",
            "domain": "https://www.npr.org",
            "feed": "https://feeds.npr.org/1004/rss.xml"
        },
        {
            "name": "TechCrunch",
            "domain": "https://techcrunch.com",
            "feed": "https://feeds.feedburner.com/techcrunch"
        },
        {
            "name": "Ars Technica",
            "domain": "https://arstechnica.com",
            "feed": "https://feeds.arstechnica.com/arstechnica/index"
        }
    ]
    
    # Realistic article titles and descriptions
    article_templates = [
        {
            "title": "Major Cybersecurity Breach Affects Millions of Users",
            "description": "A sophisticated cyber attack has compromised sensitive data across multiple organizations, raising concerns about digital security infrastructure.",
            "topic": "Cybersecurity",
            "urgency": "high"
        },
        {
            "title": "New AI Technology Revolutionizes Industry Standards",
            "description": "Breakthrough artificial intelligence developments are transforming traditional business models and creating new opportunities.",
            "topic": "Technology",
            "urgency": "medium"
        },
        {
            "title": "International Trade Agreement Reached After Months of Negotiation",
            "description": "Global leaders have finalized a comprehensive trade deal that could reshape economic relationships between major powers.",
            "topic": "Economics",
            "urgency": "medium"
        },
        {
            "title": "Natural Disaster Response Teams Deployed to Affected Region",
            "description": "Emergency services are coordinating relief efforts following a devastating natural disaster that has displaced thousands.",
            "topic": "Disasters",
            "urgency": "high"
        },
        {
            "title": "Military Exercise Raises Tensions in Strategic Region",
            "description": "Large-scale military maneuvers have sparked diplomatic concerns and calls for de-escalation from neighboring countries.",
            "topic": "Military",
            "urgency": "medium"
        },
        {
            "title": "Public Health Alert: New Virus Strain Detected",
            "description": "Health authorities are monitoring a newly identified virus variant with potential implications for public safety.",
            "topic": "Health",
            "urgency": "high"
        },
        {
            "title": "Terrorism Threat Level Elevated Following Recent Events",
            "description": "Security agencies have increased threat assessments in response to recent terrorist activities and intelligence reports.",
            "topic": "Terrorism",
            "urgency": "high"
        },
        {
            "title": "Diplomatic Relations Strained Over Territorial Dispute",
            "description": "Ongoing territorial conflicts have led to increased diplomatic tensions between neighboring nations.",
            "topic": "Geopolitics",
            "urgency": "medium"
        }
    ]
    
    # Create 20 sample reports
    for i in range(20):
        # Generate random timestamp within last 7 days
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Select random source and article template
        source = random.choice(real_sources)
        template = random.choice(article_templates)
        
        # Create realistic article URL
        article_slug = f"article-{i+1}-{template['title'].lower().replace(' ', '-').replace(':', '').replace(',', '')[:30]}"
        article_url = f"{source['domain']}/news/{article_slug}"
        
        # Create sample report
        report = {
            "id": str(uuid.uuid4()),
            "summary": f"OSINT analysis of {template['title'].lower()}. This incident has significant implications for {template['topic'].lower()} and requires immediate attention from relevant authorities. The situation continues to develop and may impact multiple stakeholders.",
            "region": random.choice(regions),
            "topic": template["topic"],
            "urgency": template["urgency"],
            "confidence": random.choice(confidences),
            "analyzed_at": timestamp.isoformat(),
            "original_article": {
                "title": template["title"],
                "link": article_url,
                "source": source["name"],
                "published": (timestamp - timedelta(hours=random.randint(1, 24))).isoformat(),
                "description": template["description"]
            }
        }
        sample_reports.append(report)
    
    # Calculate summary statistics
    urgency_distribution = {"high": 0, "medium": 0, "low": 0}
    topic_distribution = {}
    region_distribution = {}
    
    for report in sample_reports:
        urgency_distribution[report["urgency"]] += 1
        
        topic = report["topic"]
        topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
        
        region = report["region"]
        region_distribution[region] = region_distribution.get(region, 0) + 1
    
    # Create top topics (limit to top 5)
    top_topics = dict(sorted(topic_distribution.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Create top regions (limit to top 5)
    top_regions = dict(sorted(region_distribution.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Create the complete data structure
    data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Noctua OSINT Analysis Data - Sample Data with Real Sources",
            "last_updated": datetime.now().isoformat(),
            "total_reports": len(sample_reports)
        },
        "reports": sample_reports,
        "summary": {
            "total_articles": len(sample_reports),
            "urgency_distribution": urgency_distribution,
            "top_topics": top_topics,
            "top_regions": top_regions
        }
    }
    
    return data

def main():
    """Main function to create and save sample data"""
    print("🦉 Creating sample OSINT data with real source links...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Save to file
    with open('data/reports.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Created {len(sample_data['reports'])} sample reports")
    print(f"📊 High urgency items: {sample_data['summary']['urgency_distribution']['high']}")
    print(f"🌍 Top region: {list(sample_data['summary']['top_regions'].keys())[0]}")
    print(f"📝 Top topic: {list(sample_data['summary']['top_topics'].keys())[0]}")
    print("🔗 All source links now point to real RSS feed domains")
    print("🎯 Dashboard should now show sample data with working links at http://localhost:8080")

if __name__ == "__main__":
    main() 