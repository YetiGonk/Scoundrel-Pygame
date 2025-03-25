""" Rules state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY
from states.game_state import GameState
from utils.resource_loader import ResourceLoader

class RulesState(GameState):
    """The rules screen state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
    
    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = pygame.font.SysFont(None, 20)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load floor
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1: # left click
            self.game_manager.change_state("playing")
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Create a semi-transparent panel
        panel = pygame.Surface((600, 500))
        panel.fill(WHITE)
        panel.set_alpha(220)
        panel_rect = panel.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(panel, panel_rect)
        
        # Draw title
        title_text = self.header_font.render("HOW TO PLAY", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, panel_rect.top + 40))
        surface.blit(title_text, title_rect)
        
        # Rules text
        rules = [
            "SCOUNDREL is a card-based dungeon crawler:",
            "",
            "• Each 'dungeon room' consists of 4 cards from the deck",
            "• Cards represent:",
            "  - Monsters (Clubs & Spades)",
            "  - Weapons (Diamonds)",
            "  - Potions (Hearts)",
            "• You start with 20 life points",
            "• Defeat monsters with your bare hands (take full damage)",
            "• Or defeat them with weapons (take partial damage)",
            "• Weapons lose durability and can only battle weaker monsters each time",
            "• Heal with potions",
            "• You can RUN from dangerous rooms (but not twice in a row)",
            "• Win by surviving until the deck is empty",
            "• Lose if your health reaches zero"
        ]
        
        y_offset = title_rect.bottom + 10
        for line in rules:
            rule_text = self.normal_font.render(line, True, BLACK)
            rule_rect = rule_text.get_rect(left=panel_rect.left + 40, top=y_offset)
            surface.blit(rule_text, rule_rect)
            y_offset += 25
        
        # Continue text
        continue_text = self.body_font.render("Left-click to continue...", True, GRAY)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, panel_rect.bottom - 30))
        surface.blit(continue_text, continue_rect)