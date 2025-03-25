""" Menu state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, LIGHT_GRAY
from states.game_state import GameState
from ui.panel import Panel
from utils.resource_loader import ResourceLoader

class MenuState(GameState):
    """The main menu state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None
        self.start_button_rect = None
    
    def enter(self):
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 64)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load floor
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.start_button_rect and self.start_button_rect.collidepoint(event.pos):
                self.game_manager.change_state("rules")
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Create a semi-transparent panel
        from constants import MENU_WIDTH, MENU_HEIGHT, MENU_POSITION
        panel = Panel((MENU_WIDTH, MENU_HEIGHT), MENU_POSITION)
        panel.draw(surface)
        
        # Draw title
        title_text = self.title_font.render("SCOUNDREL", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, panel.rect.top + 50))
        surface.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.header_font.render("The 52-Card Dungeon Crawler", True, BLACK)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, title_rect.bottom + 30))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw start button
        self.start_button_rect = pygame.Rect(0, 0, 225, 50)
        self.start_button_rect.center = (SCREEN_WIDTH//2, panel.rect.bottom + 150)
        pygame.draw.rect(surface, LIGHT_GRAY, self.start_button_rect)
        pygame.draw.rect(surface, BLACK, self.start_button_rect, 2)
        
        button_text = self.body_font.render("START GAME", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        surface.blit(button_text, button_text_rect)