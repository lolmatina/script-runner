#!/usr/bin/env python3
"""
Data Analyzer Script - Creates sample sales data and performs analysis
Generates multiple output files: charts, data files, and reports
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import numpy as np
    HAS_REQUIRED_PACKAGES = True
except ImportError as e:
    HAS_REQUIRED_PACKAGES = False
    missing_package = str(e)

def generate_sample_data(days=30):
    """Generate sample sales data for analysis."""
    base_date = datetime.now() - timedelta(days=days)
    data = []
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        # Generate realistic sales data with trends and seasonality
        base_sales = 1000 + (i * 10)  # Growth trend
        weekend_factor = 0.7 if date.weekday() >= 5 else 1.0  # Lower weekend sales
        seasonal_factor = 1.0 + 0.3 * (i / days)  # Seasonal growth
        noise = random.uniform(0.8, 1.2)  # Random variation
        
        sales = base_sales * weekend_factor * seasonal_factor * noise
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),
            'sales': round(sales, 2),
            'customers': random.randint(50, 150),
            'avg_order_value': round(sales / random.randint(50, 150), 2)
        })
    
    return pd.DataFrame(data)

def create_sales_chart(df, output_path="sales_analysis_chart.png"):
    """Create a sales analysis chart."""
    plt.figure(figsize=(12, 8))
    
    # Convert date strings to datetime for plotting
    dates = pd.to_datetime(df['date'])
    
    # Create subplot for sales trend
    plt.subplot(2, 2, 1)
    plt.plot(dates, df['sales'], marker='o', linewidth=2, markersize=4)
    plt.title('Daily Sales Trend', fontsize=12, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Sales ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Create subplot for customers vs sales
    plt.subplot(2, 2, 2)
    plt.scatter(df['customers'], df['sales'], alpha=0.6, color='green')
    plt.title('Customers vs Sales', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Customers')
    plt.ylabel('Sales ($)')
    plt.grid(True, alpha=0.3)
    
    # Create subplot for average order value
    plt.subplot(2, 2, 3)
    plt.bar(range(len(df)), df['avg_order_value'], alpha=0.7, color='orange')
    plt.title('Average Order Value by Day', fontsize=12, fontweight='bold')
    plt.xlabel('Day')
    plt.ylabel('Avg Order Value ($)')
    plt.grid(True, alpha=0.3)
    
    # Create subplot for day of week analysis
    plt.subplot(2, 2, 4)
    dow_sales = df.groupby('day_of_week')['sales'].mean()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_sales = dow_sales.reindex(dow_order, fill_value=0)
    plt.bar(dow_sales.index, dow_sales.values, alpha=0.7, color='purple')
    plt.title('Average Sales by Day of Week', fontsize=12, fontweight='bold')
    plt.xlabel('Day of Week')
    plt.ylabel('Average Sales ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the chart
    chart_filename = os.path.join(os.getcwd(), output_path)
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Sales chart saved to: {chart_filename}")
    return chart_filename

def create_weekly_chart(df, output_path="weekly_sales_chart.png"):
    """Create a weekly sales summary chart."""
    # Add week number
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    
    # Group by week
    weekly_data = df.groupby('week').agg({
        'sales': ['sum', 'mean', 'count'],
        'customers': 'sum',
        'avg_order_value': 'mean'
    }).round(2)
    
    plt.figure(figsize=(10, 6))
    
    weeks = weekly_data.index
    weekly_sales = weekly_data[('sales', 'sum')]
    
    plt.bar(weeks, weekly_sales, alpha=0.7, color='steelblue')
    plt.title('Weekly Sales Summary', fontsize=14, fontweight='bold')
    plt.xlabel('Week Number')
    plt.ylabel('Total Sales ($)')
    plt.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for week, sales in zip(weeks, weekly_sales):
        plt.text(week, sales + max(weekly_sales) * 0.01, f'${sales:,.0f}', 
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    weekly_chart_filename = os.path.join(os.getcwd(), output_path)
    plt.savefig(weekly_chart_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Weekly chart saved to: {weekly_chart_filename}")
    return weekly_chart_filename

def save_data_files(df):
    """Save data in multiple formats."""
    # Save as CSV
    csv_filename = os.path.join(os.getcwd(), "sales_data.csv")
    df.to_csv(csv_filename, index=False)
    print(f"Raw data saved to: {csv_filename}")
    
    return csv_filename

def create_summary_statistics(df):
    """Create and save summary statistics."""
    stats = {
        'total_sales': float(df['sales'].sum()),
        'avg_sales': float(df['sales'].mean()),
        'median_sales': float(df['sales'].median()),
        'std_sales': float(df['sales'].std()),
        'min_sales': float(df['sales'].min()),
        'max_sales': float(df['sales'].max()),
        'total_customers': int(df['customers'].sum()),
        'avg_customers': float(df['customers'].mean()),
        'avg_order_value': float(df['avg_order_value'].mean()),
        'total_days': len(df),
        'best_day': df.loc[df['sales'].idxmax(), 'date'],
        'worst_day': df.loc[df['sales'].idxmin(), 'date'],
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save summary as JSON
    json_filename = os.path.join(os.getcwd(), "sales_summary.json")
    with open(json_filename, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Summary statistics saved to: {json_filename}")
    return json_filename, stats

def create_detailed_report(df, stats):
    """Create a detailed text report."""
    report_filename = os.path.join(os.getcwd(), "sales_report.txt")
    
    with open(report_filename, 'w') as f:
        f.write("SALES ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Analysis Date: {stats['analysis_date']}\n")
        f.write(f"Data Period: {df['date'].min()} to {df['date'].max()}\n")
        f.write(f"Total Days Analyzed: {stats['total_days']}\n\n")
        
        f.write("SALES SUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Sales: ${stats['total_sales']:,.2f}\n")
        f.write(f"Average Daily Sales: ${stats['avg_sales']:,.2f}\n")
        f.write(f"Median Daily Sales: ${stats['median_sales']:,.2f}\n")
        f.write(f"Sales Standard Deviation: ${stats['std_sales']:,.2f}\n")
        f.write(f"Minimum Daily Sales: ${stats['min_sales']:,.2f} ({stats['worst_day']})\n")
        f.write(f"Maximum Daily Sales: ${stats['max_sales']:,.2f} ({stats['best_day']})\n\n")
        
        f.write("CUSTOMER METRICS:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Customers: {stats['total_customers']:,}\n")
        f.write(f"Average Daily Customers: {stats['avg_customers']:.1f}\n")
        f.write(f"Average Order Value: ${stats['avg_order_value']:.2f}\n\n")
        
        f.write("DAY OF WEEK ANALYSIS:\n")
        f.write("-" * 25 + "\n")
        dow_analysis = df.groupby('day_of_week')['sales'].agg(['mean', 'sum', 'count']).round(2)
        for day, row in dow_analysis.iterrows():
            f.write(f"{day}: Avg ${row['mean']:,.2f}, Total ${row['sum']:,.2f}, Days {row['count']}\n")
    
    print(f"Detailed report saved to: {report_filename}")
    return report_filename

def main():
    """Main analysis function."""
    print("SALES DATA ANALYSIS")
    print("=" * 30)
    
    # Parse command line arguments
    days = 30  # Default
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
            if days <= 0:
                raise ValueError("Days must be positive")
        except ValueError as e:
            print(f"Invalid days argument: {e}")
            return
    
    print(f"Generating {days} days of sample sales data...")
    
    # Generate sample data
    df = generate_sample_data(days)
    print("Data generated successfully!")
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Display basic statistics
    print(f"Total sales: ${df['sales'].sum():,.2f}")
    print(f"Average daily sales: ${df['sales'].mean():,.2f}")
    print()
    
    # Create visualizations
    chart_files = []
    chart_files.append(create_sales_chart(df))
    chart_files.append(create_weekly_chart(df))
    
    # Save data files
    data_files = []
    data_files.append(save_data_files(df))
    
    # Create summary statistics
    json_file, stats = create_summary_statistics(df)
    data_files.append(json_file)
    
    # Create detailed report
    report_file = create_detailed_report(df, stats)
    data_files.append(report_file)
    
    # List all generated files
    all_files = chart_files + data_files
    print(f"\nGenerated {len(all_files)} output files:")
    for i, file_path in enumerate(all_files, 1):
        file_name = os.path.basename(file_path)
        print(f"   {i}. {file_name}")
    
    print("\nAnalysis completed successfully!")
    print(f"Key insight: Average daily sales = ${stats['avg_sales']:,.2f}")
    print(f"Files generated: {len(chart_files)} charts, {len(data_files)} data files")

if __name__ == "__main__":
    try:
        if not HAS_REQUIRED_PACKAGES:
            print(f"Missing required package: {missing_package}")
            print("Required packages: pandas, matplotlib, numpy")
            print("Enable 'Auto-install missing packages' option to install them automatically")
        else:
            main()
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1) 