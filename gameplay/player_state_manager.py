"""Player State Manager for handling player health and effects in the Scoundrel game."""
import pygame


class PlayerStateManager:
    """Manages player state."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def change_health(self, amount):
        """Change player health with animation."""
        old_health = self.playing_state.life_points
        
        # Calculate new health value with limits
        if amount > 0:  # Healing
            # Can't heal beyond max_life
            self.playing_state.life_points = min(self.playing_state.life_points + amount, self.playing_state.max_life)
            actual_change = self.playing_state.life_points - old_health
            # Only animate if there was an actual change
            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(False, actual_change)  # False = healing
        else:  # Damage
            # Can't go below 0
            self.playing_state.life_points = max(0, self.playing_state.life_points + amount)  # amount is negative for damage
            actual_change = old_health - self.playing_state.life_points
            # Only animate if there was an actual change
            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(True, actual_change)  # True = damage
