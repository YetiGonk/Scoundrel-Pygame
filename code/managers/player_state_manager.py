class PlayerStateManager:
    """Manages player state."""

    def __init__(self, playing_state):
        """Initialize with reference to playing state."""
        self.playing_state = playing_state

    @property
    def session(self):
        """Quick access to game session."""
        return self.playing_state.session

    @property
    def animation_controller(self):
        """Quick access to animation controller."""
        return self.playing_state.animation_controller

    def change_health(self, amount):
        """Change player health with animation."""
        # Use session's change_health which handles clamping
        actual_change = self.session.change_health(amount)
        
        # Animate the change
        if actual_change != 0:
            is_damage = actual_change < 0
            abs_change = abs(actual_change)
            self.animation_controller.animate_health_change(is_damage, abs_change)
