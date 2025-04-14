""" Enhanced Game Manager for the Roguelike version of Scoundrel. """
from states.menu_state import MenuState
from states.rules_state import RulesState
from states.playing_state import PlayingState
from states.game_over_state import GameOverState
from states.merchant_state import MerchantState
from states.floor_start_state import FloorStartState

# Import roguelike components
from floor_manager import FloorManager
from item_manager import ItemManager
from spell_manager import SpellManager

from roguelike_constants import STARTING_ATTRIBUTES

class GameManager:
    """Manager for game states with roguelike elements."""
    
    def __init__(self):
        # Initialize roguelike managers
        self.floor_manager = FloorManager(self)
        self.item_manager = ItemManager(self)
        self.spell_manager = SpellManager(self)
        
        # Initialize player attributes
        self.player_gold = STARTING_ATTRIBUTES["gold"]
        
        # Initialize game states
        self.states = {
            "menu": MenuState(self),
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self),
            "merchant": MerchantState(self),
            "floor_start": FloorStartState(self)
        }
        
        self.current_state = None
        self.game_data = {
            "life_points": STARTING_ATTRIBUTES["life_points"],
            "max_life": STARTING_ATTRIBUTES["max_life"],
            "victory": False,
            "run_complete": False
        }
        
        # Storage for equipment, defeated monsters, and remaining card when transitioning between states
        self.equipped_weapon = {}
        self.defeated_monsters = []
        self.last_card_data = None
        # Flag to track if coming from merchant room
        self.coming_from_merchant = False
        
        # Start with the menu state
        self.change_state("menu")
    
    def change_state(self, state_name):
        if self.current_state:
            self.current_state.exit()
        
        # Reset coming_from_merchant flag and last_card_data when we're not going between merchant and playing
        # We need to preserve these values when going from merchant to playing
        if state_name != "playing" and (not self.current_state or not isinstance(self.current_state, MerchantState)):
            self.coming_from_merchant = False
            self.last_card_data = None
            
        self.current_state = self.states[state_name]
        self.current_state.enter()
    
    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)
    
    def update(self, delta_time):
        if self.current_state:
            self.current_state.update(delta_time)
    
    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
    
    def start_new_run(self):
        """Initialize a new roguelike run."""
        # Reset player attributes
        self.player_gold = STARTING_ATTRIBUTES["gold"]
        self.game_data["life_points"] = STARTING_ATTRIBUTES["life_points"]
        self.game_data["max_life"] = STARTING_ATTRIBUTES["max_life"]
        self.game_data["victory"] = False
        self.game_data["run_complete"] = False
        
        # Clear player items and spells
        self.item_manager.player_items = []
        self.spell_manager.player_spells = []
        
        # Initialize the floor sequence
        self.floor_manager.initialize_run()
        
        # Go to the floor start state
        self.change_state("floor_start")
    
    def advance_to_next_room(self):
        """Advance to the next room in the current floor."""
        # Update spells (reduce memory points)
        self.spell_manager.update_room_advance()
        
        # Get next room info
        room_info = self.floor_manager.advance_room()
        
        # Check if the run is complete
        if "run_complete" in room_info and room_info["run_complete"]:
            self.game_data["victory"] = True
            self.game_data["run_complete"] = True
            self.change_state("game_over")
            return
        
        # Check if this is a new floor
        if "is_floor_start" in room_info and room_info["is_floor_start"]:
            self.change_state("floor_start")
            return
        
        # Check if this is a merchant room
        if "is_merchant" in room_info and room_info["is_merchant"]:
            self.change_state("merchant")
            return
        
        # Otherwise, continue to the next regular room
        # This will be handled by the playing state
    
    def check_game_over(self):
        """Check if the game is over."""
        if self.game_data["life_points"] <= 0:
            self.game_data["victory"] = False
            self.change_state("game_over")
            return True
        return False
    
    # Item and spell effect methods
    def heal_player(self, amount=5):
        """Heal the player by the specified amount."""
        self.game_data["life_points"] = min(
            self.game_data["life_points"] + amount,
            self.game_data["max_life"]
        )
    
    def increase_max_health(self, amount=5):
        """Increase the player's maximum health."""
        self.game_data["max_life"] += amount
        self.game_data["life_points"] += amount
    
    def add_gold(self, amount=10):
        """Add gold to the player."""
        self.player_gold += amount
    
    def reveal_next_room(self):
        """Reveal the contents of the next room."""
        # This would be implemented in the UI to show what's coming
        pass
    
    def protect_from_damage(self, amount=5):
        """Create a damage shield for the next monster."""
        # This would be implemented in the playing state
        pass