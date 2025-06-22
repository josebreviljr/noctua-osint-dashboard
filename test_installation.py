#!/usr/bin/env python3
"""
Test script to verify Noctua installation and dependencies
"""

import sys
import importlib

def test_imports():
    """Test that all required modules can be imported"""
    required_modules = [
        'feedparser',
        'google.generativeai', 
        'requests',
        'tqdm',
        'dotenv'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_local_modules():
    """Test that local modules can be imported"""
    local_modules = [
        'config',
        'collector', 
        'processor',
        'storage',
        'utils'
    ]
    
    print("\nTesting local module imports...")
    failed_imports = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("✅ Config class imported")
        
        # Test that we can access config (API key will be None without .env)
        print(f"   Gemini Model: {Config.GEMINI_MODEL}")
        print(f"   Max Articles: {Config.MAX_ARTICLES_PER_FEED}")
        print(f"   Feeds File: {Config.FEEDS_FILE}")
        print(f"   Output File: {Config.OUTPUT_FILE}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_feeds_file():
    """Test that feeds.txt exists and is readable"""
    print("\nTesting feeds file...")
    
    try:
        with open('feeds.txt', 'r') as f:
            feeds = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"✅ feeds.txt found with {len(feeds)} feeds")
        for i, feed in enumerate(feeds[:3], 1):
            print(f"   {i}. {feed}")
        if len(feeds) > 3:
            print(f"   ... and {len(feeds) - 3} more")
        
        return True
    except FileNotFoundError:
        print("❌ feeds.txt not found")
        return False
    except Exception as e:
        print(f"❌ Error reading feeds.txt: {e}")
        return False

def main():
    """Run all tests"""
    print("🦉 Noctua Installation Test")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Configuration", test_config),
        ("Feeds File", test_feeds_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Noctua is ready to use.")
        print("\nNext steps:")
        print("1. Copy env.example to .env")
        print("2. Add your Google API key to .env")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 