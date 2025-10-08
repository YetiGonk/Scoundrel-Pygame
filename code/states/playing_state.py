"""
states/playing_state.py - CLEAN VERSION

PlayingState is now just a coordinator. All state lives in GameSession.
No more scattered state, no more sync methods, no more madness!
"""

import pygame
from config import *
from core.game_state import GameState
from core.resource_loader import ResourceLoader
from core.game_session import GameSession

# Managers
from managers.animation_manager import AnimationManager
from managers.card_action_manager import CardActionManager
from managers.inventory_manager import InventoryManager
from managers.room_manager import RoomManager
from managers.player_state_manager import PlayerStateManager
from managers.game_state_controller import GameStateController

from animations.animation_controller import AnimationController

# UI
from ui.ui_factory import UIFactory
from ui.ui_renderer import UIRenderer
from ui.status_ui import StatusUI

# Rendering
from rendering.game_renderer import GameRenderer, UIComponents

# Input
from input.game_input_handler import GameInputHandler


class PlayingState(GameState):
    """
    The main gameplay state.
    Now CLEAN - just coordinates subsystems, all state in GameSession.
    """

    def __init__(self, game_manager):
        """Initialize the playing state."""
        super().__init__(game_manager)
        
        # Game session - THE ONLY PLACE STATE LIVES
        self.session = None
        
        # Managers
        self.animation_manager = AnimationManager()
        self.animation_controller = AnimationController(self)
        self.card_action_manager = CardActionManager(self)
        self.room_manager = RoomManager(self)
        self.inventory_manager = InventoryManager(self)
        self.player_state_manager = PlayerStateManager(self)
        self.game_state_controller = GameStateController(self)
        
        # UI
        self.ui_factory = UIFactory(self)
        self.ui_renderer = UIRenderer(self)
        self.status_ui = None
        self.run_button = None
        
        # Rendering
        self.ui_components = None
        self.renderer = None
        self.input_handler = None
        
        # Message display (could move to session too)
        self.message = None
        
        # Temporary flags (TODO: move to session or remove)
        self.room_started_in_enter = False

    def enter(self):
        """Initialize when entering the playing state."""
        # Create/reset game session
        floor_type = self.game_manager.floor_manager.get_current_floor()
        self.session = GameSession(floor_type)
        
        # Load player state from save data
        self.session.load_from_dict(self.game_manager.game_data)
        
        # Load resources
        self._load_resources()
        
        # Initialize game components
        self._setup_game_components()
        
        # Initialize subsystems
        self._setup_subsystems()
        
        # Start first room
        self._start_initial_room()

    def _load_resources(self):
        """Load fonts and images."""
        self.ui_components = UIComponents.load_all(
            ResourceLoader,
            self.session.current_floor,
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
        """Initialize deck, room, etc."""
        # Initialize deck
        if hasattr(self.session.deck, "initialise_deck"):
            self.session.deck.initialise_deck()
        
        if hasattr(self.session.deck, "initialise_visuals"):
            self.session.deck.initialise_visuals()
        
        if hasattr(self.session.discard_pile, "initialise_visuals"):
            self.session.discard_pile.initialise_visuals()
        
        # Create run button
        self.ui_factory.create_run_button()

    def _setup_subsystems(self):
        """Initialize renderer, input handler, etc."""
        # Status UI
        self.status_ui = StatusUI(self.game_manager)
        self.status_ui.update_fonts(
            self.ui_components.header_font,
            self.ui_components.normal_font
        )
        
        # Renderer
        self.renderer = GameRenderer(
            self.session,
            self.ui_components,
            self.ui_renderer,
            self.animation_manager,
            self.run_button,
            self.status_ui
        )
        
        # Input handler
        self.input_handler = GameInputHandler(
            self.session,
            self.card_action_manager,
            self.room_manager,
            self.inventory_manager,
            self.run_button
        )

    def _start_initial_room(self):
        """Start the first room."""
        self.room_manager.start_new_room()
        self.room_started_in_enter = True

    def exit(self):
        """Save state when exiting."""
        if self.session:
            # Save to game data
            save_data = self.session.save_to_dict()
            self.game_manager.game_data.update(save_data)

    # ========================================================================
    # Main Loop
    # ========================================================================

    def handle_event(self, event):
        """Handle input events."""
        self.input_handler.handle_event(event, self.animation_manager)

    def update(self, delta_time):
        """Update game state."""
        # Track animation state
        was_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        is_animating = self.animation_manager.is_animating()
        animations_just_finished = was_animating and not is_animating
        
        # Update messages
        self._update_message(delta_time)
        
        # Update cards
        self._update_cards(delta_time)
        
        # Process game logic when animations finish
        if not is_animating:
            self._process_game_logic(animations_just_finished)
        
        # Check for game over
        self.game_state_controller.check_game_over()

    def draw(self, surface):
        """Render the game."""
        self.renderer.render(surface, self.message)

    # ========================================================================
    # Update Helpers
    # ========================================================================

    def _update_message(self, delta_time):
        """Update message fade animation."""
        if not self.message or 'alpha' not in self.message:
            return
        
        if self.message['fade_in']:
            # Fade in
            self.message['alpha'] = min(
                255,
                self.message['alpha'] + self.message['fade_speed'] * delta_time
            )
            if self.message['alpha'] >= 255:
                self.message['fade_in'] = False
        else:
            # Wait then fade out
            self.message['time_remaining'] -= delta_time
            if self.message['time_remaining'] <= 0:
                self.message['alpha'] = max(
                    0,
                    self.message['alpha'] - self.message['fade_speed'] * delta_time
                )
                if self.message['alpha'] <= 0:
                    self.message = None

    def _update_cards(self, delta_time):
        """Update all card animations."""
        # Room cards
        for card in self.session.room.cards:
            card.update(delta_time)
            if hasattr(card, 'is_flipping') and card.is_flipping:
                card.update_flip(delta_time)
        
        # Inventory cards
        for card in self.session.inventory:
            card.update(delta_time)
            if hasattr(card, 'is_flipping') and card.is_flipping:
                card.update_flip(delta_time)
        
        # Equipped weapon
        if self.session.equipped_weapon:
            self.session.equipped_weapon.update(delta_time)
        
        # Defeated monsters
        for monster in self.session.defeated_monsters:
            monster.update(delta_time)

    def _process_game_logic(self, animations_just_finished):
        """Process game state changes after animations."""
        # Skip first frame after room start
        if self.room_started_in_enter:
            self.room_started_in_enter = False
            return
        
        # Check room completion
        if self.session.is_room_empty():
            self._handle_empty_room()
        elif (self.session.has_single_card_remaining() and 
              animations_just_finished and 
              self.session.has_deck_cards_remaining()):
            self._handle_single_card_room()

    def _handle_empty_room(self):
        """Handle when all cards are processed."""
        if not self.session.current_room_complete:
            self.session.mark_room_complete()
        
        if self.session.has_deck_cards_remaining():
            # More rooms on this floor
            self.game_manager.advance_to_next_room()
            if self.game_manager.current_state == self:
                self.room_manager.start_new_room()
        else:
            # Floor complete
            self._handle_floor_completion()

    def _handle_single_card_room(self):
        """Handle when one card remains."""
        if not self.session.current_room_complete:
            self.session.mark_room_complete()
            self.game_manager.advance_to_next_room()
        
        # Carry the card to next room
        carried_card = self.session.room.cards[0]
        self.room_manager.start_new_room(carried_card)

    def _handle_floor_completion(self):
        """Handle when floor is complete."""
        if self.session.floor_complete:
            return
        
        self.session.mark_floor_complete()
        
        # Check if final floor
        floor_manager = self.game_manager.floor_manager
        is_final = floor_manager.current_floor_index >= len(floor_manager.floors) - 1
        
        if is_final:
            # Victory!
            self.game_manager.game_data["victory"] = True
            self.game_manager.game_data["run_complete"] = True
            self.game_manager.change_state("game_over")
        else:
            # Next floor
            next_floor_index = floor_manager.current_floor_index + 1
            next_floor_type = floor_manager.floors[next_floor_index]
            
            self.show_message(
                f"Floor completed! Moving to {next_floor_type.title()}..."
            )
            
            self.animation_controller.schedule_delayed_animation(
                3.0,
                lambda: self._transition_to_next_floor()
            )

    def _transition_to_next_floor(self):
        """Transition to the next floor."""
        # Advance floor
        self.game_manager.floor_manager.advance_floor()
        next_floor = self.game_manager.floor_manager.get_current_floor()
        
        # Reset session for new floor
        self.session.reset_for_new_floor(next_floor)
        
        # Reinitialize
        if hasattr(self.session.deck, "initialise_deck"):
            self.session.deck.initialise_deck()
        
        if hasattr(self.session.deck, "initialise_visuals"):
            self.session.deck.initialise_visuals()
        
        # Start first room
        self.room_manager.start_new_room()

    # ========================================================================
    # Delegation Methods (for managers that need them)
    # ========================================================================

    def show_message(self, message, duration=2.0):
        """Show a message to the player."""
        self.game_state_controller.show_message(message, duration)
