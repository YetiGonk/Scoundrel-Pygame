"""Game State Controller for managing game state transitions in the Scoundrel game."""

import pygame

class GameStateController:
    """Manages game state transitions and end game conditions."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
    
    def check_game_over(self):
        """Check if the game is over due to player death."""
        if self.playing_state.life_points <= 0:
            self.end_game(False)
            return True
        return False
    
    def end_game(self, victory):
        """End the game with either victory or defeat."""
        # Save victory state
        self.playing_state.game_manager.game_data["victory"] = victory
        
        # Change to game over state
        self.playing_state.game_manager.change_state("game_over")
    
    def show_message(self, message, duration=2.0):
        """Display a temporary message on screen with a dungeon-themed panel."""
        # Create the message text
        message_text = self.playing_state.header_font.render(message, True, self.playing_state.WHITE)
        message_rect = message_text.get_rect(center=(self.playing_state.SCREEN_WIDTH//2, self.playing_state.SCREEN_HEIGHT//2 - 50))
        
        # Calculate panel size based on text (with padding)
        padding_x, padding_y = 40, 20
        panel_width = message_rect.width + padding_x * 2
        panel_height = message_rect.height + padding_y * 2
        panel_pos = (
            self.playing_state.SCREEN_WIDTH//2 - panel_width//2,
            self.playing_state.SCREEN_HEIGHT//2 - 50 - panel_height//2
        )
        
        # Create a dungeon-style message panel
        from ui.panel import Panel
        message_panel = Panel(
            (panel_width, panel_height),
            panel_pos,
            colour=(50, 40, 30),  # Dark wooden appearance
            alpha=230,
            border_radius=10,
            dungeon_style=True,
            border_width=3,
            border_color=(100, 80, 60)  # Brown border
        )
        
        # Create a subtle glow effect around the text for emphasis
        glow_size = 20
        glow_surface = pygame.Surface((message_rect.width + glow_size*2, message_rect.height + glow_size*2), pygame.SRCALPHA)
        
        # Draw a radial gradient for the glow
        glow_color = (255, 240, 200, 40)  # Warm glow color
        center = (glow_surface.get_width()//2, glow_surface.get_height()//2)
        max_radius = glow_size * 2
        
        for radius in range(max_radius, 0, -2):
            alpha = int(40 * (radius / max_radius))
            current_color = (glow_color[0], glow_color[1], glow_color[2], alpha)
            pygame.draw.circle(glow_surface, current_color, center, radius)
        
        # Store all the message components
        self.playing_state.message = {
            "panel": message_panel,
            "text": message_text,
            "rect": message_rect,
            "glow": glow_surface,
            "glow_rect": glow_surface.get_rect(center=message_rect.center),
            "time_remaining": duration
        }
        
        # Schedule a delay to clear the message
        from utils.animation import Animation
        timer = Animation(duration, on_complete=lambda: setattr(self.playing_state, 'message', None))
        self.playing_state.animation_manager.add_animation(timer)