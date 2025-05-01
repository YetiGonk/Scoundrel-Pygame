"""
Status UI component for displaying game progression information
"""
import pygame
from constants import WHITE, BLACK, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT, \
    FLOOR_ROOM_TITLE_POSITION, FLOOR_ROOM_TITLE_WIDTH, FLOOR_ROOM_TITLE_HEIGHT

class StatusUI:
    """Displays current floor, room, and player stats during gameplay."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.header_font = pygame.font.SysFont(None, 28)
        self.normal_font = pygame.font.SysFont(None, 20)
        
        self.panel_rect = pygame.Rect(
            FLOOR_ROOM_TITLE_POSITION,
            (FLOOR_ROOM_TITLE_WIDTH, FLOOR_ROOM_TITLE_HEIGHT)
        )
    
    def update_fonts(self, header_font, normal_font):
        """Update fonts if they are loaded after initialization."""
        self.header_font = header_font
        self.normal_font = normal_font
    
    def draw(self, surface):
        """Draw the status UI with a dungeon-themed panel."""
        # Get current game state info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()  # Now safely returns "unknown" if needed
        current_floor_index = max(1, floor_manager.current_floor_index + 1)  # Ensure index is at least 1
        
        # Use the floor manager's current_room which is now 1-based
        current_room = floor_manager.current_room
            
        total_rooms = floor_manager.FLOOR_STRUCTURE["rooms_per_floor"]
        
        # Create dungeon-themed status panel if it doesn't exist yet
        if not hasattr(self, 'styled_panel'):
            from ui.panel import Panel
            
            # Create a panel with a parchment/scroll appearance
            self.styled_panel = Panel(
                (self.panel_rect.width, self.panel_rect.height),
                (self.panel_rect.left, self.panel_rect.top),
                colour=(70, 60, 45),  # Dark parchment colour
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(110, 90, 50)  # Darker border for scroll-like appearance
            )
        
        # Draw the styled panel
        self.styled_panel.draw(surface)
        
        # Draw floor info with a slight glow effect for emphasis
        floor_text = self.header_font.render(f"Floor {current_floor_index}: {current_floor.capitalize()}", True, WHITE)
        floor_rect = floor_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 10)
        
        # Create a subtle glow behind the text (for magical floors)
        glow_surface = pygame.Surface((floor_text.get_width() + 10, floor_text.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (230, 220, 170, 30)  # Warm parchment glow
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        glow_rect = glow_surface.get_rect(center=floor_rect.center)
        
        # Apply the glow and text
        surface.blit(glow_surface, glow_rect)
        surface.blit(floor_text, floor_rect)
    
        # Draw room info with a more subtle appearance
        room_text = self.normal_font.render(f"Room {current_room}", True, (220, 220, 200))  # Slightly off-white
        room_rect = room_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + floor_rect.height + 10)
        surface.blit(room_text, room_rect)