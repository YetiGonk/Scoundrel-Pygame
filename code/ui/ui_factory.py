import pygame
from pygame.locals import *

from config import *

from ui.button import Button


class UIFactory:
    """Creates and manages UI elements."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def create_run_button(self):
        """Create the run button with dungeon styling."""

        run_width = 90
        run_height = 45

        run_x = SCREEN_WIDTH // 2
        run_y = 170

        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)

        self.playing_state.run_button = Button(
            run_button_rect,
            "RUN",
            self.playing_state.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(70, 20, 20),
            border_colour=(120, 40, 40)
        )