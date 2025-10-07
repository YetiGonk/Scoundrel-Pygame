from config import *

class InventoryManager:
    """Manages the player's inventory of cards."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def position_inventory_cards(self):
        """Position inventory cards centered vertically within the panel."""

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        card_scale = 1.0

        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)

        num_cards = len(self.playing_state.inventory)

        for i, card in enumerate(self.playing_state.inventory):

            card.update_scale(card_scale)

            card.in_inventory = True

            inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)

            if num_cards == 1:

                inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
            elif num_cards == 2:

                if i == 0:

                    inventory_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
                else:

                    inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)

            card.update_position((inventory_x, inventory_y))

    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.playing_state.inventory:
            if card.rect.collidepoint(position):
                return card
        return None