"""
Test script for the TreasureChest class.
"""
import pygame
import sys
import time
import os

# Add the project root to path to allow importing utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.treasure_chest import TreasureChest

# Initialise pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Treasure Chest Effect Test")

# Create background
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
# Create a dark gradient background
for y in range(SCREEN_HEIGHT):
    # Gradient from dark blue to darker blue
    color = (10, 10, max(5, 40 - y // 10))
    pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))

# Create 10 treasure chests in a grid (one of each rarity)
chests = []
for i in range(10):
    x = 150 + (i % 5) * 200
    y = 150 + (i // 5) * 220
    
    # Create chest with specific rarity (1-10)
    chest = TreasureChest((x, y), scale=2)
    chest.rarity = i + 1  # Set rarity manually (1-10)
    
    # Reload sprite and extract frames for this rarity
    chest.load_treasure_sprite()
    chest.extract_frames()
    
    chests.append(chest)

# Main loop
clock = pygame.time.Clock()
running = True
start_time = time.time()

# Controls help text
controls = [
    "Controls:",
    "ESC: Quit",
    "R: Reset animations",
    "SPACE: Pause/Resume",
    "1-0: Jump to frame",
    "Up/Down: Adjust animation speed"
]

# Animation state
paused = False
frame_duration = 0.1  # Default frame duration

# Font for text
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 36)

# Particle count for info display
total_particles = 0

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Reset all animations
                for chest in chests:
                    chest.current_frame = 0
                    chest.animation_complete = False
                    chest.particles = []
            elif event.key == pygame.K_SPACE:
                # Toggle pause
                paused = not paused
            elif event.key == pygame.K_UP:
                # Increase animation speed
                frame_duration = max(0.02, frame_duration - 0.02)
                for chest in chests:
                    chest.frame_duration = frame_duration
            elif event.key == pygame.K_DOWN:
                # Decrease animation speed
                frame_duration = min(0.3, frame_duration + 0.02)
                for chest in chests:
                    chest.frame_duration = frame_duration
            # Number keys 1-0 to jump to specific frames
            elif event.key in range(pygame.K_1, pygame.K_0 + 1):
                frame = event.key - pygame.K_1  # 0-9
                if event.key == pygame.K_0:  # Handle 0 key special case
                    frame = 9
                # Map 0-9 to frames 1-21
                target_frame = int(frame * 2.3)  # Spread across 21 frames
                for chest in chests:
                    chest.current_frame = target_frame
                    chest.animation_complete = False
    
    # Clear screen
    screen.blit(background, (0, 0))
    
    # Update and draw chests
    if not paused:
        elapsed_time = clock.tick(60) / 1000.0  # Delta time in seconds
        total_particles = 0
        for chest in chests:
            chest.update(elapsed_time)
            total_particles += len(chest.particles)
    else:
        clock.tick(60)  # Still maintain frame rate when paused
    
    # Draw all chests
    for chest in chests:
        chest.draw(screen)
    
    # Draw rarity labels
    for i, chest in enumerate(chests):
        x = 150 + (i % 5) * 200
        y = 150 + (i // 5) * 220
        
        # Label text
        if chest.rarity == 1:
            rarity_text = "Common (1)"
        elif chest.rarity == 2:
            rarity_text = "Uncommon (2)"
        elif chest.rarity in (9, 10):
            rarity_text = f"Legendary ({chest.rarity})"
        else:
            rarity_text = f"Rarity {chest.rarity}"
            
        # Show rarity and frame
        label = font.render(rarity_text, True, (220, 220, 220))
        frame_info = font.render(f"Frame: {chest.current_frame+1}", True, (180, 180, 180))
        
        # Draw with drop shadow
        shadow_color = (0, 0, 0)
        shadow_offset = 1
        
        # Draw shadow
        shadow_label = font.render(rarity_text, True, shadow_color)
        shadow_frame = font.render(f"Frame: {chest.current_frame+1}", True, shadow_color)
        
        # Draw labels
        label_rect = label.get_rect(center=(x, y - 55))
        frame_rect = frame_info.get_rect(center=(x, y - 35))
        
        # Draw shadows
        screen.blit(shadow_label, (label_rect.x + shadow_offset, label_rect.y + shadow_offset))
        screen.blit(shadow_frame, (frame_rect.x + shadow_offset, frame_rect.y + shadow_offset))
        
        # Draw text
        screen.blit(label, label_rect)
        screen.blit(frame_info, frame_rect)
    
    # Draw title
    title = title_font.render("Treasure Chest Animations", True, (255, 255, 255))
    title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, top=20)
    screen.blit(title, title_rect)
    
    # Draw controls help
    for i, text in enumerate(controls):
        text_surf = font.render(text, True, (200, 200, 200))
        screen.blit(text_surf, (20, 20 + i * 25))
    
    # Show animation speed
    speed_text = font.render(f"Frame Duration: {frame_duration:.2f}s", True, (200, 200, 200))
    screen.blit(speed_text, (20, 170))
    
    # Show particle count
    particles_text = font.render(f"Total Particles: {total_particles}", True, (200, 200, 200))
    screen.blit(particles_text, (20, 190))
    
    # Show pause status
    if paused:
        pause_text = title_font.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, (SCREEN_WIDTH - 150, 20))
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()