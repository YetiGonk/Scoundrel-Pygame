import pygame


class GameStateController:
    """Manages game state transitions and UI messages."""

    def __init__(self, playing_state):
        """Initialize with reference to playing state."""
        self.playing_state = playing_state

    @property
    def session(self):
        """Quick access to game session."""
        return self.playing_state.session

    def check_game_over(self):
        """Check if player is dead and transition to game over."""
        if self.session.is_player_dead():
            self.playing_state.game_manager.game_data["victory"] = False
            self.playing_state.game_manager.change_state("game_over")

    def show_message(self, text, duration=2.0):
        """Show a message to the player with fade effect."""
        # Get font (use ui_components if available)
        if hasattr(self.playing_state, 'ui_components'):
            font = self.playing_state.ui_components.body_font
        else:
            font = pygame.font.Font(None, 36)
        
        # Create message surface
        message_surface = font.render(text, True, (255, 255, 255))
        message_rect = message_surface.get_rect()
        
        # Position in center
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        message_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        
        # Create background rect (slightly larger)
        bg_rect = message_rect.inflate(40, 20)
        
        # Set message data
        self.playing_state.message = {
            "text": message_surface,
            "rect": message_rect,
            "bg_rect": bg_rect,
            "alpha": 0,
            "fade_in": True,
            "fade_speed": 255 / 0.3,  # Fade in over 0.3 seconds
            "time_remaining": duration,
        }
