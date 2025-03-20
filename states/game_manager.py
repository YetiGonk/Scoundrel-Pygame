""" Game manager for handling states in the Scoundrel game. """
from states.menu_state import MenuState
from states.rules_state import RulesState
from states.playing_state import PlayingState
from states.game_over_state import GameOverState

class GameManager:
    """Manager for game states."""
    
    def __init__(self):
        self.states = {
            "menu": MenuState(self),
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self)
        }
        self.current_state = None
        self.game_data = {
            "life_points": 20,
            "max_life": 20,
            "victory": False
        }
        
        # Start with the menu state
        self.change_state("menu")
    
    def change_state(self, state_name):
        if self.current_state:
            self.current_state.exit()
        
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