""" Floor manager for handling multiple floors in the Scoundrel game. """
import random
from roguelike_constants import FLOOR_TYPES, FLOOR_STRUCTURE, DECK_VARIATIONS, BOSS_CARDS

class FloorManager:
    """Manages the different floors in a run."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.FLOOR_STRUCTURE = FLOOR_STRUCTURE
        self.floors = []
        self.current_floor_index = 0
        self.current_room = 0
        self.total_floors = len(FLOOR_TYPES)
        
    def initialize_run(self):
        """Initialize a new run with randomized floor order."""
        self.floors = random.sample(FLOOR_TYPES, self.total_floors)
        self.current_floor_index = 0
        self.current_room = 0
        return self.get_current_floor()
    
    def get_current_floor(self):
        """Get the current floor type."""
        return self.floors[self.current_floor_index]
    
    def advance_room(self):
        """Move to the next room in the current floor."""
        self.current_room += 1
        
        # Check if we've reached the end of the floor
        if self.current_room > FLOOR_STRUCTURE["rooms_per_floor"]:
            return self.advance_floor()
        
        # Check if this is a merchant room
        is_merchant = self.current_room in FLOOR_STRUCTURE["merchant_rooms"]
        
        # Check if this is a boss room
        is_boss = self.current_room == FLOOR_STRUCTURE["boss_room"]
        
        return {
            "floor": self.get_current_floor(),
            "room": self.current_room,
            "is_merchant": is_merchant,
            "is_boss": is_boss
        }
    
    def advance_floor(self):
        """Move to the next floor."""
        self.current_floor_index += 1
        # Reset room counter when moving to a new floor
        self.current_room = 0
        
        # Check if run is complete
        if self.current_floor_index >= len(self.floors):
            return {"run_complete": True}
        
        # Reset completion tracking in the playing state if it exists
        if hasattr(self.game_manager, 'states') and 'playing' in self.game_manager.states:
            playing_state = self.game_manager.states["playing"]
            if hasattr(playing_state, 'completed_rooms'):
                playing_state.completed_rooms = 0
        
        return {
            "floor": self.get_current_floor(),
            "room": self.current_room,
            "is_floor_start": True
        }
    
    def get_floor_deck_variation(self):
        """Get the deck variation for the current floor."""
        current_floor = self.get_current_floor()
        if current_floor and current_floor in DECK_VARIATIONS:
            return DECK_VARIATIONS[current_floor]
        return {}
    
    def get_boss_card(self):
        """Get the boss card for the current floor."""
        current_floor = self.get_current_floor()
        if current_floor and current_floor in BOSS_CARDS:
            return BOSS_CARDS[current_floor].copy()
        return None
    
    def is_merchant_room(self):
        """Check if the current room is a merchant room."""
        return self.current_room in FLOOR_STRUCTURE["merchant_rooms"]
    
    def is_boss_room(self):
        """Check if the current room is a boss room."""
        return self.current_room == FLOOR_STRUCTURE["boss_room"]