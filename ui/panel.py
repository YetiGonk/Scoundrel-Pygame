""" Panel UI component. """

import pygame
from constants import WHITE, GRAY, BLACK, DARK_GRAY

class Panel:
    def __init__(self, width_height, top_left, colour=WHITE, alpha=220, border_radius=10):
        self.width_height = width_height
        self.top_left = top_left
        self.rect = pygame.Rect(self.top_left, self.width_height)
        self.colour = colour
        self.alpha = alpha
        self.border_radius = border_radius
        
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw a rounded rectangle
        self._draw_rounded_rect(self.surface, pygame.Rect(0, 0, self.rect.width, self.rect.height), 
            self.colour, self.border_radius)
        # Apply alpha
        self.surface.set_alpha(alpha)
    
    def _draw_rounded_rect(self, surface, rect, color, border_radius):
        """Draw a rectangle with rounded corners"""
        rect_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, color, rect_surf.get_rect(), border_radius=border_radius)
        surface.blit(rect_surf, rect.topleft)
    
    def update_position(self, pos):
        self.rect.topleft = pos
    
    def update_size(self, size):
        self.rect.size = size
        # Create new surface with the new size
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        # Redraw the rounded rectangle
        self._draw_rounded_rect(self.surface, pygame.Rect(0, 0, size[0], size[1]), 
            self.colour, self.border_radius)
        # Apply alpha
        self.surface.set_alpha(self.alpha)
    
    def update_colour(self, colour):
        self.colour = colour
        # Redraw the rounded rectangle with the new color
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self._draw_rounded_rect(self.surface, pygame.Rect(0, 0, self.rect.width, self.rect.height), 
            self.colour, self.border_radius)
        self.surface.set_alpha(self.alpha)
    
    def update_alpha(self, alpha):
        self.alpha = alpha
        self.surface.set_alpha(alpha)
    
    def update_border_radius(self, border_radius):
        self.border_radius = border_radius
        # Redraw the rounded rectangle with the new border radius
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self._draw_rounded_rect(self.surface, pygame.Rect(0, 0, self.rect.width, self.rect.height), 
            self.colour, self.border_radius)
        self.surface.set_alpha(self.alpha)
    
    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)