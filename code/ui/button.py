import pygame

from config import *

from ui.panel import Panel

class Button:
    def __init__(self, rect, text, font, text_colour=BLACK, bg_colour=LIGHT_GRAY, border_colour=BLACK,
                dungeon_style=False, panel_colour=None, border_width=None, callback=None):

        if panel_colour is None:
            panel_colour = BUTTON_PANEL_COLOUR
        if border_width is None:
            border_width = BUTTON_BORDER_WIDTH
        self.rect = rect
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.bg_colour = bg_colour
        self.border_colour = border_colour
        self.is_hovered = False
        self.dungeon_style = dungeon_style
        self.panel_colour = panel_colour
        self.border_width = border_width
        self.panel = None
        self.callback = callback

        self.text_surface = font.render(text, True, text_colour)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        if self.dungeon_style:
            self._create_dungeon_panel()

    def _create_dungeon_panel(self):
        """Create a dungeon-styled panel for the button"""
        try:

            self.panel = Panel(
                (self.rect.width, self.rect.height),
                (self.rect.left, self.rect.top),
                colour=self.panel_colour,
                alpha=BUTTON_ALPHA,
                border_radius=BUTTON_BORDER_RADIUS,
                dungeon_style=True,
                border_width=self.border_width,
                border_colour=self.border_colour
            )
        except ImportError:

            self.dungeon_style = False

    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if previous_hover != self.is_hovered and self.dungeon_style and self.panel:
            if self.is_hovered:

                lighter_border = self._lighten_colour(self.border_colour, BUTTON_HOVER_LIGHTEN)
                self.panel.update_style(True, self.border_width, lighter_border)
            else:

                self.panel.update_style(True, self.border_width, self.border_colour)

        return previous_hover != self.is_hovered

    def _lighten_colour(self, colour, factor=BUTTON_HOVER_LIGHTEN):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))

    def is_clicked(self, mouse_pos):
        is_clicked = self.rect.collidepoint(mouse_pos)
        if is_clicked and self.callback:
            self.callback()
        return is_clicked

    def draw(self, surface):
        if self.dungeon_style and self.panel:

            self.panel.draw(surface)

            if self.is_hovered:

                glow_size = BUTTON_GLOW_SIZE
                glow_surface = pygame.Surface(
                    (self.text_surface.get_width() + glow_size*2,
                        self.text_surface.get_height() + glow_size*2
                    ),
                    pygame.SRCALPHA
                )

                if self.text_colour == WHITE or sum(self.text_colour) > 400:
                    glow_colour = BUTTON_HOVER_GLOW_WHITE
                else:
                    glow_colour = BUTTON_HOVER_GLOW_DARK

                pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
                glow_rect = glow_surface.get_rect(center=self.text_rect.center)
                surface.blit(glow_surface, glow_rect)

            surface.blit(self.text_surface, self.text_rect)
        else:

            pygame.draw.rect(surface, self.bg_colour, self.rect, border_radius=BUTTON_ROUND_CORNER)

            pygame.draw.rect(surface, self.border_colour, self.rect, 2, border_radius=BUTTON_ROUND_CORNER)

            surface.blit(self.text_surface, self.text_rect)