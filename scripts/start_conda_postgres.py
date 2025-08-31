#!/usr/bin/env python3
"""
Start PostgreSQL from conda environment
"""

import os
import sys
import subprocess
import time
import psycopg2

def start_conda_postgres():
    """Start PostgreSQL from conda environment"""
    print("🚀 Starting PostgreSQL from conda environment...")
    
    # Get conda environment path
    conda_env = os.environ.get('CONDA_PREFIX')
    if not conda_env:
        print("❌ Conda environment not found")
        return False
    
    print(f"✅ Conda environment: {conda_env}")
    
    # PostgreSQL data directory in conda environment
    data_dir = os.path.join(conda_env, "Library", "postgresql", "data")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ PostgreSQL data directory not found: {data_dir}")
        print("📦 Initializing PostgreSQL data directory...")
        
        # Initialize PostgreSQL data directory
        try:
            result = subprocess.run(['initdb', '-D', data_dir], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ PostgreSQL data directory initialized")
            else:
                print(f"❌ Failed to initialize data directory: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error initializing data directory: {e}")
            return False
    
    # Start PostgreSQL server
    try:
        print("🔄 Starting PostgreSQL server...")
        
        # Start PostgreSQL in background
        process = subprocess.Popen([
            'pg_ctl', 'start', '-D', data_dir, '-l', 
            os.path.join(data_dir, 'postgresql.log')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        result = subprocess.run(['pg_ctl', 'status', '-D', data_dir], 
                              capture_output=True, text=True)
        
        if "server is running" in result.stdout:
            print("✅ PostgreSQL server started successfully")
            return True
        else:
            print("❌ PostgreSQL server failed to start")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting PostgreSQL: {e}")
        return False

def test_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        # Try to connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="postgres"
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function"""
    print("🗄️  Conda PostgreSQL Starter")
    print("=" * 40)
    
    # Start PostgreSQL
    if not start_conda_postgres():
        print("\n❌ Failed to start PostgreSQL")
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print("\n❌ Database connection test failed")
        sys.exit(1)
    
    print("\n🎉 PostgreSQL is running and ready!")
    print("📋 You can now:")
    print("   1. Run: python scripts/setup_database.py")
    print("   2. Run: python scripts/init_db.py")
    print("   3. Add Netherlands and Italy to your database")

if __name__ == "__main__":
    main()
