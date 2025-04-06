from PIL import Image
import os
import numpy as np

# Define color constants
DARK_RED = (171, 82, 54)  # CARD_RED from constants.py
WHITE = (255, 255, 255)
SLIGHTLY_LIGHTER_RED = (214, 123, 86)  # Lighter version of CARD_RED

def is_similar_to_black(color, threshold=60):
    """Check if a color is similar to black"""
    return sum(color[:3]) < threshold

def is_similar_to_white(color, threshold=620):
    """Check if a color is similar to white"""
    return sum(color[:3]) > threshold

def is_background(color, bg_color, threshold=30):
    """Check if a color is similar to the background color"""
    if len(color) > 3 and color[3] < 128:
        return True  # Already transparent
        
    # Calculate color distance
    r_diff = abs(color[0] - bg_color[0])
    g_diff = abs(color[1] - bg_color[1])
    b_diff = abs(color[2] - bg_color[2])
    
    return (r_diff + g_diff + b_diff) < threshold

def recolor_weapon(input_path, output_path):
    """Recolor a weapon image using the specified color scheme"""
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Identify the background color (assuming corners are background)
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((width-1, 0)),
        img.getpixel((0, height-1)),
        img.getpixel((width-1, height-1))
    ]
    
    # Find the most common corner color
    bg_color = max(corners, key=corners.count)
    
    # Create a new image with transparent background
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Process each pixel
    for y in range(height):
        for x in range(width):
            color = img.getpixel((x, y))
            
            # Skip background pixels
            if is_background(color, bg_color):
                continue
                
            # Determine the new color based on the original color
            if is_similar_to_black(color):
                # Replace black/dark colors with dark red (CARD_RED)
                new_color = DARK_RED
            elif is_similar_to_white(color):
                # Keep white/bright colors as white
                new_color = WHITE
            else:
                # Other colors become slightly lighter version of CARD_RED
                new_color = SLIGHTLY_LIGHTER_RED
            
            # Set the pixel in the new image (preserve original alpha)
            alpha = color[3] if len(color) > 3 else 255
            new_img.putpixel((x, y), (*new_color, alpha))
    
    # Save the recolored weapon
    new_img.save(output_path)
    print(f"Recolored: {output_path}")

def recolor_all_weapons():
    """Recolor all weapon images in the assets/weapons directory"""
    weapons_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons"
    output_dir = weapons_dir  # Save back to the same directory
    
    # Get all PNG files in the weapons directory
    weapon_files = [f for f in os.listdir(weapons_dir) 
                   if f.endswith('.png') and not f.startswith('.')]
    
    # Process each weapon
    for weapon_file in weapon_files:
        input_path = os.path.join(weapons_dir, weapon_file)
        output_path = os.path.join(output_dir, weapon_file)
        recolor_weapon(input_path, output_path)
    
    print(f"All {len(weapon_files)} weapons recolored successfully!")

if __name__ == "__main__":
    recolor_all_weapons()