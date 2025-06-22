#!/usr/bin/env python3
"""
Noctua Dashboard Startup Script
"""

import os
import sys
from config import Config

def main():
    print("🦉 Noctua OSINT Dashboard")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Dashboard will start but collection will require GOOGLE_API_KEY")
        print("Create a .env file with your Google API key for full functionality:")
        print("GOOGLE_API_KEY=your_actual_api_key_here")
    
    # Validate configuration (without requiring API key for dashboard)
    try:
        Config.validate(require_api_key=False)
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file.")
        sys.exit(1)
    
    # Check if data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ Created data directory")
    
    # Check if templates and static directories exist
    for directory in ['templates', 'static', 'static/css', 'static/js']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory} directory")
    
    print("\n🚀 Starting dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Import and run the dashboard
    from dashboard import app
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main() 