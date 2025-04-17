"""
Deck component for the Scoundrel game.
"""
import random
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_WIDTH, FLOOR_HEIGHT, GRAY, DECK_DESC_DICT, DECK_DICT, SUITS, DECK_POSITION
from utils.resource_loader import ResourceLoader

class Deck:
    """ Represents a deck of cards in the game. """
    
    def __init__(self, floor):
        self.floor = floor if floor in list(DECK_DICT.keys()) else None
        self.position = DECK_POSITION
        self.cards = []
        self.card_stack = []
        self.card_spacing = (0, 3)
        self.texture = ResourceLoader.load_image("cards/card_back.png")
        self.texture = pygame.transform.scale(self.texture, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)
    
    def initialise_deck(self, player_deck=None):
        self.cards = []
        
        # First add cards from the floor deck configuration
        for suit in SUITS:
            for value in range(DECK_DICT[self.floor][suit]["lower"], DECK_DICT[self.floor][suit]["upper"]+1):
                self.cards.append({"suit": suit, "value": value})
        
        # Add player's delving deck cards if provided
        if player_deck:
            for card_data in player_deck:
                self.cards.append(card_data)
                
        # Shuffle the combined deck
        random.shuffle(self.cards)
        self.initialise_visuals()
    
    def initialise_visuals(self):
        self.card_stack = []
        for i in range(len(self.cards)):
            card_pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
            self.card_stack.append(card_pos)
    
    def draw_card(self):
        if self.cards:
            return self.cards.pop(0)
        return None
    
    def add_to_bottom(self, card_data):
        self.cards.append(card_data)
    
    def draw(self, surface):
        # Draw the deck
        if self.card_stack:
            for i, pos in enumerate(self.card_stack):
                surface.blit(self.texture, pos)
        else:
            # Draw an empty deck placeholder
            pygame.draw.rect(surface, GRAY, self.rect, 2)