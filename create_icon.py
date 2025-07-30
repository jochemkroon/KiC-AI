#!/usr/bin/env python3
"""
Simple script to create a robot icon for KIC-AI plugin
Creates a basic robot icon using PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create 24x24 icon (standard KiCad toolbar size)
    size = (24, 24)
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Robot colors
    robot_color = (70, 130, 180)  # Steel blue
    eye_color = (255, 255, 255)   # White
    antenna_color = (200, 200, 200)  # Light gray
    
    # Draw robot head (rectangle)
    head_rect = [4, 6, 20, 18]
    draw.rectangle(head_rect, fill=robot_color, outline=(50, 50, 50))
    
    # Draw antennae
    draw.line([8, 6, 8, 3], fill=antenna_color, width=1)
    draw.line([16, 6, 16, 3], fill=antenna_color, width=1)
    draw.ellipse([7, 2, 9, 4], fill=antenna_color)
    draw.ellipse([15, 2, 17, 4], fill=antenna_color)
    
    # Draw eyes
    draw.ellipse([7, 9, 10, 12], fill=eye_color)
    draw.ellipse([14, 9, 17, 12], fill=eye_color)
    
    # Draw pupils
    draw.ellipse([8, 10, 9, 11], fill=(0, 0, 0))
    draw.ellipse([15, 10, 16, 11], fill=(0, 0, 0))
    
    # Draw mouth
    draw.rectangle([10, 14, 14, 15], fill=(50, 50, 50))
    
    # Draw body
    body_rect = [6, 18, 18, 24]
    draw.rectangle(body_rect, fill=robot_color, outline=(50, 50, 50))
    
    # Save icon
    icon_path = os.path.join(os.path.dirname(__file__), 'plugins', 'robot_icon.png')
    img.save(icon_path, 'PNG')
    print(f"Robot icon created: {icon_path}")
    
except ImportError:
    print("PIL/Pillow not available - using default KiCad icon instead")
except Exception as e:
    print(f"Error creating icon: {e}")
