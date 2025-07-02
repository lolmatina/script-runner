#!/usr/bin/env python3
"""
Data Export Script
Demonstrates data export capabilities (Excel, CSV, XML, JSON)
Requires: pandas, openpyxl
"""

import sys
import json
import csv
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

def generate_sample_data(rows=100):
    """Generate sample business data"""
    import random
    
    # Sample data categories
    departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations']
    regions = ['North', 'South', 'East', 'West', 'Central']
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    
    data = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(rows):
        record = {
            'id': i + 1,
            'date': (base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            'department': random.choice(departments),
            'region': random.choice(regions),
            'product': random.choice(products),
            'quantity': random.randint(1, 100),
            'unit_price': round(random.uniform(10.0, 500.0), 2),
            'revenue': 0,  # Will calculate
            'employee_id': f"EMP{1000 + i}",
            'customer_id': f"CUST{random.randint(100, 999)}",
            'status': random.choice(['Active', 'Pending', 'Completed', 'Cancelled'])
        }
        record['revenue'] = round(record['quantity'] * record['unit_price'], 2)
        data.append(record)
    
    return data

def create_csv_file(data, filename="export_data.csv"):
    """Create CSV file from data"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Created CSV file: {filename} ({len(data)} records)")
    return filename

def create_excel_file(data, filename="export_data.xlsx"):
    """Create Excel file with multiple sheets"""
    if not HAS_PANDAS or not HAS_OPENPYXL:
        print("Pandas/OpenPyXL not available, creating CSV instead")
        return create_csv_file(data, filename.replace('.xlsx', '.csv'))
    
    df = pd.DataFrame(data)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='All_Data', index=False)
        
        # Summary by department
        dept_summary = df.groupby('department').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'transaction_count'})
        dept_summary.to_excel(writer, sheet_name='Department_Summary')
        
        # Summary by region
        region_summary = df.groupby('region').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'transaction_count'})
        region_summary.to_excel(writer, sheet_name='Region_Summary')
        
        # Top products
        product_summary = df.groupby('product').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'unit_price': 'mean'
        }).sort_values('revenue', ascending=False)
        product_summary.to_excel(writer, sheet_name='Product_Analysis')
        
        # Monthly trends
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_summary = df.groupby('month').agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'transactions'})
        monthly_summary.to_excel(writer, sheet_name='Monthly_Trends')
    
            print(f"Created Excel file: {filename} (5 sheets, {len(data)} records)")
    return filename

def create_xml_file(data, filename="export_data.xml"):
    """Create XML file from data"""
    root = ET.Element("business_data")
    root.set("generated", datetime.now().isoformat())
    root.set("total_records", str(len(data)))
    
    # Add summary information
    summary = ET.SubElement(root, "summary")
    total_revenue = sum(record['revenue'] for record in data)
    total_quantity = sum(record['quantity'] for record in data)
    
    ET.SubElement(summary, "total_revenue").text = str(total_revenue)
    ET.SubElement(summary, "total_quantity").text = str(total_quantity)
    ET.SubElement(summary, "average_transaction").text = str(round(total_revenue / len(data), 2))
    
    # Add records
    records = ET.SubElement(root, "records")
    
    for record in data:
        record_elem = ET.SubElement(records, "record")
        record_elem.set("id", str(record['id']))
        
        for key, value in record.items():
            if key != 'id':  # id is already an attribute
                elem = ET.SubElement(record_elem, key)
                elem.text = str(value)
    
    # Pretty print XML
    rough_string = ET.tostring(root, 'unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"Created XML file: {filename} ({len(data)} records)")
    return filename

def create_json_export(data, filename="export_data.json"):
    """Create JSON file with structured data"""
    # Calculate summary statistics
    total_revenue = sum(record['revenue'] for record in data)
    total_quantity = sum(record['quantity'] for record in data)
    
    # Group by department
    dept_stats = {}
    for record in data:
        dept = record['department']
        if dept not in dept_stats:
            dept_stats[dept] = {'revenue': 0, 'quantity': 0, 'count': 0}
        dept_stats[dept]['revenue'] += record['revenue']
        dept_stats[dept]['quantity'] += record['quantity']
        dept_stats[dept]['count'] += 1
    
    # Group by region
    region_stats = {}
    for record in data:
        region = record['region']
        if region not in region_stats:
            region_stats[region] = {'revenue': 0, 'quantity': 0, 'count': 0}
        region_stats[region]['revenue'] += record['revenue']
        region_stats[region]['quantity'] += record['quantity']
        region_stats[region]['count'] += 1
    
    export_data = {
        "metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "total_records": len(data),
            "data_source": "Business Transaction System",
            "format_version": "1.0"
        },
        "summary_statistics": {
            "total_revenue": round(total_revenue, 2),
            "total_quantity": total_quantity,
            "average_transaction_value": round(total_revenue / len(data), 2),
            "date_range": {
                "earliest": min(record['date'] for record in data),
                "latest": max(record['date'] for record in data)
            }
        },
        "department_breakdown": dept_stats,
        "region_breakdown": region_stats,
        "raw_data": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created JSON export: {filename} ({len(data)} records)")
    return filename

def create_tsv_file(data, filename="export_data.tsv"):
    """Create Tab-Separated Values file"""
    with open(filename, 'w', newline='', encoding='utf-8') as tsvfile:
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Created TSV file: {filename} ({len(data)} records)")
    return filename

def create_summary_report(data, filename="export_summary.txt"):
    """Create a text summary report"""
    total_revenue = sum(record['revenue'] for record in data)
    total_quantity = sum(record['quantity'] for record in data)
    
    # Calculate department statistics
    dept_stats = {}
    for record in data:
        dept = record['department']
        if dept not in dept_stats:
            dept_stats[dept] = []
        dept_stats[dept].append(record['revenue'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("DATA EXPORT SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Records: {len(data):,}\n")
        f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
        f.write(f"Total Quantity: {total_quantity:,}\n")
        f.write(f"Average Transaction: ${total_revenue/len(data):,.2f}\n\n")
        
        f.write("DEPARTMENT ANALYSIS\n")
        f.write("-" * 30 + "\n")
        for dept, revenues in dept_stats.items():
            dept_total = sum(revenues)
            dept_avg = dept_total / len(revenues)
            f.write(f"{dept:12}: ${dept_total:>10,.2f} (avg: ${dept_avg:>8,.2f}) [{len(revenues):>3} transactions]\n")
        
        f.write("\nDATE RANGE ANALYSIS\n")
        f.write("-" * 30 + "\n")
        dates = [record['date'] for record in data]
        f.write(f"Earliest: {min(dates)}\n")
        f.write(f"Latest:   {max(dates)}\n")
        
        f.write("\nPRODUCT PERFORMANCE\n")
        f.write("-" * 30 + "\n")
        product_stats = {}
        for record in data:
            product = record['product']
            if product not in product_stats:
                product_stats[product] = {'revenue': 0, 'quantity': 0}
            product_stats[product]['revenue'] += record['revenue']
            product_stats[product]['quantity'] += record['quantity']
        
        for product, stats in sorted(product_stats.items(), key=lambda x: x[1]['revenue'], reverse=True):
            f.write(f"{product:12}: ${stats['revenue']:>10,.2f} ({stats['quantity']:>4} units)\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("End of Report\n")
    
    print(f"Created summary report: {filename}")
    return filename

def main():
    """Main function"""
    print("DATA EXPORT SCRIPT")
    print("=" * 50)
    
    # Check dependencies
    missing_deps = []
    if not HAS_PANDAS:
        missing_deps.append("pandas")
    if not HAS_OPENPYXL:
        missing_deps.append("openpyxl")
    
    if missing_deps:
        print(f"Missing optional packages: {', '.join(missing_deps)}")
        print("Enable 'Auto-install missing packages' for Excel support")
        print()
    
    # Parse command line arguments for number of records
    num_records = 100  # Default
    if len(sys.argv) > 1:
        try:
            num_records = int(sys.argv[1])
            if num_records <= 0:
                raise ValueError("Number of records must be positive")
        except ValueError as e:
            print(f"Invalid argument: {e}")
            print("Usage: python data_export.py [num_records]")
            print("Example: python data_export.py 500")
            return
    
    print(f"Generating {num_records} sample records...")
    data = generate_sample_data(num_records)
    print(f"Sample data generated successfully!")
    
    # Display basic information
    print(f"Generated {len(data)} records with {len(data[0].keys())} fields each")
    print()
    
    generated_files = []
    
    try:
        # Create all export formats
        print("Creating CSV export...")
        csv_file = create_csv_file(data)
        generated_files.append(csv_file)
        
        print("Creating Excel export...")
        excel_file = create_excel_file(data)
        generated_files.append(excel_file)
        
        print("Creating XML export...")
        xml_file = create_xml_file(data)
        generated_files.append(xml_file)
        
        print("Creating JSON export...")
        json_file = create_json_export(data)
        generated_files.append(json_file)
        
        print("Creating TSV export...")
        tsv_file = create_tsv_file(data)
        generated_files.append(tsv_file)
        
        print("Creating summary report...")
        report_file = create_summary_report(data)
        generated_files.append(report_file)
        
        # Remove any None values (failed exports)
        generated_files = [f for f in generated_files if f is not None]
        
        # Summary
        print("\nDATA EXPORT COMPLETE!")
        print(f"Generated {len(generated_files)} files:")
        for file in generated_files:
            try:
                file_size = os.path.getsize(file)
                file_name = os.path.basename(file)
                print(f"   • {file_name} ({file_size} bytes)")
            except:
                print(f"   • {os.path.basename(file)}")
        
        print(f"\nData Summary:")
        print(f"   • Total records: {num_records}")
        print(f"   • File formats: {len(generated_files)}")
        print(f"   • Export types: CSV, Excel, XML, JSON, TSV, Report")
        print(f"   • Excel support: {'Yes' if HAS_PANDAS and HAS_OPENPYXL else 'No'}")
        
    except ValueError as e:
        print(f"Invalid argument: {e}")
        print("Make sure the number of records is a valid positive integer")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    exit(main()) 