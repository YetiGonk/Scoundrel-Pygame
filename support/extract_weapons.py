from PIL import Image
import os
import numpy as np

def extract_weapons():
    # Create output directory
    output_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/individual"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define color parameters
    dark_color = (171, 82, 54)
    light_color = (214, 123, 86)
    
    # Function to process a weapon
    def process_weapon(source_img, x, y, width, height, index):
        # Crop the weapon from source
        weapon = source_img.crop((x, y, x + width, y + height))
        
        # Create new image with transparent background
        new_weapon = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Get pixel data from weapon
        for py in range(height):
            for px in range(width):
                # Get original pixel
                pixel = weapon.getpixel((px, py))
                
                # Skip processing background pixels (brownish color)
                # Weapons1.png background
                if (120 < pixel[0] < 160 and 
                    100 < pixel[1] < 140 and 
                    70 < pixel[2] < 110):
                    continue
                
                # Weapons2.jpg background (slightly different due to jpg compression)
                if (130 < pixel[0] < 170 and 
                    110 < pixel[1] < 150 and 
                    80 < pixel[2] < 120):
                    continue
                
                # Skip fully transparent pixels if they exist
                if len(pixel) == 4 and pixel[3] == 0:
                    continue
                
                # Determine if pixel is light or dark
                brightness = sum(pixel[:3]) / 3
                
                if brightness > 180:  # Lighter parts (gold/yellow)
                    new_color = light_color
                else:  # Darker parts (brown/black)
                    new_color = dark_color
                
                # Set alpha to match original or full opacity
                alpha = pixel[3] if len(pixel) == 4 else 255
                
                # Set the pixel in the new image
                new_weapon.putpixel((px, py), (*new_color, alpha))
        
        # Save the weapon
        output_path = os.path.join(output_dir, f"weapon{index}.png")
        new_weapon.save(output_path)
        print(f"Saved: {output_path}")
    
    # Process weapons1.png (3x3 grid of 32x32 weapons)
    weapons1_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons1.png"
    weapons1 = Image.open(weapons1_path).convert("RGBA")
    
    # Process each weapon in the grid
    for row in range(3):
        for col in range(3):
            index = row * 3 + col + 1
            process_weapon(weapons1, col * 32, row * 32, 32, 32, index)
    
    # Process weapons2.jpg - manual approach
    weapons2_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons2.jpg"
    weapons2 = Image.open(weapons2_path).convert("RGBA")
    
    # Define weapon positions and sizes in weapons2.jpg
    # Format: (x, y, width, height)
    weapon_positions = [
        (12, 11, 32, 32),    # Weapon 10
        (60, 10, 32, 32),    # Weapon 11
        (114, 10, 32, 32),   # Weapon 12
        (12, 58, 32, 32),    # Weapon 13
        (60, 58, 32, 32),    # Weapon 14
        (114, 58, 32, 32),   # Weapon 15
        (12, 106, 32, 32),   # Weapon 16
        (60, 106, 32, 32),   # Weapon 17
        (114, 106, 32, 32)   # Weapon 18
    ]
    
    # Process each weapon
    for i, (x, y, w, h) in enumerate(weapon_positions):
        index = i + 10
        process_weapon(weapons2, x, y, w, h, index)
    
    print("All weapons processed successfully!")

if __name__ == "__main__":
    extract_weapons()