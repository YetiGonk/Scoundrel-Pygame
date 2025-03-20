"""
Game over state for the Scoundrel game.
"""
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, RED, LIGHT_GRAY
from states.game_state import GameState
from utils.resource_loader import ResourceLoader

class GameOverState(GameState):
    """The game over state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None
        self.restart_button_rect = None
        
        # We will use the PlayingState to render the game in the background
        self.playing_state = None
    
    def enter(self):
        # Get the PlayingState instance for rendering
        self.playing_state = self.game_manager.states["playing"]
        
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.restart_button_rect and self.restart_button_rect.collidepoint(event.pos):
                # Reset game data
                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False
                
                # Completely reset the playing state
                from states.playing_state import PlayingState
                self.game_manager.states["playing"] = PlayingState(self.game_manager)
                
                # Start a new game
                self.game_manager.change_state("menu")
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw the game state behind (this assumes PlayingState.draw can work in a "view only" mode)
        if self.playing_state:
            self.playing_state.draw(surface)
        
        # Create a semi-transparent panel
        panel = pygame.Surface((200, 80))
        panel.fill(WHITE)
        panel.set_alpha(220)
        panel_rect = panel.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(panel, panel_rect)
        
        # Draw result
        if self.game_manager.game_data["victory"]:
            result_text = self.header_font.render("You Win!", True, GREEN)
        else:
            result_text = self.header_font.render("You Are Dead...", True, RED)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, panel_rect.top + 25))
        surface.blit(result_text, result_rect)
        
        # Draw restart button
        self.restart_button_rect = pygame.Rect(0, 0, 100, 30)
        self.restart_button_rect.center = (SCREEN_WIDTH//2, panel_rect.bottom - 20)
        pygame.draw.rect(surface, LIGHT_GRAY, self.restart_button_rect)
        pygame.draw.rect(surface, BLACK, self.restart_button_rect, 2)
        
        button_text = self.body_font.render("Restart", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.restart_button_rect.center)
        surface.blit(button_text, button_text_rect)