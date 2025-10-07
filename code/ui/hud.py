from config import *
from core.resource_loader import ResourceLoader

class HUD:
    """Heads-up display for showing active effects and status."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        self.small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)

        self.active_effects = []

        self.effect_icon_size = EFFECT_ICON_SIZE
        self.effect_spacing = EFFECT_ICON_SPACING
        self.effect_start_pos = EFFECT_START_POSITION

        self.last_particle_time = 0

        self.health_panel = None

    def update_fonts(self, normal_font, small_font=None):
        """Update fonts if they are loaded after initialization."""
        self.normal_font = normal_font
        if small_font:
            self.small_font = small_font

    def add_effect(self, effect_type, duration=None, value=None):
        """Add a new active effect to display."""
        self.active_effects.append({
            'type': effect_type,
            'duration': duration,
            'value': value,
            'start_time': pygame.time.get_ticks()
        })

    def update(self):
        """Update active effects and resource animations."""
        current_time = pygame.time.get_ticks()

        self.active_effects = [effect for effect in self.active_effects if (
            effect['duration'] is None) or
            ((current_time - effect['start_time']) < effect['duration'])
        ]

    def draw(self, surface):
        """Draw the HUD elements."""

        self.draw_active_effects(surface)

        self.draw_health_indicator(surface)

    def draw_active_effects(self, surface):
        """Draw icons for active effects with dungeon styling."""
        try:
            using_panels = True
        except ImportError:
            using_panels = False

        for i, effect in enumerate(self.active_effects):

            x = self.effect_start_pos[0] + i * (self.effect_icon_size + self.effect_spacing)
            y = self.effect_start_pos[1]

            effect_rect = pygame.Rect(x, y, self.effect_icon_size, self.effect_icon_size)

            effect_colour = EFFECT_DEFAULT_COLOUR
            if effect['type'] == 'healing':
                effect_colour = EFFECT_HEALING_COLOUR
                panel_colour = EFFECT_HEALING_PANEL
                border_colour = EFFECT_HEALING_BORDER
                icon_symbol = "+"
            elif effect['type'] == 'damage':
                effect_colour = EFFECT_DAMAGE_COLOUR
                panel_colour = EFFECT_DAMAGE_PANEL
                border_colour = EFFECT_DAMAGE_BORDER
                icon_symbol = "⚔"
            else:
                effect_colour = EFFECT_DEFAULT_COLOUR
                panel_colour = EFFECT_DEFAULT_PANEL
                border_colour = EFFECT_DEFAULT_BORDER
                icon_symbol = "◆"

            if using_panels:

                effect_panel = Panel(
                    (self.effect_icon_size, self.effect_icon_size),
                    (x, y),
                    colour=panel_colour,
                    alpha=PANEL_ALPHA,
                    border_radius=PANEL_BORDER_RADIUS - 2,
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=border_colour
                )
                effect_panel.draw(surface)

                current_time = pygame.time.get_ticks()
                if effect['duration'] is not None:

                    elapsed = (current_time - effect['start_time']) / effect['duration']

                    base, amplitude, frequency = EFFECT_PULSE_TEMPORARY
                    pulse_factor = base + amplitude * math.sin(elapsed * 10 + current_time / frequency)
                else:

                    base, amplitude, frequency = EFFECT_PULSE_PERMANENT
                    pulse_factor = base + amplitude * math.sin(current_time / frequency)

                glow_radius = int(self.effect_icon_size * 0.3 * pulse_factor)
                center_x = x + self.effect_icon_size // 2
                center_y = y + self.effect_icon_size // 2

                for r in range(glow_radius, 0, -1):
                    alpha = max(0, 150 - (glow_radius - r) * 20)
                    pygame.draw.circle(
                        surface, (*effect_colour, alpha),
                        (center_x, center_y), r
                    )

                symbol_font = pygame.font.SysFont(None, int(self.effect_icon_size * 0.6))
                symbol_text = symbol_font.render(icon_symbol, True, WHITE)
                symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
                surface.blit(symbol_text, symbol_rect)
            else:

                pygame.draw.rect(surface, effect_colour, effect_rect)
                pygame.draw.rect(surface, BLACK, effect_rect, 2)

            if effect['value'] is not None:
                value_text = self.normal_font.render(str(effect['value']), True, WHITE)
                value_rect = value_text.get_rect(center=effect_rect.center)

                if using_panels:
                    value_rect.midtop = (x + self.effect_icon_size // 2, y + self.effect_icon_size + 2)

                surface.blit(value_text, value_rect)

            if effect['duration'] is not None:
                remaining = max(0, effect['duration'] - (pygame.time.get_ticks() - effect['start_time']))
                remaining_text = self.small_font.render(f"{remaining//1000}s", True, WHITE)

                if effect['value'] is not None and using_panels:

                    remaining_rect = remaining_text.get_rect(
                        midtop=(
                            x + self.effect_icon_size // 2,
                            y + self.effect_icon_size + value_text.get_height() + 4
                        )
                    )
                else:

                    remaining_rect = remaining_text.get_rect(
                        midbottom=(
                            x + self.effect_icon_size // 2,
                            y + self.effect_icon_size + (10 if using_panels else 0)
                        )
                    )

                if remaining < EFFECT_EXPIRE_THRESHOLD:

                    remaining_text = self.small_font.render(f"{remaining//1000}s", True, (255, 100, 100))

                    pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 100)
                    scaled_size = int(remaining_text.get_width() * pulse), int(remaining_text.get_height() * pulse)
                    if scaled_size[0] > 0 and scaled_size[1] > 0:
                        pulsed_text = pygame.transform.scale(remaining_text, scaled_size)
                        remaining_rect = pulsed_text.get_rect(center=remaining_rect.center)
                        surface.blit(pulsed_text, remaining_rect)
                    else:
                        surface.blit(remaining_text, remaining_rect)
                else:
                    surface.blit(remaining_text, remaining_rect)

    def draw_health_indicator(self, surface):
        """Draw a health bar indicator with dungeon styling."""
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return

        bar_width = HEALTH_BAR_WIDTH
        bar_height = HEALTH_BAR_HEIGHT
        x, y = HEALTH_BAR_POSITION

        if not self.health_panel:
            try:

                self.health_panel = Panel(
                    (bar_width, bar_height),
                    (x, y),
                    colour=PANEL_HEALTH,
                    alpha=PANEL_ALPHA + 10,
                    border_radius=PANEL_BORDER_RADIUS,
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=PANEL_HEALTH_BORDER
                )
            except ImportError:

                self.health_panel = None

        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int((bar_width - 10) * health_percent)

        if health_percent > 0.7:
            health_colour = HEALTH_COLOUR_GOOD
            glow_colour = HEALTH_GLOW_GOOD
        elif health_percent > 0.3:
            health_colour = HEALTH_COLOUR_WARNING
            glow_colour = HEALTH_GLOW_WARNING
        else:
            health_colour = HEALTH_COLOUR_DANGER
            glow_colour = HEALTH_GLOW_DANGER

        if self.health_panel:
            self.health_panel.draw(surface)

            health_rect = pygame.Rect(x + 5, y + 5, health_width, bar_height - 10)

            glow_surface = pygame.Surface((health_width + 10, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface, glow_colour,
                (5, 0, health_width, bar_height - 10), border_radius=4
            )
            surface.blit(glow_surface, (x, y))

            pygame.draw.rect(surface, health_colour, health_rect, border_radius=4)

            if health_width > 4:
                highlight_colour = self._lighten_colour(health_colour, 0.3)
                pygame.draw.rect(
                    surface, highlight_colour,
                    (x + 5, y + 5, health_width, 2), border_radius=2
                )
        else:

            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)

            health_rect = pygame.Rect(x, y, health_width, bar_height)
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)

        text_colour = WHITE
        health_text = self.normal_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, text_colour)
        health_text_rect = health_text.get_rect(center=(x + bar_width//2, y + bar_height//2))
        surface.blit(health_text, health_text_rect)

    def _lighten_colour(self, colour, factor=0.3):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))