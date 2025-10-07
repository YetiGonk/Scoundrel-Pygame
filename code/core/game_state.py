"""
Base GameState class for all game states
"""


class GameState:
    """Base class for all game states."""

    def __init__(self, game_manager):
        self.game_manager = game_manager

    def enter(self):
        """Called when entering this state."""
        pass

    def exit(self):
        """Called when exiting this state."""
        pass

    def handle_event(self, event):
        """Handle pygame events."""
        pass

    def update(self, delta_time):
        """Update state logic."""
        pass

    def draw(self, surface):
        """Draw state visuals."""
        pass