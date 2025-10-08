from config import *


class InventoryManager:
    """Manages inventory positioning and display."""

    def __init__(self, playing_state):
        """Initialize with reference to playing state."""
        self.playing_state = playing_state

    @property
    def session(self):
        """Quick access to game session."""
        return self.playing_state.session

    def position_inventory_cards(self):
        """Position inventory cards in the inventory panel."""
        inventory = self.session.inventory
        
        if not inventory:
            return
        
        # Calculate positions
        spacing = 20
        total_width = (len(inventory) * CARD_WIDTH * INVENTORY_CARD_SCALE) + \
                     ((len(inventory) - 1) * spacing)
        
        start_x = INVENTORY_PANEL_X + (INVENTORY_PANEL_WIDTH - total_width) // 2
        start_y = INVENTORY_PANEL_Y + (INVENTORY_PANEL_HEIGHT - 
                                       (CARD_HEIGHT * INVENTORY_CARD_SCALE)) // 2
        
        # Position each card
        for i, card in enumerate(inventory):
            x = start_x + i * (CARD_WIDTH * INVENTORY_CARD_SCALE + spacing)
            y = start_y
            
            card.update_position((int(x), int(y)))
            
            if hasattr(card, 'update_scale'):
                card.update_scale(INVENTORY_CARD_SCALE)

    def get_inventory_card_at_position(self, position):
        """Get inventory card at mouse position."""
        # Check in reverse order (top card first)
        for card in reversed(self.session.inventory):
            if card.rect.collidepoint(position):
                return card
        
        return None
