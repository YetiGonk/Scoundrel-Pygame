""" Panel UI component. """

import pygame
from constants import WHITE

class Panel:
    def __init__(self, width_height, top_left, colour=WHITE, alpha=220):
        self.width_height = width_height
        self.top_left = top_left
        self.rect = pygame.Rect(self.top_left, self.width_height)
        self.colour = colour
        self.alpha = alpha
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(colour)
        self.surface.set_alpha(alpha)
    
    def update_position(self, pos):
        self.rect.topleft = pos
    
    def update_size(self, size):
        self.rect.size = size
        self.surface = pygame.Surface(size)
        self.surface.fill(self.colour)
        self.surface.set_alpha(self.alpha)
    
    def update_colour(self, colour):
        self.colour = colour
        self.surface.fill(colour)
    
    def update_alpha(self, alpha):
        self.alpha = alpha
        self.surface.set_alpha(alpha)
    
    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)