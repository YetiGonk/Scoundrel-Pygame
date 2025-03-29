"""
Discard Pile component for the Scoundrel game.
"""
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_WIDTH, FLOOR_HEIGHT, GRAY, DISCARD_POSITION

class DiscardPile:
    """Represents a discard pile in the game."""
    
    def __init__(self):
        self.position = DISCARD_POSITION
        self.cards = []
        self.card_spacing = (0, -3)
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)
    
    def add_card(self, card):
        self.cards.append(card)
    
    def get_card_count(self):
        return len(self.cards)
    
    def draw(self, surface):
        if self.cards:
            for i, card in enumerate(self.cards):
                pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
                surface.blit(card.texture, pos)
        else:
            # Draw an empty discard pile placeholder
            pygame.draw.rect(surface, GRAY, self.rect, 2)