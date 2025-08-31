#!/usr/bin/env python3
"""
Backend startup script for ShortSelling.eu
Works both locally and on Railway deployment
"""

import os
import sys
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_conda_env():
    """Check if we're in the correct conda environment (only for local dev)"""
    # Skip conda check if we're in a container (Railway deployment)
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return True
        
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
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting FastAPI backend...")
    print(f"📡 Backend will be available at: http://0.0.0.0:{port}")
    if port == 8000:
        print("📚 API docs will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Use reload only for local development
    reload = port == 8000 and not os.environ.get('RAILWAY_ENVIRONMENT')
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port,
        reload=reload
    )

def main():
    """Main startup function"""
    print("🎯 ShortSelling.eu Backend Startup Script")
    print("=" * 50)
    
    # Check conda environment (skip for Railway)
    if not check_conda_env():
        sys.exit(1)
    
    start_backend()

if __name__ == "__main__":
    main()