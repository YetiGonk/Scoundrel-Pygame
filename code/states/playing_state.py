import pygame
from pygame.locals import *

from animations.animation_controller import AnimationController

from config import *
from core.game_state import GameState
from core.resource_loader import ResourceLoader

# Import the new classes
from input.game_input_handler import GameInputHandler
from rendering.game_renderer import GameRenderer, UIComponents

# Keep existing imports for managers
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


class PlayingState(GameState):
    """The main gameplay state."""

    def __init__(self, game_manager):
        """Initialise the playing state."""
        super().__init__(game_manager)

        self._initialise_managers()

        self._initialise_state_variables()
        self._initialise_player_state()
        self._initialise_game_components()

        self.input_handler = None
        self.renderer = None
        self.ui_components = None

    def _initialise_managers(self):
        """Initialise all manager and controller classes."""
        self.animation_manager = AnimationManager()
        self.resource_loader = ResourceLoader

        self.card_action_manager = CardActionManager(self)
        self.room_manager = None
        self.animation_controller = AnimationController(self)

        self.player_state_manager = PlayerStateManager(self)
        self.inventory_manager = InventoryManager(self)
        self.ui_renderer = UIRenderer(self)
        self.game_state_controller = GameStateController(self)
        self.ui_factory = UIFactory(self)
        
    def _initialise_room_manager(self):
        session = self._create_session_object()
        
        self.room_manager = RoomManager(
            session,
            self.animation_manager,
            self.animation_controller,
            self.game_manager
        )
        
        self.room_manager.set_playing_state_ref(self)

    def _initialise_state_variables(self):
        """Initialise general state variables."""
        self.is_running = False
        self.ran_last_turn = False
        self.show_debug = False

        self.completed_rooms = 0
        self.floor_completed = False
        self.room_completion_in_progress = False
        self.room_started_in_enter = False

        self.message = None
        
        self.z_index_counter = 0

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

    def enter(self):
        """Initialise the playing state when entering."""
        self._load_resources()
        self._setup_game_components()
        self._setup_player_state()
        
        self._initialise_input_and_rendering()
        self._initialise_room_manager()
        
        self._start_initial_room()
        self._reset_state_tracking()

    def _load_resources(self):
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()

        self.ui_components = UIComponents.load_all(
            self.resource_loader,
            current_floor_type,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            FLOOR_WIDTH,
            FLOOR_HEIGHT
        )

        self.header_font = self.ui_components.header_font
        self.body_font = self.ui_components.body_font
        self.caption_font = self.ui_components.caption_font
        self.normal_font = self.ui_components.normal_font
        self.background = self.ui_components.background
        self.floor = self.ui_components.floor

    def _setup_game_components(self):
        """Initialise deck, discard pile, and room."""
        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()

        if not self.current_floor:
            self.current_floor = "dungeon"

        from entities.deck import Deck, DiscardPile
        from entities.room import Room

        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        if hasattr(self.deck, "initialise_visuals"):
            self.deck.initialise_visuals()

        if hasattr(self.discard_pile, "initialise_visuals"):
            self.discard_pile.initialise_visuals()

        if hasattr(self.inventory_manager, "position_inventory_cards"):
            self.inventory_manager.position_inventory_cards()

        self.ui_factory.create_run_button()

    def _initialise_input_and_rendering(self):
        equipped_weapon_ref = self.equipped_weapon
        
        session = type('Session', (), {
            'player': type('Player', (), {
                'inventory': self.inventory,
                'max_inventory_size': self.MAX_INVENTORY_SIZE,
                'equipped_weapon': self.equipped_weapon.get("node") if "node" in self.equipped_weapon else None,
                'defeated_monsters': self.defeated_monsters,
                'life_points': self.life_points,
                'has_weapon': lambda self: "node" in equipped_weapon_ref
            })(),
            'room': self.room,
            'deck': self.deck,
            'discard_pile': self.discard_pile,
            'ran_last_turn': self.ran_last_turn
        })()

        # Create input handler
        self.input_handler = GameInputHandler(
            session,
            self.card_action_manager,
            self.room_manager,
            self.inventory_manager,
            self.run_button
        )

        # Create status UI
        status_ui = StatusUI(self.game_manager)
        status_ui.update_fonts(self.header_font, self.normal_font)

        # Create renderer
        self.renderer = GameRenderer(
            session,
            self.ui_components,
            self.ui_renderer,
            self.animation_manager,
            self.run_button,
            status_ui
        )

    def _setup_player_state(self):
        """Set up player stats and equipped weapon."""
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]

    def _start_initial_room(self):
        """Start the initial room."""
        self.deck.initialise_deck()

        if self.discard_pile:
            self.discard_pile.cards = []
            if hasattr(self.discard_pile, 'card_stack'):
                self.discard_pile.card_stack = []

        self.room_manager.start_new_room()
        self.room_started_in_enter = True

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

        self.input_handler.handle_event(event, self.animation_manager)

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
        """Handle logic for when the room is empty."""
        if not self.room_completion_in_progress:
            self.room_completion_in_progress = True
            self.completed_rooms += 1

        if len(self.deck.cards) > 0:
            self.game_manager.advance_to_next_room()
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
                next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
                next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
                
                self.game_state_controller.show_message(
                    f"Floor {floor_type.title()} completed! Moving to {next_floor_type.title()}..."
                )

                # Use animation controller (import at top from animations.animation_controller)
                from animations.animation_controller import AnimationController
                anim_controller = AnimationController(self)
                anim_controller.schedule_delayed_animation(
                    3.0,
                    lambda: self.room_manager.transition_to_next_floor()
                )

    def draw(self, surface):
        """
        Draw game elements to the screen - MASSIVELY SIMPLIFIED!
        Now just delegates to the renderer.
        """
        # Update session state (until full GameSession is implemented)
        self._sync_session_state()
        
        # Render everything
        self.renderer.render(surface, self.message)

    def _sync_session_state(self):
        """
        Temporary method to sync state to the session object.
        Will be removed when GameSession is fully implemented.
        """
        session = self.renderer.session
        session.ran_last_turn = self.ran_last_turn
        session.player.life_points = self.life_points
        session.player.inventory = self.inventory
        session.player.defeated_monsters = self.defeated_monsters
        
        # Update equipped weapon
        if "node" in self.equipped_weapon:
            session.player.equipped_weapon = self.equipped_weapon["node"]
        else:
            session.player.equipped_weapon = None

    def change_health(self, amount):
        """Forward health change to player state manager."""
        self.player_state_manager.change_health(amount)

    def position_inventory_cards(self):
        """Forward inventory positioning to inventory manager."""
        self.inventory_manager.position_inventory_cards()

    def animate_card_to_discard(self, card):
        """Forward card discard animation to animation controller."""
        from animations.animation_controller import AnimationController
        anim_controller = AnimationController(self)
        anim_controller.animate_card_to_discard(card)

    def show_message(self, message, duration=2.0):
        """Forward message display to game state controller."""
        self.game_state_controller.show_message(message, duration)

    def _create_session_object(self):
        """Create a session object with current game state."""
        equipped_weapon_ref = self.equipped_weapon
        
        return type('Session', (), {
            'player': type('Player', (), {
                'inventory': self.inventory,
                'max_inventory_size': self.MAX_INVENTORY_SIZE,
                'equipped_weapon': self.equipped_weapon.get("node") if "node" in self.equipped_weapon else None,
                'defeated_monsters': self.defeated_monsters,
                'life_points': self.life_points,
                'has_weapon': lambda self: "node" in equipped_weapon_ref
            })(),
            'room': self.room,
            'deck': self.deck,
            'discard_pile': self.discard_pile,
            'ran_last_turn': self.ran_last_turn,
            'is_running': self.is_running,
            'completed_rooms': self.completed_rooms,
            'floor_completed': self.floor_completed,
            'current_floor': self.current_floor,
            'room_completion_in_progress': self.room_completion_in_progress,
        })()
        
    def animate_card_to_inventory(self, card):
        """Forward card inventory animation to animation controller."""
        self.animation_controller.animate_card_to_inventory(card)

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