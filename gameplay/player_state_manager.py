"""Player State Manager for handling player health, gold, and effects in the Scoundrel game."""
import pygame


class PlayerStateManager:
    """Manages player state such as health and gold."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
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
    
    def change_gold(self, amount):
        """Change player gold amount with animation."""
        old_gold = self.playing_state.game_manager.player_gold
        
        # Update the gold amount in the game manager
        self.playing_state.game_manager.player_gold += amount
        
        # Ensure gold doesn't go negative
        if self.playing_state.game_manager.player_gold < 0:
            self.playing_state.game_manager.player_gold = 0
            
        # Calculate actual change for animation
        actual_change = abs(amount)
        
        # Only animate if there was an actual change
        if actual_change > 0:
            self.playing_state.animation_controller.animate_gold_change(amount < 0, actual_change)  # True = gold loss, False = gold gain

