"""Inventory Manager for handling the player's inventory in the Scoundrel game."""
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, SPELL_PANEL_HEIGHT


class InventoryManager:
    """Manages the player's inventory of cards."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
    
    def position_inventory_cards(self):
        """Position all inventory cards in their proper places."""
        # Calculate position based on inventory panel location
        
        # Calculate vertical center between spell and item panels
        vertical_center = (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT + 
            (ITEM_PANEL_POSITION[1] - (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT))// 2)
        
        # Create a smaller inventory panel
        inv_width = ITEM_PANEL_WIDTH
        inv_height = 120  # Smaller height
        inv_x = SCREEN_WIDTH - inv_width - 40  # Same x as item/spell panels
        inv_y = vertical_center - inv_height // 2  # Center between items and spells
        
        # Scale cards to fit inventory panel nicely
        card_scale = 0.8  # 80% of normal size
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Center cards in inventory panel with proper spacing
        margin = 10
        card_spacing = 10  # Fixed spacing between cards
        if self.playing_state.MAX_INVENTORY_SIZE > 1:
            card_spacing = (inv_width - (self.playing_state.MAX_INVENTORY_SIZE * scaled_card_width) - (margin * 2)) // max(1, self.playing_state.MAX_INVENTORY_SIZE - 1)
        
        # Position each card
        for i, card in enumerate(self.playing_state.inventory):
            # Apply scale to card
            card.update_scale(card_scale)
            
            # Make sure card knows it's in inventory to reduce bobbing
            card.in_inventory = True
            
            # Calculate position
            inventory_x = inv_x + margin + (i * (scaled_card_width + card_spacing))
            inventory_y = inv_y + margin
            
            card.update_position((inventory_x, inventory_y))
    
    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.playing_state.inventory:
            if card.rect.collidepoint(position):
                return card
        return None