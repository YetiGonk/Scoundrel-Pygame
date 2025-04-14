"""Player State Manager for handling player health, gold, and effects in the Scoundrel game."""
import pygame


class PlayerStateManager:
    """Manages player state such as health, gold, and damage shield."""
    
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
    
    def set_damage_shield(self, amount):
        """Set a damage shield for the player."""
        self.playing_state.damage_shield = amount
        
        # Create a visual indicator for the shield
        shield_effect = pygame.Surface((self.playing_state.SCREEN_WIDTH, self.playing_state.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(shield_effect, (0, 100, 255, 100), (self.playing_state.SCREEN_WIDTH//2, self.playing_state.SCREEN_HEIGHT//2), 150, 5)
    
    def use_item(self, item_index):
        """Use an item from the player's inventory."""
        if self.playing_state.game_manager.item_manager.use_item(item_index):
            # Apply shield effect if it's a protection item
            if item_index < len(self.playing_state.game_manager.item_manager.player_items):
                item = self.playing_state.game_manager.item_manager.player_items[item_index]
                if item.effect == "protect_from_damage":
                    self.set_damage_shield(10)  # Set a default shield value
            
            # Refresh the UI
            self.playing_state.ui_factory.create_item_buttons()
            return True
        return False
    
    def cast_spell(self, spell_index):
        """Cast a spell from the player's spellbook."""
        if self.playing_state.game_manager.spell_manager.cast_spell(spell_index):
            # Apply shield effect if it's a protection spell
            if spell_index < len(self.playing_state.game_manager.spell_manager.player_spells):
                spell = self.playing_state.game_manager.spell_manager.player_spells[spell_index]
                if spell.effect == "protect_from_damage":
                    self.set_damage_shield(5)  # Set a default shield value
            
            # Refresh the UI
            self.playing_state.ui_factory.create_spell_buttons()
            return True
        return False