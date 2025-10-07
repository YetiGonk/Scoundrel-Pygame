class GameStateController:
    """Manages game state transitions and end game conditions."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def check_game_over(self):
        """Check if the game is over due to player death."""
        if self.playing_state.life_points <= 0:
            self.end_game(False)
            return True
        return False

    def end_game(self, victory):
        """End the game with either victory or defeat."""

        self.playing_state.game_manager.game_data["victory"] = victory

        self.playing_state.game_manager.change_state("game_over")

    def show_message(self, message, duration=1.2):
        """Display a small, non-blocking notification above the room cards."""

        message_text = self.playing_state.body_font.render(message, True, self.playing_state.WHITE)

        room_top = self.playing_state.SCREEN_HEIGHT//2 - 120
        message_rect = message_text.get_rect(center=(self.playing_state.SCREEN_WIDTH//2, room_top - 25))

        padding_x, padding_y = 15, 8
        bg_rect = pygame.Rect(
            message_rect.left - padding_x,
            message_rect.top - padding_y,
            message_rect.width + padding_x * 2,
            message_rect.height + padding_y * 2
        )

        self.playing_state.message = {
            "text": message_text,
            "rect": message_rect,
            "bg_rect": bg_rect,
            "alpha": 0,
            "fade_in": True,
            "time_remaining": duration,
            "fade_speed": 510
        }