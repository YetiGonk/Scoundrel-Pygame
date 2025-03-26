"""
    Scoundrel - The 52-Card Roguelike Dungeon Crawler

    A roguelike card game where you navigate through multiple floors of monsters, 
    weapons, and potions with items and spells to aid your journey.
"""
import sys
import os
import json
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from states.game_manager import GameManager
from floor_manager import FloorManager
from item_manager import ItemManager
from spell_manager import SpellManager

def load_game_data():
    """Load item and spell data from JSON files."""
    items_data = []
    spells_data = []
    
    try:
        # Try to load items data
        if os.path.exists("data/items.json"):
            with open("data/items.json", "r") as f:
                items_data = json.load(f)
    except Exception as e:
        print(f"Error loading items data: {e}")
        # Use empty items list
        items_data = []
    
    try:
        # Try to load spells data
        if os.path.exists("data/spells.json"):
            with open("data/spells.json", "r") as f:
                spells_data = json.load(f)
    except Exception as e:
        print(f"Error loading spells data: {e}")
        # Use empty spells list
        spells_data = []
    
    return items_data, spells_data

def main():
    """ Main entry point for the game. """
    
    # Initialize pygame
    pygame.init()
    
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scoundrel - The 52-Card Roguelike Dungeon Crawler")
    clock = pygame.time.Clock()
    
    # Load game data
    items_data, spells_data = load_game_data()
    
    # Create the game manager
    game_manager = GameManager()
    
    # Load items and spells
    game_manager.item_manager.load_items(items_data)
    game_manager.spell_manager.load_spells(spells_data)
    
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