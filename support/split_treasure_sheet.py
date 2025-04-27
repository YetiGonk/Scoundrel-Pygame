"""
Script to create sample treasure chest sprites in different colors,
and save each row as a separate PNG file.
"""
import pygame
import os
import sys
import random

# Initialise pygame
pygame.init()

# Constants
SPRITE_WIDTH = 48
SPRITE_HEIGHT = 40
FRAMES_PER_ROW = 21
NUM_ROWS = 10

# Create the spritesheet surface
spritesheet_width = SPRITE_WIDTH * FRAMES_PER_ROW
spritesheet_height = SPRITE_HEIGHT * NUM_ROWS
spritesheet = pygame.Surface((spritesheet_width, spritesheet_height), pygame.SRCALPHA)

# Color schemes for different rarities
color_schemes = [
    # Common - brown
    [(139, 69, 19), (160, 82, 45), (210, 105, 30)],
    # Uncommon - green
    [(0, 100, 0), (34, 139, 34), (50, 205, 50)],
    # Row 2 - blue
    [(0, 0, 139), (0, 0, 205), (30, 144, 255)],
    # Row 3 - purple
    [(75, 0, 130), (106, 90, 205), (147, 112, 219)],
    # Row 4 - orange
    [(178, 34, 34), (255, 140, 0), (255, 165, 0)],
    # Row 5 - red
    [(139, 0, 0), (205, 0, 0), (255, 0, 0)],
    # Row 6 - white/silver
    [(169, 169, 169), (192, 192, 192), (211, 211, 211)],
    # Row 7 - dark purple
    [(75, 0, 130), (138, 43, 226), (148, 0, 211)],
    # Row 8 - cyan
    [(0, 139, 139), (0, 206, 209), (64, 224, 208)],
    # Legendary - gold
    [(184, 134, 11), (218, 165, 32), (255, 215, 0)]
]

# Create a basic chest shape
def draw_basic_chest(surface, x, y, colors, frame_number, row_number):
    # Draw chest parts based on frame number (animation progression)
    
    # Determine if chest is closed, opening, or open based on frame
    if frame_number < 5:
        # Closed chest
        chest_state = "closed"
    elif frame_number < 13:
        # Opening animation
        chest_state = "opening"
    else:
        # Open with glow
        chest_state = "open"
    
    # Base color (dark)
    base_color = colors[0]
    # Mid color
    mid_color = colors[1]
    # Light color (highlights)
    light_color = colors[2]
    
    # Draw chest base (bottom part)
    chest_rect = pygame.Rect(x + 5, y + 20, 38, 16)
    pygame.draw.rect(surface, base_color, chest_rect, border_radius=2)
    
    # Draw chest lid
    if chest_state == "closed":
        # Closed lid
        lid_rect = pygame.Rect(x + 5, y + 8, 38, 14)
        pygame.draw.rect(surface, mid_color, lid_rect, border_radius=2)
        
        # Lid edge
        lid_edge = pygame.Rect(x + 5, y + 19, 38, 3)
        pygame.draw.rect(surface, light_color, lid_edge)
        
        # Lock
        lock_rect = pygame.Rect(x + 21, y + 13, 6, 8)
        pygame.draw.rect(surface, light_color, lock_rect)
    
    elif chest_state == "opening":
        # Lid in process of opening - calculate angle
        opening_progress = (frame_number - 5) / 8.0  # 0.0 to 1.0
        
        # Lid position moves up and back as it opens
        lid_y = y + 8 - (opening_progress * 6)
        lid_height = 14 + (opening_progress * 2)
        
        lid_rect = pygame.Rect(x + 5, lid_y, 38, lid_height)
        pygame.draw.rect(surface, mid_color, lid_rect, border_radius=2)
        
        # Lid edge moves with lid
        edge_y = lid_y + lid_height - 3
        lid_edge = pygame.Rect(x + 5, edge_y, 38, 3)
        pygame.draw.rect(surface, light_color, lid_edge)
        
        # Lock moves with lid
        lock_rect = pygame.Rect(x + 21, lid_y + 5, 6, 8)
        pygame.draw.rect(surface, light_color, lock_rect)
    
    else:  # open
        # Fully open lid
        lid_rect = pygame.Rect(x + 5, y + 2, 38, 14)
        pygame.draw.rect(surface, mid_color, lid_rect, border_radius=2)
        
        # Lid edge
        lid_edge = pygame.Rect(x + 5, y + 13, 38, 3)
        pygame.draw.rect(surface, light_color, lid_edge)
        
        # Lock
        lock_rect = pygame.Rect(x + 21, y + 7, 6, 8)
        pygame.draw.rect(surface, light_color, lock_rect)
        
        # Add treasure glow effect for open chest
        glow_progress = min(1.0, (frame_number - 13) / 8.0)  # 0.0 to 1.0
        
        # Draw treasure inside chest
        treasure_color = light_color
        
        # Create a smaller rect for the treasure
        treasure_rect = pygame.Rect(x + 12, y + 22, 24, 8)
        pygame.draw.rect(surface, treasure_color, treasure_rect)
        
        # Add glow around treasure based on rarity and animation progress
        if glow_progress > 0:
            # Glow size increases with frame number
            glow_size = int(glow_progress * 12)
            glow_alpha = int(glow_progress * 150)
            
            # Create a surface for the glow
            glow_surf = pygame.Surface((chest_rect.width + glow_size*2, 
                                       chest_rect.height + glow_size*2), pygame.SRCALPHA)
            
            # Glow color based on chest rarity (row)
            # Add increasing glow alpha as animation progresses
            glow_color = (*light_color, glow_alpha)
            
            # Draw circular glow
            pygame.draw.ellipse(glow_surf, glow_color, 
                              (0, 0, 
                               chest_rect.width + glow_size*2, 
                               chest_rect.height + glow_size*2))
            
            # Position glow behind chest
            glow_pos = (chest_rect.x - glow_size, chest_rect.y - glow_size)
            surface.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ALPHA_SDL2)

# Generate the spritesheet
for row in range(NUM_ROWS):
    colors = color_schemes[row]
    for frame in range(FRAMES_PER_ROW):
        x = frame * SPRITE_WIDTH
        y = row * SPRITE_HEIGHT
        
        # Draw chest with appropriate colors and animation frame
        draw_basic_chest(spritesheet, x, y, colors, frame, row)

# Save the complete spritesheet
pygame.image.save(spritesheet, "assets/ui/treasure_spritesheet.png")

# Create directory if it doesn't exist
os.makedirs("assets/ui/treasure_sprites", exist_ok=True)

# Extract each row as a separate image
for row in range(NUM_ROWS):
    # Create a surface for this row
    row_surface = pygame.Surface((SPRITE_WIDTH * FRAMES_PER_ROW, SPRITE_HEIGHT), pygame.SRCALPHA)
    
    # Extract the row from the spritesheet
    row_surface.blit(spritesheet, (0, 0), 
                    (0, row * SPRITE_HEIGHT, SPRITE_WIDTH * FRAMES_PER_ROW, SPRITE_HEIGHT))
    
    # Save this row
    row_filename = f"assets/ui/treasure_sprites/treasure_row_{row}.png"
    pygame.image.save(row_surface, row_filename)
    print(f"Saved {row_filename}")

pygame.quit()
print("Spritesheet and individual rows created successfully!")