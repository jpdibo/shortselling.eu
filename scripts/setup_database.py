#!/usr/bin/env python3
"""
Database setup script for ShortSelling.eu
Sets up PostgreSQL database and initializes tables
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_conda_env():
    """Check if we're in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'short_selling':
        print("❌ Error: Please activate the 'short_selling' conda environment first:")
        print("   conda activate short_selling")
        return False
    print(f"✅ Using conda environment: {conda_env}")
    return True

def check_postgresql_installation():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ PostgreSQL found: {version}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not found in PATH")
        return False

def install_postgresql():
    """Install PostgreSQL using conda"""
    print("\n📦 Installing PostgreSQL...")
    try:
        result = subprocess.run(['conda', 'install', '-c', 'conda-forge', 'postgresql', '-y'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL installed successfully")
            return True
        else:
            print("❌ Failed to install PostgreSQL")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing PostgreSQL: {e}")
        return False

def create_database():
    """Create the shortselling database"""
    print("\n🗄️  Creating database...")
    
    # Database configuration
    DB_NAME = "shortselling"
    DB_USER = "postgres"  # Default PostgreSQL user
    DB_PASSWORD = "postgres"  # Default password - should be changed in production
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created successfully")
        else:
            print(f"✅ Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
        # Test connection to the new database
        test_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        test_conn.close()
        print("✅ Database connection test successful")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 To fix this:")
        print("   1. Make sure PostgreSQL service is running")
        print("   2. Check your database credentials")
        print("   3. Update the .env file with correct database URL")
        return False
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def update_env_file():
    """Update the .env file with database configuration"""
    print("\n⚙️  Updating .env file...")
    
    env_file = ".env"
    env_example = ".env.example"
    
    # Check if .env exists, if not copy from .env.example
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            with open(env_example, 'r') as f:
                content = f.read()
            
            # Update database URL
            content = content.replace(
                'DATABASE_URL=postgresql://username:password@localhost:5432/shortselling',
                'DATABASE_URL=postgresql://postgres:postgres@localhost:5432/shortselling'
            )
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created from .env.example")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def start_postgresql_service():
    """Start PostgreSQL service"""
    print("\n🚀 Starting PostgreSQL service...")
    
    try:
        # Try to start PostgreSQL service
        if os.name == 'nt':  # Windows
            result = subprocess.run(['net', 'start', 'postgresql'], 
                                  capture_output=True, text=True, shell=True)
        else:  # Linux/Mac
            result = subprocess.run(['sudo', 'service', 'postgresql', 'start'], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL service started")
            return True
        else:
            print("⚠️  Could not start PostgreSQL service automatically")
            print("   Please start it manually:")
            if os.name == 'nt':
                print("   - Windows: Start PostgreSQL service from Services")
            else:
                print("   - Linux/Mac: sudo service postgresql start")
            return True  # Continue anyway
            
    except Exception as e:
        print(f"⚠️  Could not start PostgreSQL service: {e}")
        print("   Please start it manually")
        return True  # Continue anyway

def main():
    """Main function"""
    print("🗄️  ShortSelling.eu Database Setup")
    print("=" * 50)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    # Check PostgreSQL installation
    if not check_postgresql_installation():
        print("\n📦 PostgreSQL not found. Installing...")
        if not install_postgresql():
            print("\n❌ Failed to install PostgreSQL")
            print("Please install PostgreSQL manually:")
            print("   - Download from: https://www.postgresql.org/download/")
            print("   - Or use: conda install -c conda-forge postgresql")
            sys.exit(1)
    
    # Start PostgreSQL service
    start_postgresql_service()
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Update .env file
    if not update_env_file():
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run: python scripts/init_db.py")
    print("   2. Run: python scripts/start.py")
    print("   3. Check the application at: http://localhost:8000")

if __name__ == "__main__":
    main()
