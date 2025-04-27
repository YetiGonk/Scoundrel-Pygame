"""Inventory Manager for handling the player's inventory in the Scoundrel game."""
from constants import FLOOR_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT, INVENTORY_PANEL_X, INVENTORY_PANEL_Y


class InventoryManager:
    """Manages the player's inventory of cards."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def position_inventory_cards(self):
        """Position inventory cards centered vertically within the panel."""
        # Define inventory panel position - must match playing_state.py
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Use standard card size (no scaling) for inventory cards
        card_scale = 1.0
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Get number of cards in inventory
        num_cards = len(self.playing_state.inventory)
        
        # Position each card
        for i, card in enumerate(self.playing_state.inventory):
            # Apply scale to card
            card.update_scale(card_scale)
            
            # Make sure card knows it's in inventory to reduce bobbing
            card.in_inventory = True
            
            # Center X position (horizontally centered in panel)
            inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)
            
            # Calculate Y position based on number of cards
            if num_cards == 1:
                # Single card - center vertically in panel
                inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
            elif num_cards == 2:
                # Two cards - one above center, one below center
                if i == 0:
                    # First card positioned in top half
                    inventory_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
                else:
                    # Second card positioned in bottom half
                    inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)
            
            # Update the card's position
            card.update_position((inventory_x, inventory_y))
    
    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.playing_state.inventory:
            if card.rect.collidepoint(position):
                return card
        return None