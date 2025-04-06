import os
import pygame
import numpy as np
from PIL import Image

def slice_and_recolor_weapons():
    """
    Extract and recolor weapons from sprite sheets using pygame
    """
    # Define paths
    weapons1_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons1.png"
    weapons2_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons2.jpg"
    output_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/individual"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize pygame and create a dummy display
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    # Define colors
    dark_color = (171, 82, 54)
    light_color = (214, 123, 86)
    
    # Function to process a weapon image
    def process_weapon(weapon_surface, index):
        # Create a surface with per-pixel alpha
        result = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Get the background color (assuming top-left pixel is background)
        bg_color = weapon_surface.get_at((0, 0))
        
        # Process each pixel
        for x in range(32):
            for y in range(32):
                try:
                    color = weapon_surface.get_at((x, y))
                    
                    # Skip if color is similar to background
                    color_distance = sum(abs(color[i] - bg_color[i]) for i in range(3))
                    if color_distance < 30:
                        continue
                    
                    # Determine if pixel is light or dark
                    brightness = (color[0] + color[1] + color[2]) / 3
                    
                    if brightness > 180:  # Light color
                        result.set_at((x, y), (*light_color, color[3]))
                    else:  # Dark color
                        result.set_at((x, y), (*dark_color, color[3]))
                        
                except IndexError:
                    pass
        
        # Save the processed weapon
        output_path = os.path.join(output_dir, f"weapon{index}.png")
        pygame.image.save(result, output_path)
        print(f"Saved: {output_path}")
    
    # Process weapons1.png (3x3 grid)
    weapons1 = pygame.image.load(weapons1_path).convert_alpha()
    for row in range(3):
        for col in range(3):
            index = row * 3 + col + 1
            weapon = pygame.Surface((32, 32), pygame.SRCALPHA)
            weapon.blit(weapons1, (0, 0), (col * 32, row * 32, 32, 32))
            process_weapon(weapon, index)
    
    # Process weapons2.jpg - Manual approach due to irregular positions
    weapons2 = pygame.image.load(weapons2_path).convert_alpha()
    
    # Define weapon positions in weapons2.jpg
    positions = [
        (12, 11),   # Weapon 10
        (60, 10),   # Weapon 11
        (114, 10),  # Weapon 12
        (12, 58),   # Weapon 13
        (60, 58),   # Weapon 14
        (114, 58),  # Weapon 15
        (12, 106),  # Weapon 16
        (60, 106),  # Weapon 17
        (114, 106)  # Weapon 18
    ]
    
    for i, (x, y) in enumerate(positions):
        index = i + 10
        weapon = pygame.Surface((32, 32), pygame.SRCALPHA)
        weapon.blit(weapons2, (0, 0), (x, y, 32, 32))
        process_weapon(weapon, index)
    
    # Clean up pygame
    pygame.quit()
    
    print("All weapons processed successfully!")

if __name__ == "__main__":
    slice_and_recolor_weapons()