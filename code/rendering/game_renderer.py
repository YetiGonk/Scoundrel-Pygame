"""
rendering/game_renderer.py

Handles all rendering for the playing state.
Separates drawing logic from game state and input handling.
"""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    FLOOR_WIDTH, FLOOR_HEIGHT,
    INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT,
    INVENTORY_PANEL_X, INVENTORY_PANEL_Y,
    WHITE, BLACK, LIGHT_GRAY
)
from ui.panel import Panel


class GameRenderer:
    """
    Responsible for rendering all game elements to the screen.
    Handles drawing order, layering, and visual effects.
    """

    def __init__(self, session, ui_components, ui_renderer, animation_manager, run_button, status_ui):
        """
        Initialize the game renderer.

        Args:
            session: GameSession containing all game state
            ui_components: UIComponents with fonts and images
            ui_renderer: UIRenderer for specialized UI drawing
            animation_manager: AnimationManager for effects
            run_button: Run button UI element
            status_ui: Status UI for displaying game progress
        """
        self.session = session
        self.ui = ui_components
        self.ui_renderer = ui_renderer
        self.animation_manager = animation_manager
        self.run_button = run_button
        self.status_ui = status_ui

        # Create inventory panel (lazy init in original code)
        self.inventory_panel = None
        self._init_inventory_panel()

    def _init_inventory_panel(self):
        """Create the inventory panel with dungeon styling."""
        parchment_colour = (60, 45, 35)
        self.inventory_panel = Panel(
            (INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT),
            (INVENTORY_PANEL_X, INVENTORY_PANEL_Y),
            colour=parchment_colour,
            alpha=230,
            border_radius=8,
            dungeon_style=True,
            border_width=3,
            border_colour=(95, 75, 45)
        )

    def render(self, surface, message=None):
        """
        Main render method - draws all game elements in correct order.

        Args:
            surface: pygame Surface to draw on
            message: Optional message to display (dict with text, rect, etc.)
        """
        self._draw_background(surface)
        self._draw_game_board(surface)
        self._draw_inventory(surface)
        self._draw_ui_overlay(surface, message)

    def _draw_background(self, surface):
        """
        Draw the background and floor images.

        Args:
            surface: pygame Surface to draw on
        """
        # Draw full background
        surface.blit(self.ui.background, (0, 0))

        # Center the floor image
        floor_x = (SCREEN_WIDTH - self.ui.floor.get_width()) / 2
        floor_y = (SCREEN_HEIGHT - self.ui.floor.get_height()) / 2
        surface.blit(self.ui.floor, (floor_x, floor_y))

    def _draw_game_board(self, surface):
        """
        Draw the main game board: deck, discard pile, equipped weapon, defeated monsters.

        Args:
            surface: pygame Surface to draw on
        """
        # Draw deck and discard pile
        self.session.deck.draw(surface)
        self.session.discard_pile.draw(surface)

        # Draw equipped weapon and defeated monsters with proper layering
        if self.session.has_weapon():
            self._draw_weapon_and_monsters(surface)

    def _draw_weapon_and_monsters(self, surface):
        """
        Draw equipped weapon and defeated monsters with proper z-ordering.
        Hovered monsters are drawn on top.

        Args:
            surface: pygame Surface to draw on
        """
        weapon_card = self.session.equipped_weapon

        # Draw weapon
        weapon_card.draw(surface)

        # Separate monsters by hover state for proper layering
        hovered_monsters = []
        non_hovered_monsters = []

        for monster in self.session.defeated_monsters:
            if monster.is_hovered and monster.face_up:
                hovered_monsters.append(monster)
            else:
                non_hovered_monsters.append(monster)

        # Draw non-hovered monsters first
        for monster in non_hovered_monsters:
            monster.draw(surface)

        # Draw hovered monsters on top
        for monster in hovered_monsters:
            monster.draw(surface)

    def _draw_inventory(self, surface):
        """
        Draw the inventory panel, title, and inventory cards.

        Args:
            surface: pygame Surface to draw on
        """
        # Draw inventory panel background
        self.inventory_panel.draw(surface)

        # Draw inventory title with glow effect
        self._draw_inventory_title(surface)

        # Draw inventory cards with shadows and proper layering
        self._draw_inventory_cards(surface)

    def _draw_inventory_title(self, surface):
        """
        Draw the "Inventory" title with a glowing effect.

        Args:
            surface: pygame Surface to draw on
        """
        inv_rect = self.inventory_panel.rect
        inv_title = self.ui.body_font.render("Inventory", True, WHITE)

        # Create glow effect
        glow_surface = pygame.Surface(
            (inv_title.get_width() + 10, inv_title.get_height() + 10),
            pygame.SRCALPHA
        )
        glow_colour = (255, 240, 200, 50)
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())

        # Position title above panel
        glow_rect = glow_surface.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 35)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)

        # Draw glow then title
        surface.blit(glow_surface, glow_rect)
        surface.blit(inv_title, title_rect)

    def _draw_inventory_cards(self, surface):
        """
        Draw all inventory cards with shadows.
        Hovered cards are drawn last (on top).

        Args:
            surface: pygame Surface to draw on
        """
        # Sort so hovered cards are drawn last
        sorted_cards = sorted(
            self.session.inventory,
            key=lambda c: 1 if c.is_hovered else 0
        )

        # Draw shadows first
        for card in sorted_cards:
            self.ui_renderer._draw_card_shadow(surface, card)

        # Draw cards
        for card in sorted_cards:
            card.draw(surface)

    def _draw_ui_overlay(self, surface, message=None):
        """
        Draw all UI elements that appear on top of the game board.

        Args:
            surface: pygame Surface to draw on
            message: Optional message to display
        """
        # Draw room cards
        self.session.room.draw(surface)

        # Draw animation effects (particles, etc.)
        self.animation_manager.draw_effects(surface)

        # Draw hover text for interactive elements
        self._draw_hover_tooltips(surface)

        # Draw health display and deck count
        self.ui_renderer.draw_health_display(surface)
        self.ui_renderer.draw_deck_count(surface)

        # Draw UI-layer animation effects
        self.animation_manager.draw_ui_effects(surface)

        # Draw run button
        self._draw_run_button(surface)

        # Draw message if present
        if message:
            self._draw_message(surface, message)

        # Draw status UI (progress indicators, etc.)
        self.status_ui.draw(surface)

    def _draw_hover_tooltips(self, surface):
        """
        Draw hover text for all interactive elements that are currently hovered.

        Args:
            surface: pygame Surface to draw on
        """
        # Draw inventory card tooltips
        for card in self.session.inventory:
            if card.is_hovered and card.face_up:
                card.draw_hover_text(surface)

        # Draw weapon tooltip
        if self.session.has_weapon():
            weapon = self.session.equipped_weapon
            if weapon.is_hovered and weapon.face_up:
                weapon.draw_hover_text(surface)

        # Draw defeated monster tooltips
        for monster in self.session.defeated_monsters:
            # Mark as defeated for proper display
            monster.is_defeated = True

            if monster.is_hovered and monster.face_up:
                monster.draw_hover_text(surface)

    def _draw_run_button(self, surface):
        """
        Draw the run button (active or disabled).

        Args:
            surface: pygame Surface to draw on
        """
        can_run = (
            not self.session.ran_last_turn and
            len(self.session.room.cards) == 4 and
            not self.animation_manager.is_animating()
        )

        if can_run:
            # Draw active button
            self.run_button.draw(surface)
        else:
            # Draw disabled button
            self._draw_disabled_run_button(surface)

    def _draw_disabled_run_button(self, surface):
        """
        Draw the run button in a disabled state.

        Args:
            surface: pygame Surface to draw on
        """
        button_rect = self.run_button.rect

        # Draw grayed out button
        pygame.draw.rect(surface, LIGHT_GRAY, button_rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=5)

        # Draw grayed out text
        button_text = self.ui.body_font.render("RUN", True, (150, 150, 150))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        surface.blit(button_text, button_text_rect)

    def _draw_message(self, surface, message):
        """
        Draw a message with fade effect if applicable.

        Args:
            surface: pygame Surface to draw on
            message: Dict containing message data (text, rect, alpha, etc.)
        """
        if "alpha" in message:
            # Draw message with fade animation
            self._draw_fading_message(surface, message)
        else:
            # Draw message without fade
            self._draw_static_message(surface, message)

    def _draw_fading_message(self, surface, message):
        """
        Draw a message with alpha fade effect.

        Args:
            surface: pygame Surface to draw on
            message: Dict with text, rect, bg_rect, and alpha
        """
        current_alpha = message["alpha"]

        # Create text surface with alpha
        text_with_alpha = message["text"].copy()
        text_with_alpha.set_alpha(current_alpha)

        # Create background with alpha
        bg_surface = pygame.Surface(
            (message["bg_rect"].width, message["bg_rect"].height),
            pygame.SRCALPHA
        )
        bg_colour = (0, 0, 0, int(current_alpha * 0.7))
        pygame.draw.rect(bg_surface, bg_colour, bg_surface.get_rect(), border_radius=8)

        # Add border
        border_colour = (200, 200, 200, int(current_alpha * 0.5))
        pygame.draw.rect(bg_surface, border_colour, bg_surface.get_rect(), 1, border_radius=8)

        # Draw background and text
        surface.blit(bg_surface, message["bg_rect"])
        surface.blit(text_with_alpha, message["rect"])

    def _draw_static_message(self, surface, message):
        """
        Draw a message without fade effect.

        Args:
            surface: pygame Surface to draw on
            message: Dict with text and rect
        """
        # Draw background
        pygame.draw.rect(surface, BLACK, message["bg_rect"], border_radius=8)
        pygame.draw.rect(surface, WHITE, message["bg_rect"], 2, border_radius=8)

        # Draw text
        surface.blit(message["text"], message["rect"])


class UIComponents:
    """
    Container for UI resources like fonts and images.
    Handles loading and provides clean access.
    """

    def __init__(self, fonts, images):
        """
        Initialize UI components.

        Args:
            fonts: Dict of loaded fonts
            images: Dict of loaded images
        """
        self.title_font = fonts['title']
        self.header_font = fonts['header']
        self.body_font = fonts['body']
        self.caption_font = fonts['caption']
        self.normal_font = fonts['normal']

        self.background = images['background']
        self.floor = images['floor']

    @staticmethod
    def load_all(resource_loader, floor_type, screen_width, screen_height, floor_width, floor_height):
        """
        Load all UI resources from disk.

        Args:
            resource_loader: ResourceLoader class
            floor_type: Current floor type for floor image
            screen_width: Screen width for scaling
            screen_height: Screen height for scaling
            floor_width: Floor image target width
            floor_height: Floor image target height

        Returns:
            UIComponents instance with loaded resources
        """
        # Load fonts
        fonts = {
            'title': resource_loader.load_font("fonts/Pixel Times.ttf", 60),
            'header': resource_loader.load_font("fonts/Pixel Times.ttf", 36),
            'body': resource_loader.load_font("fonts/Pixel Times.ttf", 28),
            'caption': resource_loader.load_font("fonts/Pixel Times.ttf", 24),
            'normal': resource_loader.load_font("fonts/Pixel Times.ttf", 20),
        }

        # Load and scale background
        background = resource_loader.load_image("bg.png")
        if background.get_width() != screen_width or background.get_height() != screen_height:
            background = pygame.transform.scale(background, (screen_width, screen_height))

        # Load and scale floor image
        floor_image_path = f"floors/{floor_type}_floor.png"
        try:
            floor = resource_loader.load_image(floor_image_path)
        except:
            # Fallback to default floor
            floor = resource_loader.load_image("floor.png")

        floor = pygame.transform.scale(floor, (floor_width, floor_height))

        images = {
            'background': background,
            'floor': floor
        }

        return UIComponents(fonts, images)