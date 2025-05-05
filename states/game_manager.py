""" Enhanced Game Manager for the Roguelike version of Scoundrel. """
from states.title_state import TitleState  # Import the new title state
from states.menu_state import MenuState
from states.rules_state import RulesState
from states.playing_state import PlayingState
from states.game_over_state import GameOverState
from states.treasure_state import TreasureState
# Removed merchant_state and delving_deck_state imports

# Import roguelike components
from floor_manager import FloorManager

from roguelike_constants import STARTING_ATTRIBUTES

class GameManager:
    """Manager for game states with roguelike elements."""
    
    def __init__(self):
        # Initialise roguelike managers
        self.floor_manager = FloorManager(self)
        
        # Initialise player attributes
        self.player_gold = STARTING_ATTRIBUTES["gold"]
        
        # Initialise game states
        self.states = {
            "title": TitleState(self),  # New title state
            "menu": MenuState(self),    # Keep menu state for compatibility
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self),
            "treasure": TreasureState(self),
            # Removed merchant_state and delving_deck_state
        }
        
        # Initialise player card collection
        self.card_library = []  # All cards player has collected
        
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
        # Flags to track treasure room transitions
        self.coming_from_treasure = False
        self.is_bonus_treasure = False  # False = natural treasure room, True = bonus treasure room
        # Remove merchant room flag
        # self.coming_from_merchant = False
        
        # Start with the new title state
        self.change_state("title")
    
    def change_state(self, state_name):
        current_state_name = "None" if not self.current_state else self.current_state.__class__.__name__
        
        # If we're already in the requested state, don't change states
        if self.current_state and self.current_state == self.states[state_name]:
            print(f"Already in state {state_name}, not changing")
            return
            
        print(f"Changing state from {current_state_name} to {state_name}")
        
        if self.current_state:
            self.current_state.exit()
        
        # Reset coming_from_treasure flag and last_card_data when we're not going between treasure and playing
        # We need to preserve these values when going from treasure to playing
        if state_name != "playing" and (not self.current_state or not isinstance(self.current_state, TreasureState)):
            self.coming_from_treasure = False
            self.last_card_data = None
            
        # Initialise floors when going to title screen if they're not set
        if state_name == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()
            
        # Set the current state
        self.current_state = self.states[state_name]
        
        # Check if we're going back to PlayingState from a treasure room
        # In this case, ensure PlayingState.enter() isn't called twice due to flag changes
        is_treasure_to_playing = (state_name == "playing" and 
                                 hasattr(self, 'coming_from_treasure') and 
                                 self.coming_from_treasure)
                                 
        print(f"Calling enter() on {state_name}")
        self.current_state.enter()
        print(f"enter() completed for {state_name}")
    
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
        """Initialise a new roguelike run."""
        # Reset player attributes
        self.player_gold = STARTING_ATTRIBUTES["gold"]
        self.game_data["life_points"] = STARTING_ATTRIBUTES["life_points"]
        self.game_data["max_life"] = STARTING_ATTRIBUTES["max_life"]
        self.game_data["victory"] = False
        self.game_data["run_complete"] = False
        
        # Reset purchased cards for this run
        self.purchased_cards = []
        
        # Initialise the floor sequence
        self.floor_manager.initialise_run()
        
        # Set a flag to indicate this is a new run
        self.is_new_run = True
        
        # Go directly to the playing state
        self.change_state("playing")
    
    def advance_to_next_room(self):
        """Advance to the next room in the current floor."""
        print(f"GameManager.advance_to_next_room called - current room before: {self.floor_manager.current_room}")
        # Get next room info
        room_info = self.floor_manager.advance_room()
        print(f"After advance_room - room now: {self.floor_manager.current_room}")
        
        # Check if the run is complete
        if "run_complete" in room_info and room_info["run_complete"]:
            # Add treasure room at the end of the game - reward for completing all floors
            self.change_state("treasure")
            # After treasure room, will go to game over
            self.game_data["victory"] = True
            self.game_data["run_complete"] = True
            return
        
        # Check if this is a new floor and also add a treasure room when floor changes
        if "is_floor_start" in room_info and room_info["is_floor_start"]:
            # Add treasure room when floor changes - reward for completing the floor
            if self.floor_manager.current_floor_index > 0:  # Not at the very beginning of the game
                # Set a flag to indicate this is a bonus treasure room (not a natural one)
                self.is_bonus_treasure = True
                self.change_state("treasure")
            return
        
        # Check if this is a treasure room
        if "is_treasure" in room_info and room_info["is_treasure"]:
            # Set a flag to indicate this is a natural treasure room
            self.is_bonus_treasure = False
            self.change_state("treasure")
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
    
    # Helper methods
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