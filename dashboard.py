#!/usr/bin/env python3
"""
Noctua Dashboard - Web interface for OSINT analysis results
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from config import Config
from storage import DataStorage
from collector import RSSCollector
from processor import OSINTProcessor

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'noctua-dashboard-secret-key'

def get_dashboard_data() -> Dict[str, Any]:
    """Get data for the dashboard"""
    storage = DataStorage()
    data = storage.load_existing_data()
    
    # Calculate some additional stats
    total_reports = len(data.get('reports', []))
    
    # Get recent reports (last 24 hours)
    recent_reports = []
    if total_reports > 0:
        cutoff_time = datetime.now() - timedelta(hours=24)
        for report in data.get('reports', []):
            try:
                report_time = datetime.fromisoformat(report.get('analyzed_at', '').replace('Z', '+00:00'))
                if report_time > cutoff_time:
                    recent_reports.append(report)
            except:
                continue
    
    # Get top sources
    sources = {}
    for report in data.get('reports', []):
        source = report.get('original_article', {}).get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    return {
        'total_reports': total_reports,
        'recent_reports': len(recent_reports),
        'summary': data.get('summary', {}),
        'reports': data.get('reports', [])[-10:],  # Last 10 reports
        'sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]),
        'metadata': data.get('metadata', {})
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = get_dashboard_data()
    return render_template('dashboard.html', data=data)

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    data = get_dashboard_data()
    return jsonify(data)

@app.route('/api/reports')
def api_reports():
    """API endpoint for reports with filtering"""
    storage = DataStorage()
    data = storage.load_existing_data()
    
    # Get filter parameters
    urgency = request.args.get('urgency')
    topic = request.args.get('topic')
    region = request.args.get('region')
    limit = int(request.args.get('limit', 50))
    
    reports = data.get('reports', [])
    
    # Apply filters
    if urgency:
        reports = [r for r in reports if r.get('urgency') == urgency]
    if topic:
        reports = [r for r in reports if r.get('topic') == topic]
    if region:
        reports = [r for r in reports if r.get('region') == region]
    
    # Limit results
    reports = reports[-limit:]
    
    return jsonify({'reports': reports})

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """API endpoint to trigger data collection"""
    try:
        max_articles = int(request.json.get('max_articles', 5))
        
        # Check if API key is configured
        if not Config.GOOGLE_API_KEY:
            return jsonify({
                'success': False, 
                'message': 'Google API key not configured. Please add GOOGLE_API_KEY to your .env file.'
            })
        
        # Collect articles
        collector = RSSCollector()
        feeds = collector.load_feeds()
        articles = collector.collect_all_feeds(feeds, max_articles)
        
        if not articles:
            return jsonify({'success': False, 'message': 'No articles collected'})
        
        # Process with Gemini
        processor = OSINTProcessor()
        processed_articles = processor.process_articles(articles)
        analysis_summary = processor.get_analysis_summary(processed_articles)
        
        # Save results
        storage = DataStorage()
        storage.save_reports(processed_articles, analysis_summary)
        
        return jsonify({
            'success': True,
            'message': f'Collected and processed {len(processed_articles)} articles',
            'articles_processed': len(processed_articles)
        })
        
    except Exception as e:
        logger.error(f"Error in collection: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/report/<report_id>')
def report_detail(report_id):
    """Individual report detail page"""
    storage = DataStorage()
    data = storage.load_existing_data()
    
    # Find the specific report
    report = None
    for r in data.get('reports', []):
        if r.get('id') == report_id:
            report = r
            break
    
    if not report:
        return "Report not found", 404
    
    return render_template('report_detail.html', report=report)

@app.route('/export/csv')
def export_csv():
    """Export data to CSV"""
    try:
        storage = DataStorage()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/noctua_export_{timestamp}.csv"
        storage.export_to_csv(output_file)
        
        return jsonify({
            'success': True,
            'message': f'Data exported to {output_file}',
            'file': output_file
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🦉 Noctua Dashboard starting...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    print("🔧 Make sure you have your Google API key configured in .env")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 