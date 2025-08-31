from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
from typing import Dict, Any
from app.services.csv_manager import CSVManager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/csv", tags=["csv"])

csv_manager = CSVManager()

@router.post("/export/all")
async def export_all_data(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Export all data to CSV files"""
    try:
        # Run export in background
        background_tasks.add_task(csv_manager.export_all_data)
        
        return {
            "message": "Export started in background",
            "status": "processing",
            "export_dir": csv_manager.export_dir
        }
    except Exception as e:
        logger.error(f"Error starting export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/all/sync")
async def export_all_data_sync() -> Dict[str, Any]:
    """Export all data to CSV files synchronously"""
    try:
        exported_files = await csv_manager.export_all_data()
        
        return {
            "message": "Export completed successfully",
            "status": "completed",
            "exported_files": exported_files,
            "export_dir": csv_manager.export_dir
        }
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/consolidated")
async def export_consolidated_data() -> Dict[str, Any]:
    """Export only the consolidated positions file"""
    try:
        exported_files = await csv_manager.export_all_data()
        
        return {
            "message": "Consolidated export completed",
            "status": "completed",
            "consolidated_file": exported_files.get('consolidated'),
            "export_dir": csv_manager.export_dir
        }
    except Exception as e:
        logger.error(f"Error exporting consolidated data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_exported_files() -> Dict[str, Any]:
    """List all exported CSV files"""
    try:
        summary = csv_manager.get_export_summary()
        return summary
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_csv_file(filename: str):
    """Download a specific CSV file"""
    try:
        filepath = os.path.join(csv_manager.export_dir, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='text/csv'
        )
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/latest/consolidated")
async def download_latest_consolidated():
    """Download the latest consolidated positions file"""
    try:
        summary = csv_manager.get_export_summary()
        
        # Find the latest consolidated file
        consolidated_files = [
            f for f in summary.get('files', []) 
            if 'consolidated_positions' in f['name']
        ]
        
        if not consolidated_files:
            # Create a new consolidated export
            exported_files = await csv_manager.export_all_data()
            filename = os.path.basename(exported_files.get('consolidated', ''))
        else:
            # Get the most recent file
            latest_file = max(consolidated_files, key=lambda x: x['modified'])
            filename = latest_file['name']
        
        filepath = os.path.join(csv_manager.export_dir, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='text/csv'
        )
    except Exception as e:
        logger.error(f"Error downloading latest consolidated file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/{table_name}")
async def import_from_csv(table_name: str, filepath: str) -> Dict[str, Any]:
    """Import data from CSV file"""
    try:
        success = await csv_manager.import_from_csv(filepath, table_name)
        
        if success:
            return {
                "message": f"Successfully imported data to {table_name}",
                "status": "completed",
                "table": table_name,
                "file": filepath
            }
        else:
            raise HTTPException(status_code=400, detail="Import failed")
            
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_exports(days_to_keep: int = 30) -> Dict[str, Any]:
    """Clean up old CSV export files"""
    try:
        import glob
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_files = []
        
        # Find old files
        pattern = os.path.join(csv_manager.export_dir, "*.csv")
        for filepath in glob.glob(pattern):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff_date:
                os.remove(filepath)
                deleted_files.append(os.path.basename(filepath))
        
        return {
            "message": f"Cleanup completed",
            "deleted_files": deleted_files,
            "files_deleted": len(deleted_files),
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))
