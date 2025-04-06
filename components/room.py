"""
Room component for the Scoundrel game.
"""
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, FONTS_PATH
# Make sure animation is properly imported
from utils.animation import MoveAnimation, EasingFunctions

class Room:
    """Represents a room containing cards in the game."""
    
    def __init__(self, animation_manager=None, card_spacing=35):
        self.cards = []
        self.card_spacing = card_spacing
        self.z_index_counter = 0
        self.animation_manager = animation_manager
        # Font for card names
        self.name_font = None
    
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
    
    def _draw_card_name(self, surface, card):
        """Draw the card name above the card when hovering"""
        # Initialize font if needed
        if self.name_font is None:
            self.name_font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", 18)
        
        # Create a background for the text
        padding = 8
        card_name = card.name.upper()
        
        # For weapon and potion cards, add instructions
        action_text = ""
        if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
            if card.hover_selection == "top":
                action_text = " (ADD TO INVENTORY)"
                card_name = f"{card_name}{action_text}"
            elif card.hover_selection == "bottom":
                action_text = " (USE NOW)"
                card_name = f"{card_name}{action_text}"
        
        # Render text
        text_surface = self.name_font.render(card_name, True, WHITE)
        text_rect = text_surface.get_rect()
        
        # Calculate the total float offset (idle + hover)
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
        
        # Position text above card with slight overlap, accounting for floating
        text_rect.midbottom = (card.rect.centerx, card.rect.top - 5 - total_float_offset)
        
        # Scale text to match card scale for a cohesive look
        if hasattr(card, 'scale') and card.scale > 1.0:
            # Optional: scale the text slightly, but not as much as the card
            scale_factor = 1.0 + ((card.scale - 1.0) * 0.5)  # 50% of card's scaling
            scaled_width = int(text_surface.get_width() * scale_factor)
            scaled_height = int(text_surface.get_height() * scale_factor)
            
            # Scale the text surface
            text_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
            
            # Update text rect with new size
            text_rect = text_surface.get_rect()
            text_rect.midbottom = (card.rect.centerx, card.rect.top - 5 - total_float_offset)
        
        # Create background rect slightly larger than text
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        
        # Draw background with border
        pygame.draw.rect(surface, BLACK, bg_rect)
        pygame.draw.rect(surface, WHITE, bg_rect, 2)  # 2px white border
        
        # Draw text
        surface.blit(text_surface, text_rect)
    
    def draw(self, surface):
        # Sort cards by z-index for proper layering
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        
        # Draw all cards
        for card in sorted_cards:
            card.draw(surface)
        
        # Draw card names for hovered cards
        for card in sorted_cards:
            if card.is_hovered and card.face_up and card.name:
                self._draw_card_name(surface, card)