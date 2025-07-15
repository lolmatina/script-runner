# 🚀 FastAPI Script Runner with Advanced File Management

**A comprehensive Python script execution platform with intelligent file output management, email integration, and enterprise-level features.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🎯 **What's New**: Added optional file cleanup after email delivery! Files are preserved by default for web download, with optional cleanup available to save disk space. Better user experience while maintaining flexibility.

## 🌟 Why Choose This Platform?

| Feature | Benefit |
|---------|---------|
| 🖥️ **Web-Based Execution** | Run Python scripts without installing anything locally |
| 📧 **Smart Email Integration** | Get results delivered automatically with attachments |
| 🧹 **Auto File Cleanup** | Save disk space with intelligent cleanup after email delivery |
| 📦 **Package Auto-Install** | Missing packages? We'll install them automatically |
| 🔐 **Enterprise Security** | Admin invitations, secure sessions, sandboxed execution |
| 🎨 **Modern UI** | Beautiful, responsive interface with real-time feedback |

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🏗️ Architecture](#️-architecture)
- [📖 Usage Guide](#-usage-guide)
- [🧪 Script Development](#-script-development)
- [⚙️ Configuration](#️-configuration)
- [🔒 Security](#-security)
- [🆘 Troubleshooting](#-troubleshooting)
- [🚀 Performance](#-performance)
- [📚 API Reference](#-api-reference)

---

## ✨ Features

### 🎯 **Core Capabilities**
- **🖥️ Web-Based Script Execution**: Run Python scripts through a modern, responsive web interface
- **📁 Advanced File Output Management**: Intelligent handling of 50+ file types with automatic organization
- **📧 Smart Email Integration**: Automatic email delivery with file attachments and professional HTML reports
- **🧹 Automatic File Cleanup**: Optional cleanup of files after email delivery to save disk space
- **📦 Intelligent Package Management**: Auto-detection and installation of missing Python packages
- **🔐 Enterprise Security**: Session-based authentication with admin invitation system
- **🎨 Modern UI**: Bootstrap 5 responsive design with real-time feedback and file visualization

### 📧 **Email Integration with Attachments**
- **Automatic email notifications** for all script executions with detailed reports
- **File attachments** - small files (≤5MB) attached directly to emails
- **Professional HTML reports** with execution details, output, and file listings
- **Download links** in emails for larger files and complete file access
- **Gmail SMTP support** with app password configuration
- **Automatic file cleanup** after email delivery to save disk space

### 📦 **Intelligent Package Management**
- **Automatic dependency detection** - scans scripts for required packages
- **Auto-install option** - automatically install missing packages during execution
- **Smart package substitution** - automatically replaces problematic packages (e.g., `psycopg2` → `psycopg2-binary`)
- **Package verification** - verifies packages can be imported after installation to prevent timing issues
- **Installation retry logic** - prevents script execution until packages are properly available
- **Version specifier support** (e.g., `pandas>=1.0`, `numpy==2.0`)
- **Manual requirements** - admins can specify additional packages
- **Installation feedback** - real-time package installation status and warnings
- **Helpful error messages** - clear guidance when installation fails with retry suggestions

### 🎨 **Enhanced User Interface**
- **Modern Bootstrap 5 design** with responsive layout and dark/light themes
- **File output visualization** - cards showing generated files with type-specific icons
- **Real-time execution tracking** with unique execution IDs and detailed logs
- **Package status indicators** and installation progress
- **Professional dashboard** with comprehensive script information and history

---

## 🚀 Quick Start

### **Prerequisites**
- **Python 3.8+** (recommended: Python 3.9+)
- **Git** for cloning the repository
- **Gmail account** (optional, for email features)

### **1. Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd sanzhar

# Install dependencies
pip install -r requirements.txt
```

### **2. Initialize Database**
```bash
# Set up database with sample scripts
python init_db.py

# Optional: Force reset database
python init_db.py --force
```

### **3. Configure Email (Recommended)**
Create a `.env` file in the project root:

```env
# Gmail SMTP Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Script Runner App
BASE_URL=http://localhost:8000

# File Management
CLEANUP_FILES_AFTER_EMAIL=true

# Security (change in production)
SECRET_KEY=your-super-secret-key-change-this
ADMIN_PASSWORD=admin123
```

#### **📧 Gmail App Password Setup:**
1. **Enable 2-Factor Authentication** on your Google Account
2. Go to **Google Account Settings** → **Security** → **App passwords**
3. **Generate a new app password** for "Mail"
4. **Use the 16-digit password** in your `.env` file
5. See `GMAIL_SETUP.md` for detailed instructions

### **4. Run the Application**
```bash
# Development mode
python -m app.main

# Or with uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **5. Access the Application**
- **🌐 Main Application**: http://localhost:8000
- **⚙️ Admin Panel**: http://localhost:8000/admin (password: `admin123`) - Full user & script management
- **📊 User Dashboard**: http://localhost:8000/dashboard

### **6. Try It Out!**
1. **Login as admin** → Upload a script or use the 8 built-in sample scripts
2. **Invite a user** → Send email invitation or create manual registration link
3. **Run scripts** → Execute with auto-package installation and file generation
4. **Check email** → Receive results with file attachments automatically
5. **Enjoy cleanup** → Files are automatically cleaned up after email (configurable)

---

## 🏗️ Architecture

### **📁 Project Structure**
```
sanzhar/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and routes
│   ├── auth.py                 # Authentication and security
│   ├── database.py             # SQLAlchemy models and database
│   ├── email_service.py        # Gmail SMTP with attachments
│   ├── file_manager.py         # Advanced file output management
│   ├── package_manager.py      # Python package installation
│   ├── scripts/                # User-uploaded Python scripts
│   │   ├── __init__.py
│   │   ├── hello_world.py      # Sample: Text output only
│   │   ├── calculator.py       # Sample: Interactive calculator
│   │   ├── data_analyzer.py    # Sample: Data analysis with files
│   │   ├── image_processor.py  # Sample: Image generation
│   │   ├── document_generator.py # Sample: Document creation
│   │   ├── data_export.py      # Sample: Data export formats
│   │   ├── file_organizer.py   # Sample: File organization
│   │   └── mixed_output.py     # Sample: Text + File output
│   └── templates/              # Enhanced HTML templates
│       ├── base.html           # Base template with file support
│       ├── dashboard.html      # Dashboard with file visualization
│       ├── admin.html          # Admin panel with enhanced features
│       ├── login.html          # User authentication
│       ├── register.html       # User registration
│       └── ...
├── script_outputs/             # Generated file storage
│   ├── permanent/              # Organized by execution ID
│   │   ├── 1/                  # Files from execution #1
│   │   ├── 2/                  # Files from execution #2
│   │   └── ...
│   └── execution_*/            # Temporary workspaces (auto-cleaned)
├── app.db                      # SQLite database
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initialization script
├── .env                        # Email and security configuration
├── GMAIL_SETUP.md             # Detailed email setup guide
└── README.md                  # This comprehensive guide
```

### **🔄 Execution Flow**
1. **🔐 User Authentication**: Login or admin invitation system
2. **📋 Script Selection**: Choose from available scripts with descriptions
3. **⚙️ Dependency Check**: Automatic scanning for required packages
4. **📦 Package Installation**: Auto-install missing packages (optional)
5. **🚀 Script Execution**: Run in isolated workspace with file monitoring
6. **📁 File Processing**: Categorize and organize generated files by type
7. **📧 Email Delivery**: Send results with attachments and download links
8. **🧹 Cleanup**: Optional automatic file cleanup after successful email

### **🗃️ Database Schema**
- **Users**: Authentication and profile management
- **Scripts**: Metadata, requirements, and file upload information
- **ScriptExecutions**: Execution history, results, and file tracking
- **Invitations**: Admin invitation system with token management

---

## 📖 Usage Guide

### 🔧 **Admin Panel** (`/admin`)

#### **📁 Script Management:**
1. **Upload Scripts**: 
   - Drag & drop Python files or use file picker
   - Add name, description, and expected output type
   - System automatically detects imports and dependencies

2. **📝 Edit Scripts**: 
   - **Edit metadata**: Update name, description, and requirements
   - **Package management**: Modify required packages and versions
   - **Output type settings**: Change expected output configuration
   - **Bulk operations**: Efficient management of multiple scripts

3. **🗑️ Delete Scripts**: 
   - **Safe deletion**: Confirmation dialog prevents accidental removal
   - **File cleanup**: Automatically removes script files from disk
   - **History tracking**: Shows execution count before deletion
   - **Database cleanup**: Maintains referential integrity

4. **📊 Enhanced Listing**:
   - **Detailed table**: View all script metadata in organized columns
   - **Action buttons**: Quick edit and delete options for each script
   - **Requirements display**: See package dependencies at a glance
   - **Output type badges**: Visual indicators for script output types

5. **Package Requirements**: 
   - Specify required packages: `pandas>=1.0, matplotlib, numpy`
   - Auto-detection suggests missing packages
   - Version specifiers supported
   - Edit requirements post-upload

6. **Output Type Configuration**:
   - **📝 Text Only**: Scripts that only output to stdout/stderr
   - **📁 Files Only**: Scripts that generate files (PDFs, images, data)
   - **📁📝 Both**: Scripts with text output AND file generation

#### **👥 User Management:**
- **📧 Email Invitations**: Automatic invitation emails with registration links
- **🔗 Manual Invitations**: Copy invitation links for manual distribution  
- **📊 User Monitoring**: View registered users with login history and status
- **🔒 Access Control**: Manage user permissions and invitations
- **🔑 Password Reset**: Admin can reset user passwords with email notification
- **👤 User Status**: Activate/deactivate user accounts as needed
- **📋 Enhanced User Table**: Shows last login, registration date, and status
- **📧 Security Notifications**: Automatic email alerts for password changes

#### **⚙️ System Configuration:**
- **📧 Email Status**: Check Gmail SMTP configuration and test connections
- **📊 Storage Monitoring**: View disk usage and file statistics
- **🧹 Cleanup Settings**: Configure automatic file cleanup behavior
- **🚪 Admin Logout**: Secure logout with session cleanup and redirect

### 👤 **User Dashboard** (`/dashboard`)

#### **⚡ Script Execution:**
1. **📋 Select Script**: Browse available scripts with descriptions and requirements
2. **⚙️ Enter Arguments**: 
   - Single values: `30`
   - Multiple arguments: `arg1 arg2 arg3`
   - JSON arrays: `["value1", "value2"]`
3. **📦 Package Options**: Enable "Auto-install missing packages" if needed
4. **🚀 Execute**: Run script and view real-time progress

#### **📊 Results Management:**
- **📄 Text Output**: Formatted stdout/stderr with syntax highlighting
- **📁 File Downloads**: Visual cards with download buttons and metadata
- **🏷️ File Categories**: Organized by type (Images, Documents, Data, etc.)
- **📧 Email Notifications**: Automatic delivery with attachments
- **🔗 Sharing**: Direct download links for individual files

#### **📈 Execution History:**
- **📊 Execution Tracking**: View all past executions with unique IDs
- **📁 File Access**: Download files from previous executions (if not cleaned up)
- **🔄 Re-execution**: Run scripts again with different parameters
- **📋 Detailed Logs**: Full execution logs with error details

---

## 🧪 Script Development

### **📋 Supported File Types (50+)**

#### **📊 Data & Analytics**
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`, `.tsv`
- **Data Formats**: `.json`, `.xml`, `.yaml`, `.parquet`
- **Databases**: `.db`, `.sqlite`, `.sql`

#### **📄 Documents & Reports**
- **Documents**: `.pdf`, `.docx`, `.txt`, `.md`, `.rtf`
- **Presentations**: `.pptx`, `.odp`
- **Web**: `.html`, `.css`, `.js`

#### **🖼️ Images & Media**
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.svg`
- **Charts**: Interactive `.html` charts, static `.png` plots
- **Graphics**: `.eps`, `.ps`, `.webp`

#### **🔧 Technical Formats**
- **Archives**: `.zip`, `.tar`, `.gz`
- **Logs**: `.log`, `.txt`
- **Config**: `.ini`, `.conf`, `.toml`

### **📝 Script Development Guidelines**

#### **Example 1: Data Analysis with Multiple Outputs**
```python
#!/usr/bin/env python3
"""
Advanced Data Analysis Script
Requirements: pandas, matplotlib, seaborn, numpy
Output: CSV data, PNG charts, JSON summary, HTML report
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import sys
from datetime import datetime, timedelta

def generate_sample_data(days=30):
    """Generate realistic sample data"""
    dates = pd.date_range(end=datetime.now(), periods=days)
    base_trend = np.linspace(1000, 1200, days)
    seasonal = 100 * np.sin(np.arange(days) * 2 * np.pi / 7)  # Weekly pattern
    noise = np.random.normal(0, 50, days)
    sales = base_trend + seasonal + noise
    
    return pd.DataFrame({
        'date': dates,
        'sales': np.maximum(sales, 0),
        'category': np.random.choice(['A', 'B', 'C'], days),
        'region': np.random.choice(['North', 'South', 'East', 'West'], days)
    })

def create_visualizations(df):
    """Create multiple chart types"""
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # 1. Time series plot
    plt.figure(figsize=(14, 6))
    plt.plot(df['date'], df['sales'], marker='o', linewidth=2, markersize=4)
    plt.title('Sales Trend Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Sales ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('sales_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Category analysis
    plt.figure(figsize=(10, 6))
    category_sales = df.groupby('category')['sales'].sum()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    plt.pie(category_sales.values, labels=category_sales.index, 
            autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('Sales Distribution by Category', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('category_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Regional heatmap
    pivot_data = df.pivot_table(values='sales', index='region', 
                               columns='category', aggfunc='mean')
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_data, annot=True, cmap='YlOrRd', fmt='.0f')
    plt.title('Average Sales by Region and Category', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('regional_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_reports(df):
    """Generate detailed reports"""
    
    # 1. JSON Summary
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'data_period': {
            'start': df['date'].min().isoformat(),
            'end': df['date'].max().isoformat(),
            'days': len(df)
        },
        'sales_metrics': {
            'total_sales': float(df['sales'].sum()),
            'average_daily': float(df['sales'].mean()),
            'median_daily': float(df['sales'].median()),
            'max_daily': float(df['sales'].max()),
            'min_daily': float(df['sales'].min()),
            'std_deviation': float(df['sales'].std())
        },
        'category_breakdown': df.groupby('category')['sales'].sum().to_dict(),
        'regional_breakdown': df.groupby('region')['sales'].sum().to_dict(),
        'top_performing_day': {
            'date': df.loc[df['sales'].idxmax(), 'date'].isoformat(),
            'sales': float(df['sales'].max())
        }
    }
    
    with open('sales_analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    # 2. HTML Report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .metric {{ background-color: #e8f4fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Sales Analysis Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Sales:</strong> ${summary['sales_metrics']['total_sales']:,.2f}<br>
            <strong>Average Daily Sales:</strong> ${summary['sales_metrics']['average_daily']:,.2f}<br>
            <strong>Analysis Period:</strong> {len(df)} days
        </div>
        
        <h2>Performance Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Sales</td><td>${summary['sales_metrics']['total_sales']:,.2f}</td></tr>
            <tr><td>Average Daily</td><td>${summary['sales_metrics']['average_daily']:,.2f}</td></tr>
            <tr><td>Median Daily</td><td>${summary['sales_metrics']['median_daily']:,.2f}</td></tr>
            <tr><td>Best Day</td><td>${summary['sales_metrics']['max_daily']:,.2f}</td></tr>
            <tr><td>Standard Deviation</td><td>${summary['sales_metrics']['std_deviation']:,.2f}</td></tr>
        </table>
        
        <h2>Category Performance</h2>
        <table>
            <tr><th>Category</th><th>Total Sales</th><th>Percentage</th></tr>
    """
    
    total_sales = sum(summary['category_breakdown'].values())
    for category, sales in summary['category_breakdown'].items():
        percentage = (sales / total_sales) * 100
        html_report += f"<tr><td>{category}</td><td>${sales:,.2f}</td><td>{percentage:.1f}%</td></tr>"
    
    html_report += """
        </table>
    </body>
    </html>
    """
    
    with open('sales_analysis_report.html', 'w') as f:
        f.write(html_report)
    
    # 3. CSV Export
    df.to_csv('sales_data_export.csv', index=False)

def main():
    """Main execution function"""
    print("🚀 Starting Advanced Sales Analysis...")
    
    # Parse arguments
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"📊 Analyzing {days} days of sales data")
    
    # Generate data
    df = generate_sample_data(days)
    print(f"✅ Generated {len(df)} data points")
    
    # Create visualizations
    print("📈 Creating visualizations...")
    create_visualizations(df)
    print("✅ Created 3 chart files")
    
    # Generate reports
    print("📄 Generating reports...")
    generate_reports(df)
    print("✅ Created detailed reports")
    
    # Summary
    total_sales = df['sales'].sum()
    avg_sales = df['sales'].mean()
    
    print(f"\n📋 Analysis Complete!")
    print(f"   • Total Sales: ${total_sales:,.2f}")
    print(f"   • Average Daily: ${avg_sales:,.2f}")
    print(f"   • Files Generated: 7")
    print(f"   • Charts: 3 PNG files")
    print(f"   • Reports: JSON, HTML, CSV")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

#### **Example 2: Document Generator**
```python
#!/usr/bin/env python3
"""
Multi-Format Document Generator
Requirements: reportlab, markdown, jinja2
Output: PDF, HTML, Markdown, TXT reports
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import markdown
import json
import sys
from datetime import datetime
from pathlib import Path

def generate_pdf_report(title, content):
    """Generate PDF using ReportLab"""
    c = canvas.Canvas("report.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, title)
    
    # Content
    c.setFont("Helvetica", 12)
    y_position = height - 100
    for line in content.split('\n'):
        c.drawString(50, y_position, line)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    
    c.save()

def main():
    content_type = sys.argv[1] if len(sys.argv) > 1 else "report"
    
    # Generate content
    title = f"Generated {content_type.title()} - {datetime.now().strftime('%Y-%m-%d')}"
    content = f"""
    This is a sample {content_type} generated at {datetime.now()}.
    
    Key features:
    - Multi-format output
    - Professional styling
    - Automated generation
    - Email integration
    """
    
    # Generate PDF
    generate_pdf_report(title, content)
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        <pre>{content}</pre>
    </body>
    </html>
    """
    with open("report.html", "w") as f:
        f.write(html_content)
    
    # Generate Markdown
    md_content = f"# {title}\n\n{content}"
    with open("report.md", "w") as f:
        f.write(md_content)
    
    # Generate plain text
    with open("report.txt", "w") as f:
        f.write(f"{title}\n{'=' * len(title)}\n\n{content}")
    
    # Generate JSON metadata
    metadata = {
        "title": title,
        "generated": datetime.now().isoformat(),
        "type": content_type,
        "files": ["report.pdf", "report.html", "report.md", "report.txt"]
    }
    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Generated {len(metadata['files']) + 1} files")
    return 0

if __name__ == "__main__":
    exit(main())
```

### **📋 Script Requirements Format**
```python
# Method 1: Inline comments (auto-detected)
# Requirements: pandas>=1.0, matplotlib, numpy==1.21.0

# Method 2: In script metadata (when uploading)
# Specify in admin panel: "pandas>=1.0, matplotlib>=3.0, seaborn"

# Method 3: Environment detection
import pandas  # Auto-detected as requirement
import matplotlib.pyplot as plt  # Auto-detected
```

---

## ⚙️ Configuration

### **📧 Email Configuration**

#### **Required Environment Variables**
```env
# Gmail SMTP Settings
GMAIL_EMAIL=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-gmail@gmail.com
FROM_NAME=Your Organization Name
BASE_URL=http://localhost:8000

# Optional SMTP Overrides
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
```

#### **File Management Settings**
```env
# Automatic cleanup after email (default: true)
CLEANUP_FILES_AFTER_EMAIL=true

# File size limits (in MB)
MAX_EMAIL_ATTACHMENT_SIZE=5
MAX_INDIVIDUAL_FILE_SIZE=100
MAX_TOTAL_OUTPUT_SIZE=500
```

#### **Security Configuration**
```env
# Application Security
SECRET_KEY=your-super-secret-key-for-jwt-tokens
ADMIN_PASSWORD=your-secure-admin-password

# Database
DATABASE_URL=sqlite:///./app.db

# Development vs Production
DEBUG=false
```

### **🧹 File Cleanup Behavior**

#### **How Cleanup Works**
1. **Script Execution**: Files are generated in permanent storage
2. **Email Sending**: System attempts to send files via email
3. **Cleanup Decision**:
   - ✅ **Email Success + Cleanup Enabled**: Files automatically deleted
   - ❌ **Email Fails**: Files preserved regardless of cleanup setting
   - 🔒 **Cleanup Disabled**: Files always preserved

#### **Configuration Options**
```env
# Enable automatic cleanup
CLEANUP_FILES_AFTER_EMAIL=true

# Disable cleanup - keep all files (default)
CLEANUP_FILES_AFTER_EMAIL=false

# If not set, defaults to false (files preserved)
```

#### **Benefits & Considerations**
**✅ Benefits (when enabled):**
- Saves disk space and prevents unlimited file accumulation
- Maintains user privacy (files don't linger indefinitely)
- Reduces server storage costs for high-volume usage
- Files are safely delivered via email before cleanup

**🔒 Default Behavior (cleanup disabled):**
- Files remain available for web download after email sending
- Users can access files both from email attachments and web interface
- Better user experience with persistent file access
- Manual cleanup can be performed when needed

**⚠️ Considerations (when cleanup enabled):**
- Files are permanently deleted after successful email
- Users should save important files from email attachments
- Can be disabled if permanent file retention is needed
- Cleanup only occurs after confirmed email delivery

### **📦 Package Management**
```env
# Package installation settings
AUTO_INSTALL_PACKAGES=true
PACKAGE_INSTALL_TIMEOUT=300
PIP_INDEX_URL=https://pypi.org/simple/
```

### **🔒 Advanced Security**
```env
# Session management
ACCESS_TOKEN_EXPIRE_MINUTES=60
COOKIE_SECURE=true
COOKIE_HTTPONLY=true

# Rate limiting
MAX_EXECUTIONS_PER_HOUR=50
MAX_FILE_SIZE_MB=100
```

---

## 🔒 Security

### **🛡️ Authentication & Authorization**
- **Admin-only script uploads** with invitation-based user registration
- **JWT token-based sessions** with configurable expiration
- **Secure password hashing** using bcrypt
- **CSRF protection** and secure cookie handling

### **📁 File Security**
- **Path traversal prevention** - all file operations are sandboxed
- **File type validation** - only allowed extensions are processed
- **Size limits** - configurable maximum file sizes
- **Automatic cleanup** - prevents indefinite file accumulation

### **🔐 Email Security**
- **App passwords** instead of regular passwords for Gmail
- **TLS encryption** for all email communications
- **No password storage** - credentials in environment variables only
- **Secure attachment handling** with size limits

### **⚡ Execution Security**
- **Isolated execution environments** for each script
- **Resource limits** to prevent system abuse
- **Package verification** before installation
- **Error sanitization** in user-facing messages

### **🏭 Production Recommendations**
```env
# Strong secret key (32+ characters)
SECRET_KEY=super-long-random-key-for-production-use-only

# Secure admin password
ADMIN_PASSWORD=complex-admin-password-with-numbers-123

# HTTPS in production
BASE_URL=https://your-domain.com
COOKIE_SECURE=true

# Database security
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Rate limiting
MAX_EXECUTIONS_PER_HOUR=20
```

---

## 🆘 Troubleshooting

### **📧 Email Issues**

#### **"Authentication failed" Error**
```bash
❌ Problem: Gmail authentication failure
✅ Solutions:
   1. Enable 2-Factor Authentication on Google Account
   2. Generate app password (not regular password)
   3. Use 16-digit app password in GMAIL_APP_PASSWORD
   4. Check email address in GMAIL_EMAIL
```

#### **"Email not received" Issue**
```bash
❌ Problem: Users not receiving emails
✅ Solutions:
   1. Check recipient's spam/junk folder
   2. Verify recipient email address
   3. Test with your own email first
   4. Check Gmail sending limits (500 emails/day)
```

#### **"Connection failed" Error**
```bash
❌ Problem: Cannot connect to Gmail SMTP
✅ Solutions:
   1. Check internet connection
   2. Verify firewall allows port 587
   3. Try different network/VPN
   4. Check corporate firewall restrictions
```

### **📦 Package Installation Issues**

#### **"Package installation failed"**
```bash
❌ Problem: Cannot install required packages
✅ Solutions:
   1. Check internet connection
   2. Update pip: python -m pip install --upgrade pip
   3. Clear pip cache: pip cache purge
   4. Install manually: pip install package_name
   5. Check package name spelling
```

#### **"PostgreSQL/psycopg2 installation error"**
```bash
❌ Problem: "pg_config executable not found" when installing psycopg2
✅ Solutions:
   • System automatically uses 'psycopg2-binary' instead
   • Manual fix: pip install psycopg2-binary
   • Alternative: Install PostgreSQL development headers:
     - Windows: Install PostgreSQL with dev tools
     - Ubuntu/Debian: sudo apt-get install libpq-dev
     - macOS: brew install postgresql
```

#### **"MySQL/mysqlclient installation error"**
```bash
❌ Problem: "mysql_config not found" when installing mysqlclient
✅ Solutions:
   • System automatically uses 'PyMySQL' instead
   • Manual fix: pip install PyMySQL
   • Alternative: Install MySQL development headers:
     - Ubuntu/Debian: sudo apt-get install libmysqlclient-dev
     - macOS: brew install mysql
```

#### **"Module not found" After Installation**
```bash
❌ Problem: Package installed but import fails
✅ Solutions:
   1. Restart the application
   2. Check Python environment
   3. Verify package name vs import name
   4. Install in same environment as app
```

#### **"Script fails on first run but works on retry"**
```bash
❌ Problem: Script execution fails on first run with package installation
✅ What's Fixed:
   • Added package verification after installation
   • System now ensures packages are importable before script execution
   • Enhanced error messages guide users through retry process
   
🔧 Automatic Solutions:
   1. Package installation now includes import verification
   2. Script execution is blocked until packages are confirmed available
   3. Better error messages suggest retrying if verification fails
   
📋 If Still Having Issues:
   1. Try running the script again (packages might need environment refresh)
   2. Restart the application to clear module cache
   3. Check manual package installation: pip install package_name
   4. Verify package names in script requirements match actual package names
```

### **📁 File Access Issues**

#### **"Permission denied" Errors**
```bash
# Windows
icacls script_outputs /grant Everyone:F /T

# Linux/Mac
chmod -R 755 script_outputs/
chown -R $USER:$USER script_outputs/
```

#### **"File not found" Errors**
```bash
❌ Problem: Generated files not accessible
✅ Solutions:
   1. Check if files were cleaned up after email (see cleanup settings)
   2. Verify execution ID is correct
   3. Check script_outputs/permanent/{execution_id}/ directory
   4. Ensure file permissions are correct
```

### **👥 User Management Issues**

#### **"Cannot reset user password"**
```bash
❌ Problem: Password reset fails in admin panel
✅ Solutions:
   1. Verify admin authentication is valid
   2. Check user exists in database
   3. Ensure new password meets minimum requirements (6+ characters)
   4. Check database write permissions
   5. Verify email configuration for notifications
```

#### **"Email notification not sent"**
```bash
❌ Problem: User doesn't receive password reset email
✅ Solutions:
   1. Check Gmail SMTP configuration in .env file
   2. Verify recipient email address is correct
   3. Check spam/junk folder
   4. Test email connection: Admin Panel → Email Configuration
   5. Ensure GMAIL_APP_PASSWORD is correct
```

#### **"User status toggle fails"**
```bash
❌ Problem: Cannot activate/deactivate users
✅ Solutions:
   1. Verify admin authentication is valid
   2. Check user exists in database  
   3. Ensure database write permissions
   4. Try refreshing the admin panel page
   5. Check browser console for JavaScript errors
```

#### **"Last login shows 'Never'"**
```bash
❌ Problem: Users show 'Never' for last login despite recent activity
✅ Solutions:
   1. Database migration needed - run migration script if upgrading
   2. Users need to log in again after migration to update timestamp
   3. Check if last_login column exists in users table
   4. Verify login process is updating the timestamp correctly
   2. Verify file paths in script
   3. Check if cleanup removed files
   4. Look in correct execution directory
```

### **⚡ Script Execution Problems**

#### **"Script execution timeout"**
```bash
❌ Problem: Scripts taking too long
✅ Solutions:
   1. Optimize script performance
   2. Reduce data size/complexity
   3. Add progress prints to script
   4. Check for infinite loops
```

#### **"Import errors" in Scripts**
```bash
❌ Problem: Missing module imports
✅ Solutions:
   1. Enable "Auto-install packages" option
   2. Add requirements in admin panel
   3. Install packages manually
   4. Check package spelling and versions
```

### **🔐 Authentication Problems**

#### **"Invalid credentials" Error**
```bash
❌ Problem: Cannot login to admin/user account
✅ Solutions:
   1. Check admin password in .env file
   2. Reset database: python init_db.py --force
   3. Clear browser cookies
   4. Use incognito/private browsing
```

#### **"Session expired" Issues**
```bash
❌ Problem: Frequent logouts
✅ Solutions:
   1. Increase ACCESS_TOKEN_EXPIRE_MINUTES in .env
   2. Check system clock accuracy
   3. Clear browser data
   4. Check network stability
```

### **🐛 Debug Mode**
```bash
# Enable debug logging
DEBUG=true

# Check application logs
python -m app.main  # Watch console output

# Test email configuration
python -c "
from app.email_service import email_service
success, message = email_service.test_connection()
print(message)
"

# Test file manager
python -c "
from app.file_manager import file_manager
print(f'Cleanup enabled: {file_manager.cleanup_after_email}')
"
```

---

## 🚀 Performance

### **⚡ System Requirements**

#### **Minimum Requirements**
- **CPU**: 2 cores, 1.5 GHz
- **RAM**: 2 GB available
- **Storage**: 5 GB free space
- **Python**: 3.8+
- **Network**: Stable internet for packages/email

#### **Recommended for Production**
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB available
- **Storage**: 50+ GB SSD
- **Python**: 3.9+
- **Network**: High-speed internet

### **📊 Performance Optimization**

#### **Database Optimization**
```python
# For high-volume usage, consider PostgreSQL
# Update database.py connection string
DATABASE_URL=postgresql://user:pass@localhost/production_db

# Regular cleanup of old executions
file_manager.cleanup_old_executions(days=30)
```

#### **File Management Optimization**
```env
# Enable cleanup to save disk space
CLEANUP_FILES_AFTER_EMAIL=true

# Adjust file size limits based on needs
MAX_EMAIL_ATTACHMENT_SIZE=5
MAX_INDIVIDUAL_FILE_SIZE=50
MAX_TOTAL_OUTPUT_SIZE=200
```

#### **Email Performance**
```env
# Reduce email attachment size for faster sending
MAX_EMAIL_ATTACHMENT_SIZE=3

# Batch email sending (future enhancement)
EMAIL_BATCH_SIZE=10
EMAIL_RETRY_ATTEMPTS=3
```

### **📈 Scaling Considerations**

#### **Single Server Scaling**
- Use **production WSGI server** (Gunicorn, uWSGI)
- Enable **reverse proxy** (nginx, Apache)
- Implement **database connection pooling**
- Add **Redis** for session storage

#### **Multi-Server Scaling**
- **Load balancer** for web servers
- **Shared file storage** (NFS, cloud storage)
- **External database** (PostgreSQL cluster)
- **Message queue** for script execution (Celery + Redis)

---

## 📚 API Reference

### **🔗 Main Endpoints**

#### **Authentication**
```http
POST /login                 # User login
POST /logout               # User logout
GET  /register?token=xxx   # User registration with invitation
```

#### **Admin Panel**
```http
GET  /admin                # Admin dashboard
POST /admin/upload-script  # Upload new script
POST /admin/invite-user    # Send invitation email
```

#### **Script Execution**
```http
GET  /dashboard           # User dashboard
POST /run-script          # Execute script
GET  /download/{exec_id}/{file_path}  # Download generated file
```

### **📊 Database Models**

#### **User Model**
```python
class User:
    id: int
    email: str
    password_hash: str
    is_admin: bool
    created_at: datetime
```

#### **Script Model**
```python
class Script:
    id: int
    name: str
    description: str
    filename: str
    requirements: str
    output_type: str  # 'text', 'files', 'both'
    created_at: datetime
```

#### **ScriptExecution Model**
```python
class ScriptExecution:
    id: int
    user_id: int
    script_id: int
    arguments: str
    return_code: int
    stdout: str
    stderr: str
    error_message: str
    output_files: str  # JSON
    created_at: datetime
```

### **🛠️ File Manager API**

#### **FileOutputManager Methods**
```python
# Create execution workspace
workspace = file_manager.create_execution_workspace(exec_id, user_id)

# Scan for generated files
files = file_manager.scan_for_output_files(workspace, before_files)

# Move to permanent storage
permanent_dir = file_manager.move_files_to_permanent_storage(workspace, exec_id)

# Clean up after email
success = file_manager.cleanup_execution_files(exec_id)

# Get file for download
file_info = file_manager.get_file_download_info(exec_id, file_path)
```

---

## 📋 Dependencies

### **Core Dependencies**
```txt
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
sqlalchemy==2.0.23        # Database ORM
bcrypt==4.1.2             # Password hashing
python-jose==3.3.0        # JWT tokens
python-multipart==0.0.6   # File upload support
jinja2==3.1.2             # Template engine
python-dotenv==1.0.0      # Environment variables
```

### **Email & Communication**
```txt
yagmail==0.15.293         # Gmail SMTP integration
keyring==24.3.0           # Credential management
```

### **File Processing**
```txt
pillow==10.1.0            # Image processing
pandas==2.1.4             # Data analysis
matplotlib==3.8.2         # Plotting and charts
seaborn==0.13.0           # Statistical visualization
reportlab==4.0.7          # PDF generation
openpyxl==3.1.2           # Excel file support
```

### **Development & Testing**
```txt
pytest==7.4.3            # Testing framework
requests==2.31.0          # HTTP client for testing
httpx==0.25.2             # Async HTTP client
```

---

## 🎯 Use Cases

### **🏢 Enterprise Applications**
- **Data Analysis Automation**: Regular reporting with email delivery
- **Document Generation**: Automated report creation and distribution
- **Image Processing**: Batch image manipulation and optimization
- **ETL Workflows**: Data extraction, transformation, and loading

### **🎓 Educational Environments**
- **Student Assignments**: Safe script execution with file submission
- **Research Projects**: Data analysis with result sharing
- **Code Testing**: Automated testing with result visualization
- **Tutorial Platform**: Interactive Python learning environment

### **🔬 Research & Development**
- **Experiment Automation**: Automated data collection and analysis
- **Model Training**: ML model execution with result tracking
- **Data Visualization**: Automated chart and graph generation
- **Report Generation**: Research report creation and distribution

### **🏭 Operations & DevOps**
- **System Monitoring**: Automated status reports and alerts
- **Log Analysis**: Automated log processing and visualization
- **Backup Automation**: Automated backup processes with notifications
- **Performance Monitoring**: System performance analysis and reporting

---

## 🚀 Future Enhancements

### **📅 Planned Features**
- **🗓️ Scheduled Execution**: Cron-like scheduling for automated runs
- **📊 Advanced Analytics**: Execution statistics and performance metrics
- **🔗 API Access**: REST API for programmatic script execution
- **📱 Mobile Interface**: Responsive mobile app interface
- **🏢 SSO Integration**: Single Sign-On with enterprise systems

### **🔧 Technical Improvements**
- **⚡ Async Execution**: Background script execution with progress tracking
- **🐳 Containerization**: Docker support for easy deployment
- **☁️ Cloud Storage**: Integration with AWS S3, Google Cloud, Azure
- **📈 Monitoring**: Integration with monitoring tools (Prometheus, Grafana)
- **🔒 Enhanced Security**: Role-based access control and audit logs

---

## 📞 Support & Contributing

### **🐛 Bug Reports**
- Use GitHub Issues for bug reports
- Include error messages and reproduction steps
- Specify environment details (OS, Python version)

### **💡 Feature Requests**
- Submit feature requests via GitHub Issues
- Describe the use case and expected behavior
- Consider contributing the implementation

### **🤝 Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### **📞 Getting Help**
- Check this README and `GMAIL_SETUP.md` first
- Search existing GitHub Issues
- Create a new issue with detailed information
- Join community discussions

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Acknowledgments

- **FastAPI** for the excellent web framework
- **Bootstrap** for the responsive UI components
- **Gmail** for reliable email delivery
- **Python Community** for the extensive package ecosystem

---

**⭐ Star this repository if you find it useful!**

**📧 Questions? Create an issue or contact the maintainers.**

**🚀 Ready to run your Python scripts like a pro? Get started with the Quick Start guide above!** 