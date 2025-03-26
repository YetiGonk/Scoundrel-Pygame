""" Item manager for handling roguelike items in the Scoundrel game. """
import random
from roguelike_constants import ITEM_TEMPLATE, RARITY_TYPES, FLOOR_START_SELECTION

class Item:
    """Represents an item that provides passive or active effects."""
    
    def __init__(self, item_data):
        self.name = item_data.get("name", "Unknown Item")
        self.description = item_data.get("description", "")
        self.type = item_data.get("type", "passive")
        self.rarity = item_data.get("rarity", "common")
        self.durability = item_data.get("durability", 0)
        self.max_durability = self.durability
        self.effect = item_data.get("effect", "")
        self.icon = item_data.get("icon", "")
        self.price = self.calculate_price()
    
    def use(self):
        """Use the item and reduce durability if applicable."""
        if self.durability > 0:
            self.durability -= 1
            return True
        elif self.durability == 0:  # Infinite use
            return True
        return False  # Item is broken
    
    def is_broken(self):
        """Check if the item is broken."""
        return self.durability == -1
    
    def calculate_price(self):
        """Calculate the item's price based on rarity and durability."""
        base_price = {
            "common": 25,
            "uncommon": 50,
            "rare": 100,
            "legendary": 200
        }.get(self.rarity, 25)
        
        # Adjust for durability (higher durability = higher price)
        if self.durability > 0:
            durability_factor = min(2.0, 0.5 + (self.durability / 10))
            return int(base_price * durability_factor)
        elif self.durability == 0:  # Infinite use
            return base_price * 3
        
        return base_price

class ItemManager:
    """Manages item collections and operations."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.available_items = []  # All defined items
        self.player_items = []  # Items the player has
        self.max_items = 3  # Initial max items the player can carry
    
    def load_items(self, items_data):
        """Load items from data."""
        self.available_items = []
        for item_data in items_data:
            self.available_items.append(Item(item_data))
    
    def get_random_items(self, count=1, rarity_weights=None, excluded_items=None):
        """Get random items with rarity weights."""
        if excluded_items is None:
            excluded_items = []
        
        # Default rarity weights
        if rarity_weights is None:
            rarity_weights = {
                "common": 50,
                "uncommon": 30,
                "rare": 15,
                "legendary": 5
            }
        
        # Filter out excluded items
        eligible_items = [item for item in self.available_items if item not in excluded_items]
        if not eligible_items:
            return []
        
        # Select random items based on rarity
        selected_items = []
        for _ in range(count):
            if not eligible_items:
                break
                
            # Calculate total weight
            total_weight = sum(rarity_weights.get(item.rarity, 0) for item in eligible_items)
            if total_weight <= 0:
                break
                
            # Select an item based on rarity weights
            rand_val = random.randint(1, total_weight)
            cumulative_weight = 0
            
            for item in eligible_items:
                cumulative_weight += rarity_weights.get(item.rarity, 0)
                if rand_val <= cumulative_weight:
                    selected_items.append(item)
                    eligible_items.remove(item)
                    break
        
        return selected_items
    
    def get_floor_start_selection(self):
        """Get a selection of items for the start of a floor."""
        return self.get_random_items(FLOOR_START_SELECTION["items"])
    
    def add_player_item(self, item):
        """Add an item to the player's inventory."""
        if len(self.player_items) < self.max_items:
            self.player_items.append(item)
            return True
        return False
    
    def remove_player_item(self, item):
        """Remove an item from the player's inventory."""
        if item in self.player_items:
            self.player_items.remove(item)
            return True
        return False
    
    def use_item(self, item_index):
        """Use an item from the player's inventory."""
        if 0 <= item_index < len(self.player_items):
            item = self.player_items[item_index]
            if item.use():
                # Execute the effect
                if hasattr(self.game_manager, item.effect):
                    effect_method = getattr(self.game_manager, item.effect)
                    effect_method()
                
                # Remove if broken
                if item.is_broken():
                    self.player_items.pop(item_index)
                
                return True
        return False
    
    def increase_max_items(self, amount=1):
        """Increase the maximum number of items the player can carry."""
        self.max_items += amount