""" Floor start state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from utils.resource_loader import ResourceLoader

class FloorStartState(GameState):
    """The floor starting screen where players begin a new floor."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        
        # UI elements
        self.panels = {}
        self.buttons = {}
        self.continue_button = None
    
    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = pygame.font.SysFont(None, 20)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load floor based on current floor type
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()
        
        # Use the floor image for the current floor type
        floor_image = f"floors/{current_floor_type}_floor.png"
            
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        # Create UI elements
        self.create_ui()
    
    def create_ui(self):
        """Create the UI elements for the floor start state."""
        # Main panel
        self.panels["main"] = Panel(
            (600, 300),
            (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150),
            colour=DARK_GRAY
        )
        
        # Continue button
        continue_rect = pygame.Rect(0, 0, 200, 50)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.bottom = self.panels["main"].rect.bottom - 30
        self.continue_button = Button(continue_rect, "Enter Floor", self.body_font)
    
    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            # Check button hover states
            self.continue_button.check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if continue button was clicked
            if self.continue_button.is_clicked(event.pos):
                self.game_manager.change_state("playing")
                return
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
        
        # Draw floor title
        floor_type = self.game_manager.floor_manager.get_current_floor()
        floor_index = max(1, self.game_manager.floor_manager.current_floor_index + 1)  # Make sure index is at least 1
        title_text = self.header_font.render(f"Floor {floor_index}: {floor_type.title()}", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 30)
        surface.blit(title_text, title_rect)
        
        # Add a welcome message
        welcome_text = self.body_font.render(f"Welcome to the {floor_type.title()}", True, WHITE)
        welcome_rect = welcome_text.get_rect(centerx=self.panels["main"].rect.centerx, top=title_rect.bottom + 30)
        surface.blit(welcome_text, welcome_rect)
        
        # Add instructions
        instruct_text = self.normal_font.render("Prepare yourself for the challenges ahead!", True, WHITE)
        instruct_rect = instruct_text.get_rect(centerx=self.panels["main"].rect.centerx, top=welcome_rect.bottom + 20)
        surface.blit(instruct_text, instruct_rect)
        
        # Draw continue button
        self.continue_button.draw(surface)