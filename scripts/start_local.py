#!/usr/bin/env python3
"""
LOCAL DEVELOPMENT startup script for ShortSelling.eu
This script sets up the environment for local development without interfering with Railway deployment
"""

import os
import sys
import shutil
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def setup_local_env():
    """Set up local development environment"""
    env_local = Path(project_root) / '.env.local'
    env_file = Path(project_root) / '.env'
    
    if env_local.exists():
        # Copy .env.local to .env for local development
        shutil.copy2(env_local, env_file)
        print("✅ Copied .env.local to .env for local development")
        return True
    else:
        print("❌ .env.local not found. Please create it first.")
        return False

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

def check_database():
    """Check if PostgreSQL is running"""
    print("🔍 Checking PostgreSQL connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="shortselling", 
            user="jpdib",
            password="jpdib"
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("💡 Make sure PostgreSQL is running:")
        print('   "C:\\Users\\jpdib\\anaconda3\\envs\\short_selling\\Library\\bin\\pg_ctl.exe" -D "C:\\Users\\jpdib\\anaconda3\\envs\\short_selling\\Library\\postgresql\\data" start')
        return False

def start_backend():
    """Start the FastAPI backend for local development"""
    import uvicorn
    
    print("🚀 Starting LOCAL DEVELOPMENT backend...")
    print("📡 Backend will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    print("🎯 Frontend should run on: http://localhost:3000")
    print()
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Start with reload for local development
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1",  # Localhost only for security
        port=8000,
        reload=True,
        reload_dirs=[project_root]
    )

def main():
    """Main startup function for local development"""
    print("🎯 ShortSelling.eu LOCAL DEVELOPMENT Startup")
    print("=" * 60)
    print("This script sets up local development without affecting Railway")
    print("=" * 60)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    # Set up local environment
    if not setup_local_env():
        sys.exit(1)
        
    # Check database connection
    if not check_database():
        print("\n💡 Start PostgreSQL first, then run this script again")
        sys.exit(1)
    
    print("\n🎉 Local development environment ready!")
    print("📝 To start frontend: cd frontend && npm start")
    print("🌐 Frontend will be at: http://localhost:3000")
    print("🔗 Backend will be at: http://localhost:8000")
    print()
    
    start_backend()

if __name__ == "__main__":
    main()