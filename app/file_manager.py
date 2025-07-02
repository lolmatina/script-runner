import os
import shutil
import json
import mimetypes
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import base64

class FileOutputManager:
    """Manages file outputs from script executions"""
    
    def __init__(self, base_output_dir: str = "script_outputs", cleanup_after_email: bool = None):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Configure cleanup behavior from environment variable or parameter
        if cleanup_after_email is None:
            # Check environment variable, default to False if not set (changed for better UX)
            cleanup_after_email = os.getenv("CLEANUP_FILES_AFTER_EMAIL", "false").lower() in ("true", "1", "yes")
        
        self.cleanup_after_email = cleanup_after_email
        
        # File type categories
        self.file_categories = {
            'images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'data': ['.csv', '.xlsx', '.xls', '.json', '.xml', '.tsv'],
            'charts': ['.png', '.jpg', '.svg', '.html'],  # Chart outputs
            'reports': ['.html', '.pdf', '.md'],
            'other': []  # Catch-all
        }
        
        # Allowed file extensions for security
        self.allowed_extensions = set()
        for extensions in self.file_categories.values():
            self.allowed_extensions.update(extensions)
    
    def create_execution_workspace(self, execution_id: int, user_id: int) -> Path:
        """Create a temporary workspace for script execution"""
        workspace_dir = self.base_output_dir / f"execution_{execution_id}_{user_id}"
        workspace_dir.mkdir(exist_ok=True)
        return workspace_dir
    
    def scan_for_output_files(self, workspace_dir: Path, before_files: set = None) -> List[Dict]:
        """
        Scan workspace for new files created during script execution
        """
        if not workspace_dir.exists():
            return []
        
        all_files = set()
        for file_path in workspace_dir.rglob("*"):
            if file_path.is_file():
                all_files.add(file_path)
        
        # Get only new files if before_files provided
        if before_files:
            new_files = all_files - before_files
        else:
            new_files = all_files
        
        # Process and categorize files
        output_files = []
        for file_path in new_files:
            if self.is_allowed_file(file_path):
                file_info = self.analyze_file(file_path, workspace_dir)
                output_files.append(file_info)
        
        return sorted(output_files, key=lambda x: x['name'])
    
    def is_allowed_file(self, file_path: Path) -> bool:
        """Check if file type is allowed"""
        extension = file_path.suffix.lower()
        return extension in self.allowed_extensions or extension == ''
    
    def analyze_file(self, file_path: Path, workspace_dir: Path) -> Dict:
        """Analyze file and return metadata"""
        try:
            stats = file_path.stat()
            extension = file_path.suffix.lower()
            
            # Determine category
            category = 'other'
            for cat, extensions in self.file_categories.items():
                if extension in extensions:
                    category = cat
                    break
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Relative path from workspace
            relative_path = file_path.relative_to(workspace_dir)
            
            # File hash for integrity
            file_hash = self.calculate_file_hash(file_path)
            
            return {
                'name': file_path.name,
                'path': str(relative_path),
                'full_path': str(file_path),
                'size': stats.st_size,
                'size_human': self.format_file_size(stats.st_size),
                'extension': extension,
                'category': category,
                'mime_type': mime_type or 'application/octet-stream',
                'created': datetime.fromtimestamp(stats.st_ctime),
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'hash': file_hash,
                'is_viewable': self.is_viewable_file(extension, mime_type),
                'is_downloadable': True
            }
        except Exception as e:
            return {
                'name': file_path.name,
                'path': str(file_path),
                'error': f"Failed to analyze file: {str(e)}",
                'category': 'error'
            }
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()[:16]  # First 16 chars
        except:
            return "unknown"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def is_viewable_file(self, extension: str, mime_type: str) -> bool:
        """Check if file can be viewed in browser"""
        viewable_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.txt', '.html', '.json', '.csv'}
        viewable_mimes = {'text/', 'image/'}
        
        return (extension in viewable_extensions or 
                any(mime_type.startswith(mime) for mime in viewable_mimes))
    
    def move_files_to_permanent_storage(self, workspace_dir: Path, execution_id: int) -> Path:
        """Move files from workspace to permanent storage"""
        permanent_dir = self.base_output_dir / "permanent" / str(execution_id)
        permanent_dir.mkdir(parents=True, exist_ok=True)
        
        if workspace_dir.exists():
            # Copy all files to permanent storage
            for item in workspace_dir.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(workspace_dir)
                    target_path = permanent_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
        
        return permanent_dir
    
    def cleanup_workspace(self, workspace_dir: Path):
        """Clean up temporary workspace"""
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
    
    def cleanup_old_executions(self, days: int = 30):
        """Clean up old execution directories"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for execution_dir in self.base_output_dir.glob("execution_*"):
            try:
                if execution_dir.is_dir():
                    # Check if directory is old enough
                    dir_modified = datetime.fromtimestamp(execution_dir.stat().st_mtime)
                    if dir_modified < cutoff_date:
                        shutil.rmtree(execution_dir)
            except Exception as e:
                print(f"Error cleaning up {execution_dir}: {e}")
    
    def get_file_download_info(self, execution_id: int, file_path: str) -> Optional[Dict]:
        """Get file information for download"""
        permanent_dir = self.base_output_dir / "permanent" / str(execution_id)
        full_file_path = permanent_dir / file_path
        
        if not full_file_path.exists() or not full_file_path.is_file():
            return None
        
        # Security check - ensure file is within permanent directory
        try:
            full_file_path.resolve().relative_to(permanent_dir.resolve())
        except ValueError:
            return None  # Path traversal attempt
        
        return {
            'path': full_file_path,
            'name': full_file_path.name,
            'size': full_file_path.stat().st_size,
            'mime_type': mimetypes.guess_type(str(full_file_path))[0] or 'application/octet-stream'
        }
    
    def get_file_content_for_email(self, file_path: Path, max_size_mb: int = 10) -> Optional[Dict]:
        """Get file content for email attachment"""
        try:
            file_size = file_path.stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                return None  # File too large for email
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            return {
                'filename': file_path.name,
                'content': base64.b64encode(content).decode(),
                'mime_type': mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream',
                'size': file_size
            }
        except Exception:
            return None
    
    def create_file_summary(self, output_files: List[Dict]) -> Dict:
        """Create summary of output files"""
        if not output_files:
            return {'total': 0, 'categories': {}, 'total_size': 0}
        
        summary = {
            'total': len(output_files),
            'categories': {},
            'total_size': 0,
            'total_size_human': '0 B'
        }
        
        for file_info in output_files:
            category = file_info.get('category', 'other')
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
            summary['total_size'] += file_info.get('size', 0)
        
        summary['total_size_human'] = self.format_file_size(summary['total_size'])
        
        return summary

    def cleanup_execution_files(self, execution_id: int) -> bool:
        """
        Clean up files for a specific execution after they've been sent via email
        Returns True if cleanup was successful, False otherwise
        """
        try:
            permanent_dir = self.base_output_dir / "permanent" / str(execution_id)
            
            if permanent_dir.exists():
                # Remove the entire execution directory
                shutil.rmtree(permanent_dir)
                print(f"✅ Cleaned up files for execution {execution_id}")
                return True
            else:
                print(f"⚠️ No files found for execution {execution_id} (already cleaned up)")
                return True  # Consider this successful since files are already gone
                
        except Exception as e:
            print(f"❌ Error cleaning up files for execution {execution_id}: {e}")
            return False

# Global file manager instance
file_manager = FileOutputManager() 