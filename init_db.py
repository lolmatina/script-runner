#!/usr/bin/env python3
"""
Database initialization script
Adds sample scripts to the database for testing
"""

import sys
from app.database import SessionLocal, create_tables, Script
from datetime import datetime

def init_database(force_reset=False):
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if scripts already exist
        existing_scripts = db.query(Script).count()
        if existing_scripts > 0 and not force_reset:
            print(f"Database already has {existing_scripts} scripts.")
            print("Use --force to reset and reload all scripts, or --add to add missing scripts.")
            return
        
        if force_reset and existing_scripts > 0:
            print(f"🔄 Force reset requested. Removing {existing_scripts} existing scripts...")
            db.query(Script).delete()
            db.commit()
            print("✅ Existing scripts removed.")
        
        # Add sample scripts
        sample_scripts = [
            {
                "name": "Hello World",
                "filename": "hello_world.py",
                "description": "Enhanced hello world script with comprehensive argument handling, environment info, and help system. Perfect for testing text-only output.",
                "requirements": "",
                "output_types": "text"
            },
            {
                "name": "Calculator",
                "filename": "calculator.py", 
                "description": "Advanced calculator with basic arithmetic, mathematical functions, expression evaluation, and interactive mode. Supports operations like +, -, *, /, sqrt, sin, cos, etc.",
                "requirements": "",
                "output_types": "text"
            },
            {
                "name": "Data Analyzer",
                "filename": "data_analyzer.py",
                "description": "Comprehensive data analysis script that generates sample sales data, creates visualizations, and exports multiple file formats. Creates charts, CSV, JSON, and text reports.",
                "requirements": "pandas, matplotlib, numpy",
                "output_types": "files"
            },
            {
                "name": "Image Processor",
                "filename": "image_processor.py",
                "description": "Image generation and processing script that creates various types of images including basic shapes, processed versions, charts, and composite images with metadata.",
                "requirements": "pillow, matplotlib",
                "output_types": "files"
            },
            {
                "name": "Document Generator",
                "filename": "document_generator.py",
                "description": "Professional document creation script that generates PDF reports, styled HTML documents, formatted text files, Markdown documentation, and JSON metadata.",
                "requirements": "reportlab, jinja2",
                "output_types": "files"
            },
            {
                "name": "Data Export",
                "filename": "data_export.py",
                "description": "Business data export script that generates sample business data and exports it in multiple formats: Excel (with multiple sheets), CSV, XML, JSON, TSV, and summary reports.",
                "requirements": "pandas, openpyxl",
                "output_types": "files"
            },
            {
                "name": "Mixed Output Demo",
                "filename": "mixed_output.py",
                "description": "Demonstrates both rich text output AND file generation. Creates charts, data files, and reports while providing detailed console analysis and progress updates.",
                "requirements": "matplotlib",
                "output_types": "both"
            },
            {
                "name": "File Organizer",
                "filename": "file_organizer.py",
                "description": "Creates organized directory structures with multiple file types. Tests the system's handling of subdirectories and complex file organization. No external dependencies required.",
                "requirements": "",
                "output_types": "files"
            }
        ]
        
        for script_data in sample_scripts:
            script = Script(**script_data)
            db.add(script)
        
        db.commit()
        print(f"Successfully added {len(sample_scripts)} sample scripts to the database.")
        
        # List all scripts with details
        all_scripts = db.query(Script).all()
        print(f"\n🎉 Available scripts ({len(all_scripts)} total):")
        print("=" * 60)
        
        # Group by output type
        text_scripts = []
        file_scripts = []
        both_scripts = []
        
        for script in all_scripts:
            output_type = getattr(script, 'output_types', 'text')
            if output_type == 'text':
                text_scripts.append(script)
            elif output_type == 'files':
                file_scripts.append(script)
            elif output_type == 'both':
                both_scripts.append(script)
        
        # Display by category
        if text_scripts:
            print("\n📝 TEXT OUTPUT SCRIPTS:")
            for script in text_scripts:
                req_text = f" (Requires: {script.requirements})" if getattr(script, 'requirements', '') else ""
                print(f"  • {script.name} - {script.filename}{req_text}")
        
        if file_scripts:
            print("\n📁 FILE OUTPUT SCRIPTS:")
            for script in file_scripts:
                req_text = f" (Requires: {script.requirements})" if getattr(script, 'requirements', '') else ""
                print(f"  • {script.name} - {script.filename}{req_text}")
        
        if both_scripts:
            print("\n🔄 MIXED OUTPUT SCRIPTS:")
            for script in both_scripts:
                req_text = f" (Requires: {script.requirements})" if getattr(script, 'requirements', '') else ""
                print(f"  • {script.name} - {script.filename}{req_text}")
        
        print("\n✨ Database initialization complete!")
        print("🚀 You can now run scripts through the web interface at http://localhost:8000")
        print("⚙️  Admin panel available at http://localhost:8000/admin (password: admin123)")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

def show_help():
    """Show help information"""
    print("📚 DATABASE INITIALIZATION SCRIPT")
    print("=" * 50)
    print()
    print("DESCRIPTION:")
    print("   Initializes the database with sample scripts for testing")
    print("   the Script Runner platform's capabilities.")
    print()
    print("USAGE:")
    print("   python init_db.py [options]")
    print()
    print("OPTIONS:")
    print("   --force     Delete existing scripts and reload all")
    print("   --add       Add missing scripts (keep existing ones)")
    print("   --help      Show this help message")
    print()
    print("EXAMPLES:")
    print("   python init_db.py")
    print("   python init_db.py --force")
    print("   python init_db.py --add")
    print()

if __name__ == "__main__":
    # Parse command line arguments
    force_reset = '--force' in sys.argv
    add_missing = '--add' in sys.argv
    show_help_flag = '--help' in sys.argv or '-h' in sys.argv
    
    if show_help_flag:
        show_help()
        sys.exit(0)
    
    if add_missing:
        print("⚠️ --add option not yet implemented. Use --force to reset all scripts.")
        sys.exit(1)
    
    print("🚀 SCRIPT RUNNER DATABASE INITIALIZATION")
    print("=" * 50)
    
    try:
        init_database(force_reset=force_reset)
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 