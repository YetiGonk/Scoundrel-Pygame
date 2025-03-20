"""
Panel UI component for the Scoundrel game.
"""
import pygame
from constants import WHITE

class Panel:
    def __init__(self, rect, color=WHITE, alpha=220):
        self.rect = rect
        self.color = color
        self.alpha = alpha
        self.surface = pygame.Surface((rect.width, rect.height))
        self.surface.fill(color)
        self.surface.set_alpha(alpha)
    
    def update_position(self, pos):
        self.rect.topleft = pos
    
    def update_size(self, size):
        self.rect.size = size
        self.surface = pygame.Surface(size)
        self.surface.fill(self.color)
        self.surface.set_alpha(self.alpha)
    
    def update_color(self, color):
        self.color = color
        self.surface.fill(color)
    
    def update_alpha(self, alpha):
        self.alpha = alpha
        self.surface.set_alpha(alpha)
    
    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)