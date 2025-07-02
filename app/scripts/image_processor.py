#!/usr/bin/env python3
"""
Image Processor Script - Creates and processes multiple image files
Generates various image formats: PNG images, charts, composite images, and metadata
"""

import os
import sys
import json
import random

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import numpy as np
    HAS_REQUIRED_PACKAGES = True
except ImportError as e:
    HAS_REQUIRED_PACKAGES = False
    print(f"Missing required package: {e}")
    print("Required packages: pillow, matplotlib, numpy")
    print("Enable 'Auto-install missing packages' option to install them automatically")
    sys.exit(1)

def create_basic_image(size=(400, 300), color="lightblue", filename="basic_image.png"):
    """Create a basic colored image with text."""
    # Create image
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Add text to image
    text = "Generated Image"
    # Get text size using textbbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill="black", font=font)
    
    # Add some decorative elements
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline="darkblue", width=3)
    draw.ellipse([50, 50, 150, 150], fill="yellow", outline="orange", width=2)
    
    # Save the image
    output_path = os.path.join(os.getcwd(), filename)
    img.save(output_path)
    
    print(f"Created basic image: {filename}")
    return output_path

def create_processed_image(base_image_path, filename="processed_image.png", enhancement="brightness"):
    """Create a processed version of an image."""
    # Open the base image
    img = Image.open(base_image_path)
    
    # Apply different enhancements
    if enhancement == "brightness":
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)  # Increase brightness
    elif enhancement == "contrast":
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)  # Increase contrast
    elif enhancement == "color":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.4)  # Increase color saturation
    elif enhancement == "sharpness":
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # Increase sharpness
    
    # Add a border
    border_size = 10
    border_color = "red"
    
    # Create new image with border
    new_size = (img.width + 2*border_size, img.height + 2*border_size)
    bordered_img = Image.new('RGB', new_size, border_color)
    bordered_img.paste(img, (border_size, border_size))
    
    # Add enhancement label
    draw = ImageDraw.Draw(bordered_img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((15, 15), f"Enhanced: {enhancement}", fill="white", font=font)
    
    # Save the processed image
    output_path = os.path.join(os.getcwd(), filename)
    bordered_img.save(output_path)
    
    print(f"Created processed image: {filename}")
    return output_path

def create_chart_image(chart_type="bar", filename="chart_image.png"):
    """Create a chart and save as image."""
    # Generate sample data
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [random.randint(10, 100) for _ in categories]
    
    plt.figure(figsize=(10, 6))
    
    if chart_type == "bar":
        plt.bar(categories, values, color=['red', 'green', 'blue', 'orange', 'purple'])
        plt.title('Sample Bar Chart', fontsize=16, fontweight='bold')
        plt.ylabel('Values')
    elif chart_type == "line":
        plt.plot(categories, values, marker='o', linewidth=3, markersize=8)
        plt.title('Sample Line Chart', fontsize=16, fontweight='bold')
        plt.ylabel('Values')
    elif chart_type == "pie":
        plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Sample Pie Chart', fontsize=16, fontweight='bold')
    elif chart_type == "scatter":
        x_vals = list(range(len(categories)))
        plt.scatter(x_vals, values, s=100, alpha=0.7, c=['red', 'green', 'blue', 'orange', 'purple'])
        plt.title('Sample Scatter Plot', fontsize=16, fontweight='bold')
        plt.xticks(x_vals, categories)
        plt.ylabel('Values')
    
    plt.xlabel('Categories')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the chart
    output_path = os.path.join(os.getcwd(), filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created chart: {filename}")
    return output_path

def create_composite_image(image_paths, filename="composite_image.png"):
    """Create a composite image from multiple source images."""
    if len(image_paths) < 2:
        print("Need at least 2 images for composite")
        return None
    
    # Open the first two images
    img1 = Image.open(image_paths[0])
    img2 = Image.open(image_paths[1])
    
    # Resize images to same size
    size = (400, 300)
    img1 = img1.resize(size)
    img2 = img2.resize(size)
    
    # Create composite with 50% transparency
    composite = Image.blend(img1, img2, alpha=0.5)
    
    # Add a title
    draw = ImageDraw.Draw(composite)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "Composite Image", fill="white", font=font)
    draw.text((10, 40), f"Blend of {len(image_paths)} images", fill="white", font=font)
    
    # Add timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, size[1] - 30), f"Generated: {timestamp}", fill="white", font=font)
    
    # Save composite image
    output_path = os.path.join(os.getcwd(), filename)
    composite.save(output_path)
    
    print(f"Created composite image: {filename}")
    return output_path

def create_metadata_file(image_files, filename="image_metadata.json"):
    """Create metadata file for generated images."""
    metadata = {
        "generation_info": {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_images": len(image_files),
            "generator": "Image Processor Script v1.0"
        },
        "images": {}
    }
    
    for img_file in image_files:
        try:
            img = Image.open(img_file)
            file_stats = os.stat(img_file)
            
            metadata["images"][os.path.basename(img_file)] = {
                "path": img_file,
                "size": {
                    "width": img.width,
                    "height": img.height
                },
                "mode": img.mode,
                "format": img.format,
                "file_size_bytes": file_stats.st_size,
                "created": datetime.fromtimestamp(file_stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Could not read metadata for {img_file}: {e}")
    
    # Save metadata
    metadata_file = os.path.join(os.getcwd(), filename)
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Created metadata file: {filename}")
    return metadata_file

def main():
    """Main image processing function."""
    print("IMAGE PROCESSOR SCRIPT")
    print("=" * 30)
    print("Creating multiple image files with different processing techniques")
    print()
    
    # Parse command line arguments
    size = (400, 300)  # Default size
    color = "lightblue"  # Default color
    enhancement = "brightness"  # Default enhancement
    chart_type = "bar"  # Default chart type
    
    # Simple argument parsing
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith('--size='):
            try:
                size_str = arg.split('=')[1]
                w, h = map(int, size_str.split('x'))
                size = (w, h)
            except:
                print(f"Invalid size format: {arg}")
        elif arg.startswith('--color='):
            color = arg.split('=')[1]
        elif arg.startswith('--enhancement='):
            enhancement = arg.split('=')[1]
        elif arg.startswith('--chart='):
            chart_type = arg.split('=')[1]
    
    print(f"Settings: size={size}, color={color}, enhancement={enhancement}, chart={chart_type}")
    print()
    
    generated_files = []
    
    try:
        # Step 1: Create basic image
        print("Creating basic image...")
        basic_img = create_basic_image(size, color, "basic_image.png")
        generated_files.append(basic_img)
        
        # Step 2: Create processed image
        print("Creating processed image...")
        processed_img = create_processed_image(basic_img, "processed_image.png", enhancement)
        generated_files.append(processed_img)
        
        # Step 3: Create chart
        print("Creating chart...")
        chart_img = create_chart_image(chart_type, "chart_image.png")
        generated_files.append(chart_img)
        
        # Step 4: Create composite image
        print("Creating composite image...")
        composite_img = create_composite_image([basic_img, processed_img], "composite_image.png")
        if composite_img:
            generated_files.append(composite_img)
        
        # Step 5: Create metadata
        print("Creating metadata...")
        metadata_file = create_metadata_file(generated_files, "image_metadata.json")
        generated_files.append(metadata_file)
        
        print("\nIMAGE PROCESSING COMPLETE!")
        print(f"Generated {len(generated_files)} files:")
        for i, file_path in enumerate(generated_files, 1):
            file_name = os.path.basename(file_path)
            print(f"   {i}. {file_name}")
        
        print(f"\nSummary:")
        print(f"   • Image size: {size[0]}x{size[1]}")
        print(f"   • Base color: {color}")
        print(f"   • Enhancement: {enhancement}")
        print(f"   • Chart type: {chart_type}")
        
    except Exception as e:
        print(f"Invalid argument: {e}")
        print("Usage: python image_processor.py [--size=WxH] [--color=COLOR] [--enhancement=TYPE] [--chart=TYPE]")
        print("Example: python image_processor.py --size=800x600 --color=lightgreen --enhancement=contrast --chart=pie")
        return
    
if __name__ == "__main__":
    if not HAS_REQUIRED_PACKAGES:
        sys.exit(1)
    
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 