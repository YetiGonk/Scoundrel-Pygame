"""
    Scoundrel - The 52-Card Roguelike Dungeon Crawler

    A roguelike card game where you navigate through multiple floors of monsters, 
    weapons, and potions.
"""
import sys
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from states.game_manager import GameManager

def main():
    """ Main entry point for the game. """
    
    # Initialize pygame
    pygame.init()
    
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scoundrel - The 52-Card Roguelike Dungeon Crawler")
    clock = pygame.time.Clock()
    
    # Create the game manager
    game_manager = GameManager()
    
    # Main game loop
    running = True
    while running:
        # Calculate delta time
        delta_time = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
        
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # Pass the event to the current state
                game_manager.handle_event(event)
        
        # Update
        game_manager.update(delta_time)
        
        # Draw
        game_manager.draw(screen)
        
        # Flip the display
        pygame.display.flip()
    
    # Quit the game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()