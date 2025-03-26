""" Spell manager for handling spells in the Scoundrel game. """
import random
from roguelike_constants import SPELL_TEMPLATE, RARITY_TYPES, FLOOR_START_SELECTION

class Spell:
    """Represents a spell with temporary effects."""
    
    def __init__(self, spell_data):
        self.name = spell_data.get("name", "Unknown Spell")
        self.description = spell_data.get("description", "")
        self.rarity = spell_data.get("rarity", "common")
        self.memory_points = spell_data.get("memory_points", 3)
        self.remaining_memory = self.memory_points
        self.effect = spell_data.get("effect", "")
        self.icon = spell_data.get("icon", "")
        self.price = self.calculate_price()
    
    def cast(self):
        """Cast the spell, executing its effect."""
        if self.remaining_memory > 0:
            self.remaining_memory -= 1
            return True
        return False  # Spell is forgotten
    
    def is_forgotten(self):
        """Check if the spell is forgotten."""
        return self.remaining_memory <= 0
    
    def reduce_memory(self):
        """Reduce memory points when advancing to a new room."""
        if self.remaining_memory > 0:
            self.remaining_memory -= 1
        return self.is_forgotten()
    
    def calculate_price(self):
        """Calculate the spell's price based on rarity and memory points."""
        base_price = {
            "common": 30,
            "uncommon": 60,
            "rare": 120,
            "legendary": 240
        }.get(self.rarity, 30)
        
        # Adjust for memory points
        memory_factor = min(2.0, 0.5 + (self.memory_points / 5))
        return int(base_price * memory_factor)

class SpellManager:
    """Manages spell collections and operations."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.available_spells = []  # All defined spells
        self.player_spells = []  # Spells the player knows
        self.max_spells = 2  # Initial max spells the player can memorize
    
    def load_spells(self, spells_data):
        """Load spells from data."""
        self.available_spells = []
        for spell_data in spells_data:
            self.available_spells.append(Spell(spell_data))
    
    def get_random_spells(self, count=1, rarity_weights=None, excluded_spells=None):
        """Get random spells with rarity weights."""
        if excluded_spells is None:
            excluded_spells = []
        
        # Default rarity weights
        if rarity_weights is None:
            rarity_weights = {
                "common": 50,
                "uncommon": 30,
                "rare": 15,
                "legendary": 5
            }
        
        # Filter out excluded spells
        eligible_spells = [spell for spell in self.available_spells if spell not in excluded_spells]
        if not eligible_spells:
            return []
        
        # Select random spells based on rarity
        selected_spells = []
        for _ in range(count):
            if not eligible_spells:
                break
                
            # Calculate total weight
            total_weight = sum(rarity_weights.get(spell.rarity, 0) for spell in eligible_spells)
            if total_weight <= 0:
                break
                
            # Select a spell based on rarity weights
            rand_val = random.randint(1, total_weight)
            cumulative_weight = 0
            
            for spell in eligible_spells:
                cumulative_weight += rarity_weights.get(spell.rarity, 0)
                if rand_val <= cumulative_weight:
                    selected_spells.append(spell)
                    eligible_spells.remove(spell)
                    break
        
        return selected_spells
    
    def get_floor_start_selection(self):
        """Get a selection of spells for the start of a floor."""
        return self.get_random_spells(FLOOR_START_SELECTION["spells"])
    
    def add_player_spell(self, spell):
        """Add a spell to the player's spellbook."""
        if len(self.player_spells) < self.max_spells:
            self.player_spells.append(spell)
            return True
        return False
    
    def remove_player_spell(self, spell):
        """Remove a spell from the player's spellbook."""
        if spell in self.player_spells:
            self.player_spells.remove(spell)
            return True
        return False
    
    def cast_spell(self, spell_index):
        """Cast a spell from the player's spellbook."""
        if 0 <= spell_index < len(self.player_spells):
            spell = self.player_spells[spell_index]
            if spell.cast():
                # Execute the effect
                if hasattr(self.game_manager, spell.effect):
                    effect_method = getattr(self.game_manager, spell.effect)
                    effect_method()
                
                # Remove if forgotten
                if spell.is_forgotten():
                    self.player_spells.pop(spell_index)
                
                return True
        return False
    
    def update_room_advance(self):
        """Update spells when advancing to a new room."""
        forgotten_spells = []
        for spell in self.player_spells:
            if spell.reduce_memory():
                forgotten_spells.append(spell)
        
        # Remove forgotten spells
        for spell in forgotten_spells:
            self.player_spells.remove(spell)
        
        return forgotten_spells
    
    def increase_max_spells(self, amount=1):
        """Increase the maximum number of spells the player can memorize."""
        self.max_spells += amount