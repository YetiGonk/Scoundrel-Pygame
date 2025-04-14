#!/usr/bin/env python3
"""
Crop PNG images around their center to a specified width and height.
This script can process individual files or entire directories.
"""

import os
from glob import glob
from PIL import Image

def crop_center(img_path, output_path, target_width, target_height):
    """
        Crop an image to the specified dimensions, centered on the original image.
    """

    # Open the image
    img = Image.open(img_path)
    width, height = img.size
    
    # Calculate the cropping box (left, upper, right, lower)
    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    # Ensure we don't try to crop outside the image bounds
    if left < 0 or top < 0 or right > width or bottom > height:
        print(f"WARNING: Image {img_path} is smaller than the target dimensions!")
        # Adjust crop dimensions to stay within bounds
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)
    
    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save the cropped image
    cropped_img.save(output_path)
    print(f"Cropped {img_path} to {output_path}")

if __name__ == '__main__':
    pngs_dir = "assets/spells/*"
    pngs_list = glob(pngs_dir)
    target_width = 300
    target_height = 240
    output_dir = "assets/spells/cropped"
    for img_path in pngs_list:
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        crop_center(img_path, output_path, target_width, target_height)