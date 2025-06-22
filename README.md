# 🦉 Noctua OSINT Collector & Classifier

A powerful command-line tool and web dashboard for collecting and analyzing Open Source Intelligence (OSINT) from RSS feeds using AI-powered classification.

## 🎯 Features

- **RSS Feed Collection**: Automatically fetches articles from multiple RSS feeds
- **AI-Powered Analysis**: Uses Google Gemini to classify and analyze articles
- **Intelligent Classification**: Extracts region, topic, urgency, and confidence levels
- **Local Storage**: Saves results in structured JSON format
- **Web Dashboard**: Beautiful, interactive web interface for data visualization
- **CSV Export**: Export results for further analysis
- **Configurable**: Easy to customize feeds, limits, and settings

## 📋 Requirements

- Python 3.8+
- Google API key (for Gemini)
- Internet connection for RSS feeds

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your Google API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Run the Pipeline

#### Command Line Interface
```bash
# Basic run with default settings
python main.py

# Collect more articles per feed
python main.py --max-articles 10

# Enable verbose logging
python main.py --verbose

# Dry run (collect without AI processing)
python main.py --dry-run
```

#### Web Dashboard
```bash
# Start the web dashboard
python start_dashboard.py

# Or run directly
python dashboard.py
```

Then open your browser to: **http://localhost:8080**

## 📁 Project Structure

```
Noctua/
├── main.py              # CLI entry point
├── dashboard.py         # Web dashboard server
├── start_dashboard.py   # Dashboard startup script
├── config.py            # Configuration management
├── collector.py         # RSS feed collection
├── processor.py         # Gemini analysis
├── storage.py           # Data storage and export
├── utils.py             # Helper functions
├── feeds.txt            # RSS feed URLs
├── requirements.txt     # Python dependencies
├── env.example          # Environment variables template
├── templates/           # Dashboard HTML templates
│   ├── dashboard.html   # Main dashboard page
│   └── report_detail.html # Individual report view
├── static/              # Dashboard static files
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
├── data/                # Output directory
│   └── reports.json     # Analysis results
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional
GEMINI_MODEL=gemini-1.5-flash
MAX_ARTICLES_PER_FEED=5
FEEDS_FILE=feeds.txt
OUTPUT_FILE=data/reports.json
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### RSS Feeds

Edit `feeds.txt` to add your preferred RSS feeds:

```txt
https://feeds.bbci.co.uk/news/world/rss.xml
https://www.theguardian.com/world/rss
https://feeds.npr.org/1004/rss.xml
https://feeds.feedburner.com/techcrunch
https://feeds.arstechnica.com/arstechnica/index
```

## 📊 Usage Examples

### Command Line Interface

```bash
# Basic collection and analysis
python main.py

# Collect 15 articles per feed
python main.py --max-articles 15

# Use custom feeds file
python main.py --feeds my_feeds.txt

# Custom output location
python main.py --output custom_results.json

# Enable verbose logging
python main.py --verbose

# Export to CSV
python main.py --export-csv

# Dry run (collect without AI processing)
python main.py --dry-run
```

### Web Dashboard

The dashboard provides:

- **Real-time Statistics**: Total reports, recent activity, urgency distribution
- **Interactive Charts**: Visual representation of urgency and topic distribution
- **Report Filtering**: Filter by urgency, topic, and region
- **Data Collection**: Trigger new data collection from the web interface
- **Report Details**: Click on any report for detailed analysis
- **CSV Export**: Export data directly from the dashboard
- **Auto-refresh**: Dashboard updates automatically every 5 minutes

#### Dashboard Features:

1. **Overview Cards**: Quick stats on total reports, recent activity, high urgency items
2. **Charts**: Visual breakdown of urgency levels and top topics
3. **Report List**: Filterable list of all analyzed articles
4. **Collection Controls**: One-click data collection with configurable article limits
5. **Export Functionality**: Download data as CSV
6. **Responsive Design**: Works on desktop, tablet, and mobile

## 📈 Output Format

### JSON Structure

```json
{
  "metadata": {
    "created_at": "2024-01-15T10:30:00",
    "version": "1.0",
    "description": "Noctua OSINT Analysis Data",
    "last_updated": "2024-01-15T10:35:00",
    "total_reports": 25
  },
  "reports": [
    {
      "id": "abc123def456",
      "summary": "Brief summary of the article...",
      "region": "Europe",
      "topic": "Cybersecurity",
      "urgency": "high",
      "confidence": "medium",
      "analyzed_at": "2024-01-15T10:32:00",
      "original_article": {
        "title": "Article Title",
        "link": "https://example.com/article",
        "source": "https://feeds.example.com",
        "published": "2024-01-15T09:00:00"
      }
    }
  ],
  "summary": {
    "total_articles": 25,
    "urgency_distribution": {
      "high": 5,
      "medium": 12,
      "low": 8
    },
    "top_topics": {
      "Cybersecurity": 8,
      "Geopolitics": 6,
      "Technology": 4
    },
    "top_regions": {
      "Europe": 10,
      "North America": 8,
      "Asia-Pacific": 4
    }
  }
}
```

### Analysis Categories

**Regions**: Europe, Middle East, Asia-Pacific, North America, South America, Africa, Global

**Topics**: Cybersecurity, Geopolitics, Economics, Technology, Military, Terrorism, Disasters, Health, Environment

**Urgency Levels**: low, medium, high

**Confidence Levels**: low, medium, high

## 🔍 Command Line Options

```bash
python main.py --help
```

| Option | Description | Default |
|--------|-------------|---------|
| `--max-articles` | Articles per feed | 5 |
| `--feeds` | Custom feeds file | feeds.txt |
| `--output` | Output file path | data/reports.json |
| `--verbose` | Enable verbose logging | False |
| `--dry-run` | Collect without AI processing | False |
| `--export-csv` | Export results to CSV | False |

## 🌐 Dashboard API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/data` | GET | Dashboard data (JSON) |
| `/api/reports` | GET | Filtered reports (JSON) |
| `/api/collect` | POST | Trigger data collection |
| `/export/csv` | GET | Export data to CSV |
| `/report/<id>` | GET | Individual report detail |

## 🛠️ Development

### Adding New Features

1. **New RSS Sources**: Add URLs to `feeds.txt`
2. **Custom Analysis**: Modify the system prompt in `processor.py`
3. **Storage Options**: Extend `storage.py` for new formats
4. **Configuration**: Add new options to `config.py`
5. **Dashboard**: Add new routes to `dashboard.py`

### Testing

```bash
# Test collection without API calls
python main.py --dry-run

# Test with limited articles
python main.py --max-articles 1 --verbose

# Test dashboard
python start_dashboard.py
```

## 📝 Logging

Logs are written to both console and `noctua.log`:

```bash
# Enable debug logging
python main.py --verbose
```

## 🔒 Security Notes

- Keep your Google API key secure
- Never commit `.env` files to version control
- The tool respects rate limits and includes delays between requests
- Dashboard runs on localhost by default

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**"Configuration error: GOOGLE_API_KEY environment variable is required"**
- Make sure you've created a `.env` file with your API key

**"No feeds loaded"**
- Check that `feeds.txt` exists and contains valid RSS URLs

**"Error fetching feed"**
- Verify RSS URLs are accessible
- Check your internet connection

**"Failed to parse Gemini response"**
- This usually indicates an API issue
- Check your Google API key and quota

**"Dashboard won't start"**
- Ensure Flask is installed: `pip install flask`
- Check that all template files are in the `templates/` directory
- Verify your `.env` file is properly configured

### Getting Help

- Check the logs: `tail -f noctua.log`
- Run with verbose mode: `python main.py --verbose`
- Test individual components with dry-run mode
- Check dashboard logs in the terminal where you started it

---

**🦉 Noctua** - Your AI-powered OSINT companion 