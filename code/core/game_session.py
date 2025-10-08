"""
core/game_session.py

Single source of truth for all game state during a playthrough.
NO MORE scattered state, duplicate trackers, or sync methods!
"""

from entities.deck import Deck, DiscardPile
from entities.room import Room


class GameSession:
    """
    Holds ALL game state for a single playthrough.
    This is the ONLY place game state should live.
    """

    def __init__(self, floor_type="dungeon"):
        """Initialize a new game session."""
        
        # Game components
        self.deck = Deck(floor_type)
        self.discard_pile = DiscardPile()
        self.room = Room()
        self.current_floor = floor_type
        
        # Player state
        self.life_points = 20
        self.max_life = 20
        self.inventory = []
        self.max_inventory_size = 2
        
        self.equipped_weapon = None
        self.defeated_monsters = []
        
        # Room/floor progress
        self.completed_rooms = 0
        self.current_room_complete = False
        self.floor_complete = False
        
        # Turn state
        self.ran_last_turn = False
        
    # ========================================================================
    # Player State Helpers
    # ========================================================================
    
    def has_weapon(self):
        """Check if player has a weapon equipped."""
        return self.equipped_weapon is not None
    
    def can_add_to_inventory(self):
        """Check if inventory has space."""
        return len(self.inventory) < self.max_inventory_size
    
    def add_to_inventory(self, card):
        """Add a card to inventory if space available."""
        if self.can_add_to_inventory():
            self.inventory.append(card)
            return True
        return False
    
    def remove_from_inventory(self, card):
        """Remove a card from inventory."""
        if card in self.inventory:
            self.inventory.remove(card)
            return True
        return False
    
    def equip_weapon(self, weapon_card):
        """Equip a weapon, returning old weapon and defeated monsters if any."""
        old_weapon = self.equipped_weapon
        old_monsters = self.defeated_monsters.copy()
        
        self.equipped_weapon = weapon_card
        self.defeated_monsters = []
        
        return old_weapon, old_monsters
    
    def unequip_weapon(self):
        """Remove equipped weapon, returning it and defeated monsters."""
        weapon = self.equipped_weapon
        monsters = self.defeated_monsters.copy()
        
        self.equipped_weapon = None
        self.defeated_monsters = []
        
        return weapon, monsters
    
    def add_defeated_monster(self, monster_card):
        """Add a monster to the defeated stack."""
        self.defeated_monsters.append(monster_card)
    
    def change_health(self, amount):
        """
        Change player health, clamping to valid range.
        Returns actual amount changed.
        """
        old_health = self.life_points
        
        if amount > 0:
            # Healing
            self.life_points = min(self.life_points + amount, self.max_life)
        else:
            # Damage
            self.life_points = max(0, self.life_points + amount)
        
        return self.life_points - old_health
    
    def is_player_dead(self):
        """Check if player is dead."""
        return self.life_points <= 0
    
    # ========================================================================
    # Room/Floor State Helpers
    # ========================================================================
    
    def is_room_empty(self):
        """Check if current room has no cards."""
        return len(self.room.cards) == 0
    
    def has_single_card_remaining(self):
        """Check if room has exactly one card."""
        return len(self.room.cards) == 1
    
    def has_deck_cards_remaining(self):
        """Check if deck still has cards."""
        return len(self.deck.cards) > 0
    
    def mark_room_complete(self):
        """Mark current room as complete."""
        if not self.current_room_complete:
            self.current_room_complete = True
            self.completed_rooms += 1
    
    def start_new_room(self):
        """Reset flags for a new room."""
        self.current_room_complete = False
        self.ran_last_turn = False
    
    def mark_floor_complete(self):
        """Mark current floor as complete."""
        self.floor_complete = True
    
    def reset_for_new_floor(self, floor_type):
        """Reset state for a new floor."""
        self.current_floor = floor_type
        self.deck = Deck(floor_type)
        self.discard_pile.cards = []
        self.completed_rooms = 0
        self.floor_complete = False
        self.current_room_complete = False
    
    # ========================================================================
    # Save/Load Support
    # ========================================================================
    
    def save_to_dict(self):
        """Save session state to a dictionary."""
        return {
            "life_points": self.life_points,
            "max_life": self.max_life,
            "current_floor": self.current_floor,
            "completed_rooms": self.completed_rooms,
        }
    
    def load_from_dict(self, data):
        """Load session state from a dictionary."""
        self.life_points = data.get("life_points", 20)
        self.max_life = data.get("max_life", 20)
        self.current_floor = data.get("current_floor", "dungeon")
        self.completed_rooms = data.get("completed_rooms", 0)
