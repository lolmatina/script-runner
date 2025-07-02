#!/usr/bin/env python3
"""
File Organizer Script
Demonstrates creating organized directory structures with multiple file types
Tests the file management system's handling of subdirectories
No external requirements (uses only standard library)
"""

import sys
import os
import json
from datetime import datetime
import random

def create_directory(dir_name):
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(dir_name, exist_ok=True)
        print(f"Created directory: {dir_name}/")
        return dir_name
    except Exception as e:
        print(f"Failed to create directory {dir_name}: {e}")
        return None

def create_summary_file(filename="project_summary.txt"):
    """Create a project summary file."""
    content = f"""PROJECT ORGANIZATION SUMMARY
{"=" * 40}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Purpose: Demonstrate file organization capabilities

This directory structure was created by the File Organizer Script
to showcase different types of files and directory organization.

DIRECTORY STRUCTURE:
- reports/        : Analysis and summary files
- data/          : Data files in various formats  
- logs/          : Application and error logs
- config/        : Configuration files
- backup/        : Backup and archive files

Each directory contains sample files demonstrating different
file types and organization patterns commonly used in projects.

For more information about each file, see the detailed
documentation in 'file_details.txt'.
"""
    
    summary_file = os.path.join(os.getcwd(), filename)
    with open(summary_file, 'w') as f:
        f.write(content)
    
    print(f"Created: {summary_file}")
    return summary_file

def create_detail_file(filename="file_details.txt"):
    """Create a detailed file listing."""
    content = f"""DETAILED FILE DOCUMENTATION
{"=" * 40}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document provides detailed information about each file
created by the File Organizer Script.

REPORT FILES:
- project_summary.txt  : Overview of the entire project structure
- file_details.txt     : This file - detailed documentation
- analysis_report.csv  : Sample data analysis in CSV format
- project_data.json    : Project metadata in JSON format

LOG FILES:
- application.log      : Sample application log entries
- error.log           : Sample error log entries

CONFIGURATION FILES:
- main_config.ini     : Primary configuration file
- settings.json       : Application settings in JSON

BACKUP FILES:
- project_manifest.txt : Complete project file listing

Each file serves as an example of the type of content and
organization patterns typically found in software projects.
"""
    
    detail_file = os.path.join(os.getcwd(), filename)
    with open(detail_file, 'w') as f:
        f.write(content)
    
    print(f"Created: {detail_file}")
    return detail_file

def create_csv_file(filename="analysis_report.csv"):
    """Create a sample CSV file."""
    csv_file = os.path.join(os.getcwd(), filename)
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value', 'Status', 'Notes'])
        writer.writerow(['Files Created', '15+', 'Complete', 'All file types generated'])
        writer.writerow(['Directories', '5', 'Complete', 'Organized structure'])
        writer.writerow(['File Types', '8', 'Complete', 'TXT, CSV, JSON, LOG, INI, etc.'])
        writer.writerow(['Organization', 'Hierarchical', 'Complete', 'Category-based structure'])
        writer.writerow(['Documentation', 'Comprehensive', 'Complete', 'Multiple detail levels'])
    
    print(f"Created: {csv_file}")
    return csv_file

def create_json_file(filename="project_data.json"):
    """Create a sample JSON file."""
    data = {
        "project": {
            "name": "File Organization Demo",
            "version": "1.0",
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "description": "Demonstration of automated file organization"
        },
        "statistics": {
            "total_files": 15,
            "directories": 5,
            "file_types": ["txt", "csv", "json", "log", "ini"],
            "organization_method": "categorical"
        },
        "structure": {
            "reports": {
                "purpose": "Analysis and summary files",
                "file_count": 4
            },
            "data": {
                "purpose": "Data files in various formats",
                "file_count": 2
            },
            "logs": {
                "purpose": "Application and error logs", 
                "file_count": 2
            },
            "config": {
                "purpose": "Configuration files",
                "file_count": 2
            },
            "backup": {
                "purpose": "Backup and archive files",
                "file_count": 1
            }
        }
    }
    
    json_file = os.path.join(os.getcwd(), filename)
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Created: {json_file}")
    return json_file

def create_app_log(filename="application.log"):
    """Create a sample application log file."""
    log_entries = [
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Starting file organization process",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Created project directory structure",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Generated summary documentation",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Created data files",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Generated configuration files",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Created backup manifest",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO File organization completed successfully",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO Total processing time: <1 second"
    ]
    
    app_log = os.path.join(os.getcwd(), filename)
    with open(app_log, 'w') as f:
        for entry in log_entries:
            f.write(entry + '\n')
    
    print(f"Created: {app_log}")
    return app_log

def create_error_log(filename="error.log"):
    """Create a sample error log file."""
    error_entries = [
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ERROR Sample error entry for demonstration",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARN This is a sample warning message",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ERROR Another sample error for testing",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARN Configuration value using default",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ERROR Sample database connection timeout",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARN Memory usage above 80% threshold"
    ]
    
    error_log = os.path.join(os.getcwd(), filename)
    with open(error_log, 'w') as f:
        for entry in error_entries:
            f.write(entry + '\n')
    
    print(f"Created: {error_log}")
    return error_log

def create_config_file(filename="main_config.ini"):
    """Create a sample configuration file."""
    config_content = f"""# Main Configuration File
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[DATABASE]
host = localhost
port = 5432
name = project_db
user = admin
timeout = 30

[LOGGING]
level = INFO
file = application.log
max_size = 10MB
backup_count = 5

[FEATURES]
auto_backup = true
compression = enabled
encryption = false
debug_mode = false

[PATHS]
data_directory = ./data/
log_directory = ./logs/
backup_directory = ./backup/
config_directory = ./config/

[PERFORMANCE]
max_connections = 100
cache_size = 256MB
worker_threads = 4
timeout = 60
"""
    
    main_config = os.path.join(os.getcwd(), filename)
    with open(main_config, 'w') as f:
        f.write(config_content)
    
    print(f"Created: {main_config}")
    return main_config

def create_settings_file(filename="settings.json"):
    """Create a settings JSON file."""
    settings = {
        "application": {
            "name": "File Organizer",
            "version": "1.0.0",
            "debug": False
        },
        "ui": {
            "theme": "default",
            "language": "en",
            "auto_save": True
        },
        "performance": {
            "cache_enabled": True,
            "max_memory_mb": 512,
            "worker_count": 4
        },
        "security": {
            "encryption_enabled": False,
            "session_timeout": 3600,
            "max_login_attempts": 3
        }
    }
    
    settings_file = os.path.join(os.getcwd(), filename)
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"Created: {settings_file}")
    return settings_file

def create_backup_manifest(filename="project_manifest.txt"):
    """Create a backup manifest file."""
    manifest_content = f"""PROJECT BACKUP MANIFEST
{"=" * 30}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Purpose: Complete listing of all project files

This manifest serves as a backup reference for all files
created during the file organization process.

DIRECTORY STRUCTURE:
reports/
├── project_summary.txt
├── file_details.txt
├── analysis_report.csv
└── project_data.json

data/
├── sample_data.csv
└── data_export.json

logs/
├── application.log
└── error.log

config/
├── main_config.ini
└── settings.json

backup/
└── project_manifest.txt (this file)

ROOT FILES:
(Additional files may be created in the root directory)

BACKUP NOTES:
- All files are text-based and easily readable
- Configuration files use standard formats
- Log files follow standard logging conventions
- Data files use common interchange formats

For restoration, simply recreate the directory structure
and restore files according to this manifest.
"""
    
    manifest_file = os.path.join(os.getcwd(), filename)
    with open(manifest_file, 'w') as f:
        f.write(manifest_content)
    
    print(f"Created: {manifest_file}")
    return manifest_file

def create_master_index(all_files, filename="master_file_index.txt"):
    """Create a master index of all created files."""
    index_content = f"""MASTER FILE INDEX
{"=" * 20}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Files: {len(all_files)}

This index provides a complete listing of all files created
by the File Organizer Script, including their paths and purposes.

FILE LISTING:
"""
    
    for i, file_path in enumerate(all_files, 1):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path) if os.path.dirname(file_path) else "root"
        index_content += f"{i:2d}. {file_name} (in {file_dir})\n"
    
    index_content += f"""
SUMMARY:
- Total files created: {len(all_files)}
- Organization completed successfully
- All files are ready for use

This index can be used for file verification, backup planning,
or as a reference for the complete project structure.
"""
    
    index_file = os.path.join(os.getcwd(), filename)
    with open(index_file, 'w') as f:
        f.write(index_content)
    
    print(f"Created master index: {index_file}")
    return index_file

def main():
    """Main file organization function."""
    print("FILE ORGANIZER SCRIPT")
    print("=" * 30)
    print("Creating organized file structure with multiple file types")
    print()
    
    # Parse command line arguments
    create_subdirs = True  # Default
    for arg in sys.argv[1:]:
        if arg == '--no-subdirs':
            create_subdirs = False
        elif arg == '--help':
            print("File Organizer Help")
            print("Usage: python file_organizer.py [--no-subdirs]")
            print("Creates organized directory structure with sample files")
            return
    
    print(f"Configuration:")
    print(f"   • Create subdirectories: {'Yes' if create_subdirs else 'No'}")
    print(f"   • Working directory: {os.getcwd()}")
    print(f"   • Script mode: {'Hierarchical' if create_subdirs else 'Flat'}")
    print()
    
    all_files = []
    created_dirs = []
    
    try:
        # Step 1: Create directory structure (if enabled)
        print("Step 1: Creating directory structure...")
        if create_subdirs:
            dirs_to_create = ['reports', 'data', 'logs', 'config', 'backup']
            for dir_name in dirs_to_create:
                created_dir = create_directory(dir_name)
                if created_dir:
                    created_dirs.append(created_dir)
        print(f"Created {len(created_dirs)} directories")
        print()
        
        # Step 2: Create report files
        print("Step 2: Creating report files...")
        all_files.append(create_summary_file("project_summary.txt"))
        all_files.append(create_detail_file("file_details.txt"))
        
        # Step 3: Create data files
        print("Step 3: Creating data files...")
        all_files.append(create_csv_file("analysis_report.csv"))
        all_files.append(create_json_file("project_data.json"))
        
        # Step 4: Create log files
        print("Step 4: Creating log files...")
        all_files.append(create_app_log("application.log"))
        all_files.append(create_error_log("error.log"))
        
        # Step 5: Create config files
        print("Step 5: Creating config files...")
        all_files.append(create_config_file("main_config.ini"))
        all_files.append(create_settings_file("settings.json"))
        
        # Step 6: Create backup files
        print("Step 6: Creating backup files...")
        all_files.append(create_backup_manifest("project_manifest.txt"))
        
        # If subdirectories are disabled, create all files in current directory
        if not create_subdirs:
            print("Creating files in current directory...")
            # All files are already being created in current directory
            # This is just a status message
            
            # Create some additional files for flat structure
            additional_files = [
                "readme.txt",
                "changelog.txt", 
                "license.txt",
                "installation.txt",
                "usage_guide.txt"
            ]
            
            for filename in additional_files:
                file_content = f"""# {filename.replace('_', ' ').title()}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a sample {filename} file created by the File Organizer Script.
It demonstrates file creation in a flat directory structure.

Content would normally include specific information relevant 
to the file type and purpose.
"""
                file_path = os.path.join(os.getcwd(), filename)
                with open(file_path, 'w') as f:
                    f.write(file_content)
                print(f"Created: {file}")
                all_files.append(file_path)
        
        # Step 8: Create master index
        print("Step 8: Creating master index...")
        index_file = create_master_index(all_files, "master_file_index.txt")
        all_files.append(index_file)
        
        # Final summary
        print("\nFILE ORGANIZATION COMPLETE!")
        
        # Remove any None values from the files list
        all_files = [f for f in all_files if f is not None]
        
        print(f"Generated {len(all_files)} files and {len(created_dirs)} directories")
        
        # Count different file types
        file_types = {}
        for file_path in all_files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '':
                ext = '.txt'  # Assume text files without extension
            file_types[ext] = file_types.get(ext, 0) + 1
        
        print(f"Summary Statistics:")
        print(f"   • Total files: {len(all_files)}")
        print(f"   • Total directories: {len(created_dirs)}")
        print(f"   • Subdirectories used: {'Yes' if create_subdirs else 'No'}")
        
        print(f"\nFile Types Created:")
        for ext, count in sorted(file_types.items()):
            print(f"   • {ext}: {count} file(s)")
        
        print(f"\nCreated Files:")
        for i, file_path in enumerate(all_files[:10], 1):  # Show first 10
            file_name = os.path.basename(file_path)
            print(f"   {i:2d}. {file_name}")
        
        if len(all_files) > 10:
            print(f"   ... and {len(all_files) - 10} more files")
        
        print(f"\nDirectory Structure:")
        if create_subdirs:
            for dir_name in created_dirs:
                print(f"   • {dir_name}/")
        else:
            print("   • All files in current directory (flat structure)")
        
        print(f"\nUse 'master_file_index.txt' for complete file listing")
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFile organization interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1) 