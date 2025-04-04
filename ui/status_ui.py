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
        """Draw the status UI."""
        # Get current game state info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor() or "unknown"
        current_floor_index = floor_manager.current_floor_index + 1
        
        # For room count, use the completed_rooms from playing state if available
        playing_state = self.game_manager.states["playing"]
        if hasattr(playing_state, 'completed_rooms'):
            current_room = playing_state.completed_rooms
        else:
            current_room = floor_manager.current_room
            
        total_rooms = floor_manager.FLOOR_STRUCTURE["rooms_per_floor"]
        
        # Draw semi-transparent background
        status_panel = pygame.Surface((self.panel_rect.width, self.panel_rect.height))
        status_panel.fill(WHITE)
        status_panel.set_alpha(180)
        surface.blit(status_panel, self.panel_rect)
        
        # Draw border
        pygame.draw.rect(surface, GRAY, self.panel_rect, 2)
        
        # Draw floor and room info
        floor_text = self.header_font.render(f"Floor {current_floor_index}: {current_floor.capitalize()}", True, BLACK)
        floor_rect = floor_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 10)
        surface.blit(floor_text, floor_rect)
    
        # Just display the current room number without the total
        room_text = self.normal_font.render(f"Room {current_room}", True, BLACK)
        room_rect = room_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + floor_rect.height + 10)
        surface.blit(room_text, room_rect)