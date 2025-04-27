"""UI Factory for creating UI elements in the Scoundrel game."""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
from constants import WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY
from ui.button import Button
from ui.panel import Panel


class UIFactory:
    """Creates and manages UI elements."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def create_run_button(self):
        """Create the run button with dungeon styling."""
        # Increase button size to be more prominent
        run_width = 80  # Wider button
        run_height = 40  # Taller button
        
        # Position below status UI and above room
        run_x = SCREEN_WIDTH // 2
        run_y = 150  # Below status UI, above room
        
        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)
        
        # Use the Pixel Times font with dungeon styling
        self.playing_state.run_button = Button(
            run_button_rect, 
            "RUN", 
            self.playing_state.body_font,
            text_colour=WHITE,  # White text for better visibility
            dungeon_style=True,  # Enable dungeon styling
            panel_colour=(70, 20, 20),  # Dark red for urgency
            border_colour=(120, 40, 40)  # Red border for danger/action
        )
