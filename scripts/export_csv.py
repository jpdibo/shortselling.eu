#!/usr/bin/env python3
"""
CSV Export Script for ShortSelling.eu
Exports all data to CSV files for manual inspection
"""

import asyncio
import sys
import os
from app.services.csv_manager import CSVManager
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

async def export_data():
    """Export all data to CSV files"""
    try:
        print("📊 Starting CSV export...")
        
        csv_manager = CSVManager()
        exported_files = await csv_manager.export_all_data()
        
        print("✅ Export completed successfully!")
        print(f"📁 Export directory: {csv_manager.export_dir}")
        print("\n📋 Exported files:")
        
        for file_type, filepath in exported_files.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                size_mb = round(size / (1024 * 1024), 2)
                print(f"   • {file_type}: {os.path.basename(filepath)} ({size_mb} MB)")
        
        # Show summary
        summary = csv_manager.get_export_summary()
        print(f"\n📈 Summary:")
        print(f"   • Total files: {summary.get('total_files', 0)}")
        print(f"   • Total size: {sum(f['size_mb'] for f in summary.get('files', [])):.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        return False

async def export_consolidated_only():
    """Export only the consolidated positions file"""
    try:
        print("📊 Starting consolidated CSV export...")
        
        csv_manager = CSVManager()
        exported_files = await csv_manager.export_all_data()
        
        consolidated_file = exported_files.get('consolidated')
        if consolidated_file and os.path.exists(consolidated_file):
            size = os.path.getsize(consolidated_file)
            size_mb = round(size / (1024 * 1024), 2)
            
            print("✅ Consolidated export completed!")
            print(f"📁 File: {os.path.basename(consolidated_file)}")
            print(f"📊 Size: {size_mb} MB")
            print(f"📍 Location: {consolidated_file}")
            
            return True
        else:
            print("❌ Consolidated file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error during consolidated export: {e}")
        return False

def main():
    """Main function"""
    print("📊 ShortSelling.eu CSV Export Tool")
    print("=" * 40)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--consolidated":
        success = asyncio.run(export_consolidated_only())
    else:
        success = asyncio.run(export_data())
    
    if success:
        print("\n🎉 Export completed successfully!")
        print("\n💡 You can now:")
        print("   • Open the CSV files in Excel or Google Sheets")
        print("   • Use the consolidated_positions file for analysis")
        print("   • Access files via API at: http://localhost:8000/api/csv/files")
    else:
        print("\n❌ Export failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
