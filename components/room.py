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

        # Get target positions for all cards
        target_positions = []
        for i in range(num_cards):
            card_position = (
                int(start_x + i * (CARD_WIDTH + self.card_spacing)), 
                int(start_y)
            )
            target_positions.append(card_position)
        
        # Update card positions (with animation if requested)
        for i, card in enumerate(self.cards):
            if animate and animation_manager is not None:
                # Don't update position here - let the animation do it
                from utils.animation import MoveAnimation, EasingFunctions
                animation = MoveAnimation(
                    card,
                    card.rect.topleft,
                    target_positions[i],
                    0.15,
                    EasingFunctions.ease_out_quad
                )
                animation_manager.add_animation(animation)
            else:
                # Immediate positioning without animation
                card.update_position(target_positions[i])
    
    def get_card_at_position(self, position):
        for card in reversed(sorted(self.cards, key=lambda c: c.z_index)):
            if card.rect.collidepoint(position):
                return card
        return None
    
    def draw(self, surface):
        for card in sorted(self.cards, key=lambda c: c.z_index):
            card.draw(surface)