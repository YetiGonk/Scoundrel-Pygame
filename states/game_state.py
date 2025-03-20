"""
Base class for game states in the Scoundrel game.
"""
class GameState:
    """Base class for all game states."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
    
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    def handle_event(self, event):
        pass
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        pass