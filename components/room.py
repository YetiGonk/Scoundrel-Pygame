"""
Room component for the Scoundrel game.
"""
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
# Make sure animation is properly imported
from utils.animation import MoveAnimation, EasingFunctions

class Room:
    """Represents a room containing cards in the game."""
    
    def __init__(self, animation_manager=None, card_spacing=35):
        self.cards = []
        self.card_spacing = card_spacing
        self.z_index_counter = 0
        self.animation_manager = animation_manager
    
    def add_card(self, card):
        self.cards.append(card)
        
        # Set z-index for proper layering
        card.z_index = self.z_index_counter
        self.z_index_counter += 1
    
    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            # Do not immediately animate - let the calling code handle animation timing
            # This prevents cards from disappearing during animations
            if len(self.cards) > 0:
                self.position_cards(animate=True, animation_manager=self.animation_manager)
    
    def clear(self):
        self.cards.clear()
    
    def get_card_count(self):
        return len(self.cards)
    
    def position_cards(self, animate=False, animation_manager=None):
        if not self.cards:
            return

        # Calculate positions with proper centering
        num_cards = len(self.cards)
        total_width = (CARD_WIDTH * num_cards) + (self.card_spacing * (num_cards - 1))
        
        # Center the entire card group on screen
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        # Sort cards by z-index for consistent positioning
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        
        # Get target positions for all cards
        for i, card in enumerate(sorted_cards):
            card_position = (0, 0)
            if num_cards == 1:
                # position final card as if left most side of 4 cards
                card_position = (
                    int(start_x - (CARD_WIDTH + self.card_spacing) * 1.5),
                    int(start_y)
                )
            else:
                card_position = (
                    int(start_x + i * (CARD_WIDTH + self.card_spacing)), 
                    int(start_y)
                )
            
            if animate and animation_manager is not None:
                # Create animation with easing
                from utils.animation import MoveAnimation, EasingFunctions
                animation = MoveAnimation(
                    card,
                    card.rect.topleft,
                    card_position,
                    0.3,  # Smooth animation duration
                    EasingFunctions.ease_out_quad
                )
                animation_manager.add_animation(animation)
            else:
                # Immediate positioning without animation
                card.update_position(card_position)
    
    def get_card_at_position(self, position):
        for card in reversed(sorted(self.cards, key=lambda c: c.z_index)):
            if card.rect.collidepoint(position):
                return card
        return None
    
    def draw(self, surface):
        for card in sorted(self.cards, key=lambda c: c.z_index):
            card.draw(surface)