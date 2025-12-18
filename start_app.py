#!/usr/bin/env python3
"""
Startup script for the QA Agent application.
This script starts both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def start_fastapi():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend on port 8000...")
    try:
        # Change to backend directory and run uvicorn
        backend_dir = os.path.join(os.getcwd(), "backend")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--port", "8000",
            "--host", "0.0.0.0"
        ], cwd=backend_dir, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  FastAPI backend stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def start_streamlit():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend on port 8501...")
    time.sleep(3)  # Wait for FastAPI to start
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", 
            "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Streamlit frontend stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'chromadb', 
        'sentence-transformers', 'selenium', 'pymupdf', 'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            # Handle special package name mappings
            import_name = package.replace('-', '_')
            if package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'sentence-transformers':
                import_name = 'sentence_transformers'
            
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 QA Agent - Test Case & Script Generator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies found")
    print("\n🔧 Starting services...")
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in main thread
        start_streamlit()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down QA Agent...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()