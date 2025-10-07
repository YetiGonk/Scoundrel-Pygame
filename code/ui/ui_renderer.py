import pygame
import random

from config import *

from ui.panel import Panel

class UIRenderer:
    """Handles rendering of UI elements and game objects."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""

        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y
        health_bar_width = 140
        health_bar_height = 40

        if not hasattr(self, 'health_panel'):
            panel_rect = pygame.Rect(
                health_display_x - 10,
                health_display_y - health_bar_height - 20,
                health_bar_width + 20,
                health_bar_height + 20
            )

            self.health_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)
            )

        self.health_panel.draw(surface)

        bar_bg_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            health_bar_height
        )

        stone_bg = pygame.Surface((bar_bg_rect.width, bar_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(stone_bg, (50, 50, 55), pygame.Rect(0, 0, bar_bg_rect.width, bar_bg_rect.height), border_radius=5)

        for x in range(0, bar_bg_rect.width, 3):
            for y in range(0, bar_bg_rect.height, 3):

                noise = random.randint(0, 25)
                stone_colour = (50 + noise, 50 + noise, 55 + noise, 255)
                pygame.draw.rect(stone_bg, stone_colour, (x, y, 3, 3))

        surface.blit(stone_bg, bar_bg_rect.topleft)

        health_percent = self.playing_state.life_points / self.playing_state.max_life
        health_width = int(health_bar_width * health_percent)

        if health_percent > 0.7:
            health_colour = (50, 220, 100)
            glow_colour = (100, 255, 150, 40)
        elif health_percent > 0.3:
            health_colour = (255, 155, 20)
            glow_colour = (255, 180, 50, 40)
        else:
            health_colour = (255, 30, 30)
            glow_colour = (255, 70, 70, 40)

        if health_width > 0:
            health_rect = pygame.Rect(
                health_display_x,
                health_display_y - health_bar_height - 10,
                health_width,
                health_bar_height
            )

            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)

            glow_surf = pygame.Surface((health_width, health_bar_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_colour, pygame.Rect(0, 0, health_width, health_bar_height), border_radius=5)

            surface.blit(glow_surf, health_rect.topleft)

        shadow_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            8
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        surface.blit(shadow_surface, shadow_rect)

        if health_width > 0:
            highlight_rect = pygame.Rect(
                health_display_x,
                health_display_y - 18,
                health_width,
                8
            )
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, 60))
            surface.blit(highlight_surface, highlight_rect)

        health_text = self.playing_state.body_font.render(f"{self.playing_state.life_points}/{self.playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)

        glow_surf = pygame.Surface((health_text.get_width() + 10, health_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 255, 255, 30), glow_surf.get_rect())
        glow_rect = glow_surf.get_rect(center=health_text_rect.center)

        surface.blit(glow_surf, glow_rect)
        surface.blit(health_text, health_text_rect)

    def draw_deck_count(self, surface):
        """Draw deck card counter display with current and total cards."""

        count_panel_width = 80
        count_panel_height = 40
        count_panel_x = 87 + CARD_WIDTH//2 - count_panel_width//2
        count_panel_y = 35 + (len(self.playing_state.deck.cards)-1)*3 + CARD_HEIGHT//2 - count_panel_height//2

        if not hasattr(self, 'count_panel'):
            panel_rect = pygame.Rect(
                count_panel_x,
                count_panel_y,
                count_panel_width,
                count_panel_height
            )

            self.count_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)
            )
        else:

            self.count_panel.rect.topleft = (count_panel_x, count_panel_y)

        self.count_panel.draw(surface)

        count_text = self.playing_state.caption_font.render(f"{len(self.playing_state.deck.cards)}/{DECK_TOTAL_COUNT}", True, WHITE)
        count_text_rect = count_text.get_rect(center=self.count_panel.rect.center)
        surface.blit(count_text, count_text_rect)

    def _draw_card_shadow(self, surface, card):
        """Draw shadow effect for a card"""
        shadow_alpha = 60
        shadow_width = 4
        shadow_rect = card.rect.inflate(shadow_width * 2, shadow_width * 2)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=3)
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))