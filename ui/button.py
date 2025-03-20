"""
Button UI component for the Scoundrel game.
"""
import pygame
from constants import LIGHT_GRAY, BLACK

class Button:    
    def __init__(self, rect, text, font, text_color=BLACK, bg_color=LIGHT_GRAY, border_color=BLACK):
        self.rect = rect
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.is_hovered = False
        
        # Pre-render the text
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return previous_hover != self.is_hovered
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        # Draw button background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw button border
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Draw button text
        surface.blit(self.text_surface, self.text_rect)