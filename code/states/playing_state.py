import pygame
from pygame.locals import *

from animations.animation_controller import AnimationController

from config import *

from core.game_state import GameState
from core.resource_loader import ResourceLoader

from entities.card import Card
from entities.deck import Deck, DiscardPile
from entities.room import Room

from managers.animation_manager import AnimationManager
from managers.card_action_manager import CardActionManager
from managers.inventory_manager import InventoryManager
from managers.player_state_manager import PlayerStateManager
from managers.room_manager import RoomManager
from managers.game_state_controller import GameStateController

from ui.ui_factory import UIFactory
from ui.ui_renderer import UIRenderer
from ui.status_ui import StatusUI
from ui.hud import HUD
from ui.panel import Panel

class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""

    def __init__(self, game_manager):
        """Initialise the playing state."""
        super().__init__(game_manager)

        self._initialise_managers()

        self._initialise_state_variables()

        self._initialise_player_state()

        self._initialise_game_components()

        self._initialise_ui_elements()

    def _initialise_managers(self):
        """Initialise all manager and controller classes."""

        self.animation_manager = AnimationManager()

        self.resource_loader = ResourceLoader

        self.card_action_manager = CardActionManager(self)
        self.room_manager = RoomManager(self)
        self.animation_controller = AnimationController(self)
        self.player_state_manager = PlayerStateManager(self)
        self.inventory_manager = InventoryManager(self)
        self.ui_renderer = UIRenderer(self)
        self.game_state_controller = GameStateController(self)
        self.ui_factory = UIFactory(self)

    def _initialise_state_variables(self):
        """Initialise general state variables."""

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_GRAY = LIGHT_GRAY

        self.is_running = False
        self.ran_last_turn = False
        self.show_debug = False
        self.z_index_counter = 0

        self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        self.floor_completed = False
        self.room_completion_in_progress = False
        self.room_started_in_enter = False

        self.message = None

    def _initialise_player_state(self):
        """Initialise player stats and inventory."""

        self.life_points = 20
        self.max_life = 20
        self.equipped_weapon = {}
        self.defeated_monsters = []

        self.inventory = []
        self.MAX_INVENTORY_SIZE = 2

    def _initialise_game_components(self):
        """Initialise game components like deck, discard pile, room."""
        self.deck = None
        self.discard_pile = None
        self.room = None
        self.current_floor = None

    def _initialise_ui_elements(self):
        """Initialise UI elements and resources."""
        self.header_font = None
        self.body_font = None
        self.caption_font = None
        self.normal_font = None
        self.run_button = None
        self.background = None
        self.floor = None

        self.status_ui = StatusUI(self.game_manager)
        self.hud = HUD(self.game_manager)

    def enter(self):
        """Initialise the playing state when entering."""

        self._load_resources()

        self._setup_game_components()

        self._setup_player_state()

        self._start_initial_room()

        self._reset_state_tracking()

    def _load_resources(self):
        """Load fonts, background and floor image."""

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.caption_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()

        floor_image = f"floors/{current_floor_type}_floor.png"

        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:

            self.floor = ResourceLoader.load_image("floor.png")

        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

    def _setup_game_components(self):
        """Initialise deck, discard pile, and room."""

        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()

        if not self.current_floor:
            self.current_floor = "dungeon"

        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        if hasattr(self.deck, "initialise_visuals"):
            self.deck.initialise_visuals()

        if hasattr(self.discard_pile, "initialise_visuals"):
            self.discard_pile.initialise_visuals()

        if hasattr(self, "inventory_manager") and hasattr(self.inventory_manager, "position_inventory_cards"):
            self.inventory_manager.position_inventory_cards()

        self.ui_factory.create_run_button()

    def _setup_player_state(self):
        """Set up player stats and equipped weapon."""

        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]

    def _start_initial_room(self):
        """Start the initial room either with a card from fresh."""

        self.deck.initialise_deck()

        if self.discard_pile:
            self.discard_pile.cards = []
            if hasattr(self.discard_pile, 'card_stack'):
                self.discard_pile.card_stack = []

        self.room_manager.start_new_room()

        self.room_started_in_enter = True

        self.status_ui.update_fonts(self.header_font, self.normal_font)

        self.hud.update_fonts(self.normal_font, self.normal_font)

    def _reset_state_tracking(self):
        """Reset game state tracking variables."""

        self.floor_completed = False

        if self.game_manager.floor_manager.current_room == 1:
            self.completed_rooms = 0

    def exit(self):
        """Save state when exiting playing state."""

        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life

    def handle_event(self, event):
        """Handle player input events."""
        if self.animation_manager.is_animating():
            return

        if event.type == MOUSEMOTION:
            self._handle_hover(event)

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event)

    def _handle_hover(self, event):
        """Handle mouse hover events over cards and buttons."""

        inventory_is_full = len(self.inventory) >= self.MAX_INVENTORY_SIZE

        all_hoverable_cards = []

        for card in self.room.cards:

            if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
                card.weapon_available = bool(self.equipped_weapon)

                if self.equipped_weapon and self.defeated_monsters:
                    card.weapon_attack_not_viable = card.value >= self.defeated_monsters[-1].value
                else:
                    card.weapon_attack_not_viable = False

            if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
                card.inventory_available = not inventory_is_full

            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)

        for card in self.inventory:

            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)

        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]

            weapon_card.is_hovered = False
            if weapon_card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(weapon_card)

        for monster in self.defeated_monsters:

            monster.is_hovered = False
            if monster.rect.collidepoint(event.pos):
                all_hoverable_cards.append(monster)

        if all_hoverable_cards:
            closest_card = self._find_closest_card(event.pos, all_hoverable_cards)

            if closest_card:
                closest_card.check_hover(event.pos)

        self.run_button.check_hover(event.pos)

    def _find_closest_card(self, pos, cards):
        """Find the card closest to the given position."""
        if not cards:
            return None

        closest_card = None
        closest_distance = float('inf')

        for card in cards:

            card_center_x = card.rect.centerx
            card_center_y = card.rect.centery

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            card_center_y -= total_float_offset

            dist_sq = (pos[0] - card_center_x) ** 2 + (pos[1] - card_center_y) ** 2

            if dist_sq < closest_distance:
                closest_distance = dist_sq
                closest_card = card

        return closest_card

    def _handle_click(self, event):
        """Handle mouse click events."""
        if self.life_points <= 0:
            return

        if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
            self.room_manager.run_from_room()
            return

        clicked_card = None

        card = self.room.get_card_at_position(event.pos)
        if card:
            self.card_action_manager.resolve_card(card, event_pos=event.pos)
            return

        clicked_inventory_card = self.inventory_manager.get_inventory_card_at_position(event.pos)
        if clicked_inventory_card:
            self.card_action_manager.use_inventory_card(clicked_inventory_card, event.pos)
            return

        if "node" in self.equipped_weapon and self.equipped_weapon["node"].rect.collidepoint(event.pos):
            self.card_action_manager.discard_equipped_weapon()

    def update(self, delta_time):
        """Update game state for this frame."""

        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()

        animations_just_finished = previous_animating and not current_animating

        self._update_message(delta_time)
        self._update_cards(delta_time)

        if not current_animating:
            self._process_game_state(animations_just_finished)

        self.game_state_controller.check_game_over()

    def _update_message(self, delta_time):
        """Update any active message fade animation."""
        if hasattr(self, 'message') and self.message and 'alpha' in self.message:

            if self.message['fade_in']:

                self.message['alpha'] = min(255, self.message['alpha'] + self.message['fade_speed'] * delta_time)

                if self.message['alpha'] >= 255:
                    self.message['fade_in'] = False
            else:

                self.message['time_remaining'] -= delta_time

                if self.message['time_remaining'] <= 0:
                    self.message['alpha'] = max(0, self.message['alpha'] - self.message['fade_speed'] * delta_time)

                    if self.message['alpha'] <= 0:
                        self.message = None

    def _update_cards(self, delta_time):
        """Update all card animations."""

        for card in self.room.cards:

            card.update(delta_time)

            if card.is_flipping:
                card.update_flip(delta_time)

        for card in self.inventory:
            card.update(delta_time)
            if card.is_flipping:
                card.update_flip(delta_time)

        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].update(delta_time)

        for monster in self.defeated_monsters:
            monster.update(delta_time)

    def _process_game_state(self, animations_just_finished):
        """Process game state changes after animations."""
        if self.is_running:
            self.room_manager.on_run_completed()
            return

        if self.room_started_in_enter:
            self.room_started_in_enter = False
            return

        if len(self.room.cards) == 0:
            self._handle_empty_room()

        elif len(self.room.cards) == 1 and animations_just_finished and len(self.deck.cards) > 0:
            self._handle_single_card_room()

    def _handle_empty_room(self):
        """Handle logic for when the room is empty (all cards processed)."""
        if not self.room_completion_in_progress:
            self.room_completion_in_progress = True
            self.completed_rooms += 1

        if len(self.deck.cards) > 0:
            self.game_manager.advance_to_next_room()

            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()

            if self.game_manager.current_state == self:
                self.room_manager.start_new_room()
        else:
            self._handle_floor_completion()

    def _handle_single_card_room(self):
        """Handle logic for rooms with a single card remaining."""
        if not self.room_completion_in_progress:

            self.room_completion_in_progress = True

            self.completed_rooms += 1

            self.game_manager.advance_to_next_room()

            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()

        self.room_manager.start_new_room(self.room.cards[0])

    def _handle_floor_completion(self):
        """Handle logic for when the floor is completed."""
        if not self.floor_completed:
            self.floor_completed = True

            if self.game_manager.floor_manager.current_floor_index >= len(self.game_manager.floor_manager.floors) - 1:

                self.game_manager.game_data["victory"] = True
                self.game_manager.game_data["run_complete"] = True
                self.game_manager.change_state("game_over")
            else:

                floor_type = self.game_manager.floor_manager.get_current_floor()
                if "'" in floor_type:
                    b = []
                    for temp in floor_type.split():
                        b.append(temp.capitalize())
                    floor_type = " ".join(b)
                else:
                    floor_type = floor_type.title()
                next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
                next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
                if "'" in next_floor_type:
                    b = []
                    for temp in next_floor_type.split():
                        b.append(temp.capitalize())
                    next_floor_type = " ".join(b)
                else:
                    next_floor_type = next_floor_type.title()
                self.game_state_controller.show_message(f"Floor {floor_type} completed! Moving to {next_floor_type}...")

                self.animation_controller.schedule_delayed_animation(
                    3.0,
                    lambda: self.room_manager.transition_to_next_floor()
                )

    def draw(self, surface):
        """Draw game elements to the screen."""

        self._draw_background(surface)

        self._draw_cards_and_piles(surface)

        self._draw_inventory(surface)

        self._draw_ui_elements(surface)

    def _draw_background(self, surface):
        """Draw background and floor."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))

    def _draw_cards_and_piles(self, surface):
        """Draw deck, discard pile, equipped weapon, and defeated monsters."""

        self.deck.draw(surface)

        self.discard_pile.draw(surface)

        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]

            weapon_is_hovered = weapon_card.is_hovered and weapon_card.face_up

            weapon_card.draw(surface)

            hovered_monsters = []
            non_hovered_monsters = []

            for monster in self.defeated_monsters:
                if monster.is_hovered and monster.face_up:
                    hovered_monsters.append(monster)
                else:
                    non_hovered_monsters.append(monster)

            for monster in non_hovered_monsters:
                monster.draw(surface)

            for monster in hovered_monsters:

                monster.draw(surface)

    def _draw_inventory(self, surface):
        """Draw inventory panel and cards."""
        vertical_center = SCREEN_HEIGHT // 2

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        if not hasattr(self, 'inventory_panel'):

            parchment_colour = (60, 45, 35)
            self.inventory_panel = Panel(
                (inv_width, inv_height),
                (inv_x, inv_y),
                colour=parchment_colour,
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)
            )

        self.inventory_panel.draw(surface)

        inv_rect = self.inventory_panel.rect

        inv_title = self.body_font.render("Inventory", True, WHITE)

        glow_surface = pygame.Surface((inv_title.get_width() + 10, inv_title.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (255, 240, 200, 50)
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())

        glow_rect = glow_surface.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 35)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)

        surface.blit(glow_surface, glow_rect)
        surface.blit(inv_title, title_rect)

        sorted_cards = sorted(self.inventory, key=lambda c: 1 if c.is_hovered else 0)

        for card in sorted_cards:
            self.ui_renderer._draw_card_shadow(surface, card)

        for card in sorted_cards:

            card.draw(surface)

            if card.face_up and card.is_hovered:

                type_text = ""
                if card.type == "weapon" and hasattr(card, 'weapon_type') and card.weapon_type:
                    weapon_type = card.weapon_type.upper()

                    if hasattr(card, 'damage_type') and card.damage_type:
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                elif card.type == "potion":
                    type_text = "HEALING"

    def _draw_ui_elements(self, surface):
        """Draw room cards, UI elements, and status displays."""

        self.room.draw(surface)

        self.animation_manager.draw_effects(surface)

        for card in self.inventory:
            if card.is_hovered and card.face_up:
                card.draw_hover_text(surface)

        if "node" in self.equipped_weapon and self.equipped_weapon["node"].is_hovered and self.equipped_weapon["node"].face_up:
            self.equipped_weapon["node"].draw_hover_text(surface)

        for monster in self.defeated_monsters:
            monster.is_defeated = True

        for monster in self.defeated_monsters:
            if monster.is_hovered and monster.face_up:
                monster.draw_hover_text(surface)

        self.ui_renderer.draw_health_display(surface)

        self.ui_renderer.draw_deck_count(surface)

        self.animation_manager.draw_ui_effects(surface)

        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:

            button_rect = self.run_button.rect

            pygame.draw.rect(surface, LIGHT_GRAY, button_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=5)

            button_text = self.body_font.render("RUN", True, (150, 150, 150))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)

        self._draw_message(surface)

        self.status_ui.draw(surface)

    def _draw_message(self, surface):
        """Draw any active message with fade effect."""
        if hasattr(self, 'message') and self.message:

            if "alpha" in self.message:

                current_alpha = self.message["alpha"]
                text_with_alpha = self.message["text"].copy()
                text_with_alpha.set_alpha(current_alpha)

                bg_surface = pygame.Surface((self.message["bg_rect"].width, self.message["bg_rect"].height), pygame.SRCALPHA)
                bg_colour = (0, 0, 0, int(current_alpha * 0.7))
                pygame.draw.rect(bg_surface, bg_colour, bg_surface.get_rect(), border_radius=8)

                border_colour = (200, 200, 200, int(current_alpha * 0.5))
                pygame.draw.rect(bg_surface, border_colour, bg_surface.get_rect(), 1, border_radius=8)

                surface.blit(bg_surface, self.message["bg_rect"])
                surface.blit(text_with_alpha, self.message["rect"])
            else:

                pygame.draw.rect(surface, BLACK, self.message["bg_rect"], border_radius=8)
                pygame.draw.rect(surface, WHITE, self.message["bg_rect"], 2, border_radius=8)
                surface.blit(self.message["text"], self.message["rect"])

    def change_health(self, amount):
        """Forward health change to player state manager."""
        self.player_state_manager.change_health(amount)

    def position_inventory_cards(self):
        """Forward inventory positioning to inventory manager."""
        self.inventory_manager.position_inventory_cards()

    def animate_card_to_discard(self, card):
        """Forward card discard animation to animation controller."""
        self.animation_controller.animate_card_to_discard(card)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, on_complete=None):
        """Forward card movement animation to animation controller."""
        self.animation_controller.animate_card_movement(card, target_pos, duration, easing, on_complete)

    def schedule_delayed_animation(self, delay, callback):
        """Forward delayed animation to animation controller."""
        self.animation_controller.schedule_delayed_animation(delay, callback)

    def start_card_flip(self, card):
        """Forward card flip to animation controller."""
        self.animation_controller.start_card_flip(card)

    def position_monster_stack(self):
        """Forward monster stack positioning to animation controller."""
        self.animation_controller.position_monster_stack()

    def animate_card_to_inventory(self, card):
        """Forward card inventory animation to animation controller."""
        self.animation_controller.animate_card_to_inventory(card)

    def show_message(self, message, duration=2.0):
        """Forward message display to game state controller."""
        self.game_state_controller.show_message(message, duration)

def replace_colour(image_path, old_colour, new_colour):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        if item == old_colour:
            new_data.append(new_colour)
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(image_path)
