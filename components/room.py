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
        """Draw the card name above the card and type below when hovering"""
        # Initialize font if needed
        if self.name_font is None:
            self.name_font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", 18)
        
        # Create a background for the text
        padding = 8
        
        # Calculate the total float offset (idle + hover)
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
        
        # Get card scale factor for text scaling
        scale_factor = 1.0
        if hasattr(card, 'scale') and card.scale > 1.0:
            # Scale the text slightly, but not as much as the card
            scale_factor = 1.0 + ((card.scale - 1.0) * 0.5)  # 50% of card's scaling
        
        # ----- DRAW CARD NAME ABOVE THE CARD -----
        card_name = card.name.upper()
                
        # For monster cards, add value as roman numeral
        if card.type == "monster":
            if " " in card_name and not any(num in card_name for num in ["I", "V", "X"]):
                card_name += f" {card._to_roman(card.value)}"
                
        # Render the name text
        text_surface = self.name_font.render(card_name, True, WHITE)
        text_rect = text_surface.get_rect()
        
        # Calculate the total float offset for proper positioning
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
        
        # Position text above card with float offset to move with card
        gap = 15  # Consistent gap between card and text
        text_rect.midbottom = (card.rect.centerx, card.rect.top - gap - total_float_offset)
        
        # Scale text if needed
        if scale_factor > 1.0:
            scaled_width = int(text_surface.get_width() * scale_factor)
            scaled_height = int(text_surface.get_height() * scale_factor)
            text_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
            text_rect = text_surface.get_rect()
            text_rect.midbottom = (card.rect.centerx, card.rect.top - gap - total_float_offset)
        
        # Create background rect and draw
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(surface, BLACK, bg_rect)
        pygame.draw.rect(surface, WHITE, bg_rect, 2)  # 2px white border
        surface.blit(text_surface, text_rect)
        
        # ----- DRAW CARD TYPE BELOW THE CARD -----
        
        # Determine the type text to display
        type_text = ""
        
        # For weapons, show weapon type (melee/ranged/arrow) and damage type (piercing/slashing/bludgeoning)
        if card.type == "weapon" and hasattr(card, 'weapon_type') and card.weapon_type:
            weapon_type = card.weapon_type.upper()
            # Only show damage type for non-arrow weapons
            if card.weapon_type != "arrow" and hasattr(card, 'damage_type') and card.damage_type:
                damage_type = card.damage_type.upper()
                type_text = f"{weapon_type} ({damage_type})"
            else:
                type_text = weapon_type
        
        # For monsters, show monster type (humanoid/undead/etc.)
        elif card.type == "monster" and hasattr(card, 'monster_type') and card.monster_type:
            type_text = card.monster_type.upper()
        
        # For potions
        elif card.type == "potion":
            type_text = "HEALING"
            
        # Only draw type label if we have text
        if type_text:
            # Render the type text (slightly smaller)
            small_font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", 16)
            type_surface = small_font.render(type_text, True, WHITE)
            type_rect = type_surface.get_rect()
            
            # Calculate the total float offset for proper positioning
            # Reusing the already calculated total_float_offset from above
            
            # Position text below card with negative float offset to move with card in same direction
            gap = 15  # Same gap as top text
            type_rect.midtop = (card.rect.centerx, card.rect.bottom + gap - total_float_offset)
            
            # Scale text if needed
            if scale_factor > 1.0:
                scaled_width = int(type_surface.get_width() * scale_factor)
                scaled_height = int(type_surface.get_height() * scale_factor)
                type_surface = pygame.transform.scale(type_surface, (scaled_width, scaled_height))
                type_rect = type_surface.get_rect()
                type_rect.midtop = (card.rect.centerx, card.rect.bottom + gap - total_float_offset)
            
            # Create background rect and draw
            type_bg_rect = type_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(surface, BLACK, type_bg_rect)
            pygame.draw.rect(surface, WHITE, type_bg_rect, 2)  # 2px white border
            surface.blit(type_surface, type_rect)
    
    def draw(self, surface):
        # Sort cards by z-index for proper layering
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        
        # Draw all cards
        for card in sorted_cards:
            card.draw(surface)
        
        # Draw card names and hover action text for hovered cards
        for card in sorted_cards:
            if card.is_hovered and card.face_up and card.name:
                self._draw_card_name(surface, card)
                
                # Draw hover text if card can be added to inventory or has attack options
                if (hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory) or \
                   (hasattr(card, 'can_show_attack_options') and card.can_show_attack_options):
                    card.draw_hover_text(surface)