#!/usr/bin/env python3
"""
Mixed Output Script - Demonstrates both text and file outputs
Creates multiple files while displaying detailed console information
"""

import os
import sys
import random
import json
import csv
import statistics
import time
from datetime import datetime

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def generate_test_data(points=50):
    """Generate sample test data for demonstration."""
    x_data = list(range(1, points + 1))
    y_data = [random.uniform(10, 100) + i * 0.5 + random.uniform(-10, 10) for i in x_data]
    return x_data, y_data

def create_visualization(x_data, y_data):
    """Create a visualization and save it as a file."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available, skipping chart creation")
        return None
    
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(x_data, y_data, marker='o', linewidth=2, markersize=4, color='#2E86AB')
        plt.title('Sample Data Visualization', fontsize=16, fontweight='bold')
        plt.xlabel('X Values')
        plt.ylabel('Y Values')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = "mixed_output_chart.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Chart saved: {filename}")
        return filename
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None

def main():
    """Main function that produces both text output and files."""
    print("MIXED OUTPUT DEMONSTRATION")
    print("=" * 50)
    print("This script demonstrates producing both text output AND files")
    print()
    
    # Get current working directory for output
    output_dir = os.getcwd()
    print(f"Output directory: {output_dir}")
    print()
    
    # Configuration display
    print(f"Configuration:")
    print(f"   • Python version: {sys.version.split()[0]}")
    print(f"   • Matplotlib available: {'Yes' if HAS_MATPLOTLIB else 'No'}")
    print(f"   • Working directory: {output_dir}")
    print()
    
    try:
        # Parse arguments
        num_points = 50
        if len(sys.argv) > 1:
            num_points = int(sys.argv[1])
            if num_points <= 0 or num_points > 1000:
                raise ValueError("Points must be between 1 and 1000")
        
        print(f"Settings:")
        print(f"   • Data points: {num_points}")
        print(f"   • Matplotlib available: {'Yes' if HAS_MATPLOTLIB else 'No'}")
        print(f"   • Working directory: {output_dir}")
        print()
        
        # Step 1: Generate data
        print("Step 1: Generating test data...")
        x_data, y_data = generate_test_data(num_points)
        print(f"Generated {len(x_data)} data points")
        print(f"   • X range: {min(x_data)} to {max(x_data)}")
        print(f"   • Y range: {min(y_data):.1f} to {max(y_data):.1f}")
        print()
        
        # Display some sample data in console
        print("Sample data (first 10 points):")
        for i in range(min(10, len(x_data))):
            print(f"   Point {i+1}: x={x_data[i]}, y={y_data[i]:.2f}")
        print()
        
        generated_files = []
        
        # Step 2: Create visualization
        print("Step 2: Creating visualization...")
        chart_file = create_visualization(x_data, y_data)
        if chart_file:
            generated_files.append(chart_file)
            print(f"Visualization complete")
        else:
            print("Visualization skipped (matplotlib not available)")
        print()
        
        # Step 3: Save raw data
        print("Step 3: Saving raw data...")
        data_file = "raw_data.json"
        data_export = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_points": len(x_data),
                "script": "mixed_output.py"
            },
            "statistics": {
                "x_min": min(x_data),
                "x_max": max(x_data),
                "y_min": min(y_data),
                "y_max": max(y_data),
                "y_avg": sum(y_data) / len(y_data),
                "y_sum": sum(y_data)
            },
            "data": {
                "x_values": x_data,
                "y_values": y_data
            }
        }
        
        with open(data_file, 'w') as f:
            json.dump(data_export, f, indent=2)
        
        generated_files.append(data_file)
        print(f"Data saved to: {data_file}")
        print()
        
        # Step 4: Create analysis report
        print("Step 4: Creating analysis report...")
        report_file = "analysis_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("MIXED OUTPUT ANALYSIS REPORT\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Points: {len(x_data)}\n\n")
            
            f.write("STATISTICAL SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Y-Values Average: {sum(y_data)/len(y_data):.2f}\n")
            f.write(f"Y-Values Sum: {sum(y_data):.2f}\n")
            f.write(f"Y-Values Min: {min(y_data):.2f}\n")
            f.write(f"Y-Values Max: {max(y_data):.2f}\n")
            f.write(f"Y-Values Range: {max(y_data) - min(y_data):.2f}\n\n")
            
            f.write("DATA SAMPLE (first 10 points):\n")
            f.write("-" * 30 + "\n")
            for i in range(min(10, len(x_data))):
                f.write(f"Point {i+1}: X={x_data[i]}, Y={y_data[i]:.2f}\n")
            
            if len(x_data) > 10:
                f.write(f"... and {len(x_data) - 10} more points\n")
            
            f.write("\n" + "=" * 40 + "\n")
            f.write("End of Report\n")
        
        generated_files.append(report_file)
        print(f"Report saved to: {report_file}")
        print()
        
        # Step 5: Create CSV data
        print("Step 5: Creating CSV export...")
        csv_file = "data_export.csv"
        
        with open(csv_file, 'w') as f:
            f.write("x_value,y_value\n")
            for x, y in zip(x_data, y_data):
                f.write(f"{x},{y:.2f}\n")
        
        generated_files.append(csv_file)
        print(f"CSV exported to: {csv_file}")
        print()
        
        # Final analysis and summary
        print("Step 6: Performing final analysis...")
        
        # Calculate some interesting statistics
        increasing_count = sum(1 for i in range(1, len(y_data)) if y_data[i] > y_data[i-1])
        decreasing_count = sum(1 for i in range(1, len(y_data)) if y_data[i] < y_data[i-1])
        
        print(f"Trend Analysis:")
        print(f"   • Increasing points: {increasing_count} ({increasing_count/(len(y_data)-1)*100:.1f}%)")
        print(f"   • Decreasing points: {decreasing_count} ({decreasing_count/(len(y_data)-1)*100:.1f}%)")
        
        # Quartile analysis
        sorted_y = sorted(y_data)
        q1 = sorted_y[len(sorted_y)//4]
        q2 = sorted_y[len(sorted_y)//2]  # median
        q3 = sorted_y[3*len(sorted_y)//4]
        
        print(f"Quartile Analysis:")
        print(f"   • Q1 (25th percentile): {q1:.2f}")
        print(f"   • Q2 (50th percentile): {q2:.2f}")
        print(f"   • Q3 (75th percentile): {q3:.2f}")
        print()
        
        # File size analysis
        print("Generated Files Analysis:")
        total_size = 0
        for file in generated_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                total_size += size
                print(f"   • {file}: {size:,} bytes")
            else:
                print(f"   • {file}: File not found")
        
        print(f"   • Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print()
        
        # Performance metrics
        print("Performance Metrics:")
        print(f"   • Data generation: Instant")
        print(f"   • File creation: {len(generated_files)} files")
        print(f"   • Chart generation: {'Success' if HAS_MATPLOTLIB else 'Skipped'}")
        print(f"   • Memory usage: ~{len(x_data) * 8 * 2} bytes for data")
        print()
        
        # Final summary
        print("MIXED OUTPUT COMPLETE!")
        print("=" * 50)
        print("TEXT OUTPUT SUMMARY:")
        print(f"   • Console lines printed: ~50+ lines")
        print(f"   • Statistics calculated: 10+ metrics")
        print(f"   • Analysis performed: Trend and quartile analysis")
        print()
        print("FILE OUTPUT SUMMARY:")
        print(f"   • Total files created: {len(generated_files)}")
        print(f"   • File types: PNG, JSON, TXT, CSV")
        print(f"   • Total file size: {total_size:,} bytes")
        
        for file in generated_files:
            print(f"   • {file}")
        
        print()
        print("This demonstrates how scripts can provide rich console output")
        print("while simultaneously generating useful files for download!")
        
        return 0
        
    except ValueError as e:
        print(f"Invalid argument: {e}")
        print("Usage: python mixed_output.py [number_of_points]")
        print("Example: python mixed_output.py 100")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 