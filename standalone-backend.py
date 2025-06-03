#!/usr/bin/env python
"""Standalone backend for testing"""
import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'resources', 'app.asar.unpacked', 'src', 'python')
if os.path.exists(app_dir):
    sys.path.insert(0, app_dir)
else:
    print(f"Warning: App directory not found: {app_dir}")

# Try to import and run the server
try:
    print("Starting Flask server...")
    import server
except ImportError as e:
    print(f"Error importing server: {e}")
    print("\nTrying to install required packages...")
    os.system("pip install flask flask-cors openpyxl xlwings pandas reportlab")
    print("\nPlease restart this script.")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")
    sys.exit(1)