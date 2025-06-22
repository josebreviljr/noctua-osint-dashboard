import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('noctua.log')
        ]
    )

def safe_json_loads(json_string: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string, handling potential errors"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error parsing JSON: {e}")
        return None

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = " ".join(text.split())
    
    # Remove common HTML entities
    cleaned = cleaned.replace("&nbsp;", " ")
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = cleaned.replace("&lt;", "<")
    cleaned = cleaned.replace("&gt;", ">")
    cleaned = cleaned.replace("&quot;", '"')
    
    return cleaned.strip()

def format_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to specified length, preserving word boundaries"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space] + "..."
    else:
        truncated = truncated + "..."
    
    return truncated 