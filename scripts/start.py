#!/usr/bin/env python3
"""
Backend startup script for ShortSelling.eu
Checks conda environment and starts the FastAPI server
"""

import os
import sys
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_conda_env():
    """Check if we're in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'short_selling':
        print("❌ Error: Please activate the 'short_selling' conda environment first:")
        print("   conda activate short_selling")
        print(f"   Current environment: {conda_env}")
        return False
    print(f"✅ Using conda environment: {conda_env}")
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    print("📡 Backend will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Change to project root directory
        os.chdir(project_root)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")

def main():
    """Main startup function"""
    print("🎯 ShortSelling.eu Backend Startup Script")
    print("=" * 50)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    start_backend()

if __name__ == "__main__":
    main()