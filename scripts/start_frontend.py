#!/usr/bin/env python3
"""
Frontend startup script for ShortSelling.eu
Checks conda environment and starts the React development server
"""

import os
import sys
import subprocess

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

def install_dependencies():
    """Install frontend dependencies"""
    print("📦 Installing frontend dependencies...")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Error: Frontend directory not found: {frontend_dir}")
        return False
    
    try:
        os.chdir(frontend_dir)
        print(f"📁 Working directory: {os.getcwd()}")
        
        print("🔄 Running: npm install")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            return False
        
        print("✅ Frontend dependencies installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_frontend():
    """Start the React development server"""
    print("🚀 Starting React development server...")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    try:
        os.chdir(frontend_dir)
        
        print("🔄 Running: npm start")
        print("📱 Frontend will be available at: http://localhost:3000")
        print("⏹️  Press Ctrl+C to stop the server")
        
        subprocess.run(['npm', 'start'])
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend server: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎯 ShortSelling.eu Frontend Startup Script")
    print("=" * 50)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_frontend()

if __name__ == "__main__":
    main()