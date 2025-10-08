"""
core/game_logic.py

Handles all game progression, state transitions, and rule enforcement.
Extracts game logic from PlayingState for better separation of concerns.
"""


class GameLogic:
    """
    Manages game progression, room transitions, floor completion, and game rules.
    This class handles the "what happens next" logic of the game.
    """

    def __init__(self, session, managers, game_manager, animation_controller):
        """
        Initialize the game logic system.

        Args:
            session: GameSession containing all game state
            managers: ManagerCollection with all game managers
            game_manager: Main game manager for state changes
            animation_controller: For scheduling delayed animations
        """
        self.session = session
        self.managers = managers
        self.game_manager = game_manager
        self.animation_controller = animation_controller

        # State tracking flags
        self.room_started_in_enter = False
        self.room_completion_in_progress = False

    def update(self, animations_just_finished):
        """
        Main update loop for game logic.
        Called each frame when no animations are playing.

        Args:
            animations_just_finished: Whether animations completed this frame
        """
        # Handle run completion
        if self.session.is_running:
            self.managers.room_manager.on_run_completed()
            return

        # Skip first update after room start to prevent double processing
        if self.room_started_in_enter:
            self.room_started_in_enter = False
            return

        # Check room state and progress accordingly
        if self._is_room_empty():
            self._handle_empty_room()
        elif self._is_single_card_remaining() and animations_just_finished:
            self._handle_single_card_room()

    def start_room(self, carried_card=None):
        """
        Start a new room, optionally carrying over a card.

        Args:
            carried_card: Optional card to carry from previous room
        """
        self.managers.room_manager.start_new_room(carried_card)
        self.room_started_in_enter = True
        self.room_completion_in_progress = False

    def reset_for_new_floor(self):
        """Reset state tracking when starting a new floor."""
        self.session.floor_completed = False
        
        if self.game_manager.floor_manager.current_room == 1:
            self.session.completed_rooms = 0

    # ========================================================================
    # Room State Checks
    # ========================================================================

    def _is_room_empty(self):
        """Check if the room has no cards left."""
        return len(self.session.room.cards) == 0

    def _is_single_card_remaining(self):
        """Check if room has exactly one card and deck has more cards."""
        return (
            len(self.session.room.cards) == 1 and
            len(self.session.deck.cards) > 0
        )

    # ========================================================================
    # Room Progression
    # ========================================================================

    def _handle_empty_room(self):
        """
        Handle logic when all cards have been processed in a room.
        Either advance to next room or complete the floor.
        """
        # Mark room as completed (only once)
        if not self.room_completion_in_progress:
            self.room_completion_in_progress = True
            self.session.completed_rooms += 1

        # Check if there are more rooms on this floor
        if len(self.session.deck.cards) > 0:
            self._advance_to_next_room()
        else:
            self._handle_floor_completion()

    def _handle_single_card_room(self):
        """
        Handle logic when only one card remains.
        This allows carrying the card to the next room.
        """
        # Mark room as completed (only once)
        if not self.room_completion_in_progress:
            self.room_completion_in_progress = True
            self.session.completed_rooms += 1
            self.game_manager.advance_to_next_room()

        # Start new room with the remaining card
        carried_card = self.session.room.cards[0]
        self.start_room(carried_card)

    def _advance_to_next_room(self):
        """Advance to the next room on the current floor."""
        self.game_manager.advance_to_next_room()

        # Update status UI if available
        if hasattr(self.managers, 'status_ui'):
            status_ui = self.managers.status_ui
            if hasattr(status_ui, 'update_status'):
                status_ui.update_status()

        # Start the new room if we're still in playing state
        if self.game_manager.current_state == self.game_manager.states.get('playing'):
            self.start_room()

    # ========================================================================
    # Floor Progression
    # ========================================================================

    def _handle_floor_completion(self):
        """
        Handle logic when all rooms on a floor are completed.
        Either transition to next floor or trigger victory.
        """
        # Prevent double-processing
        if self.session.floor_completed:
            return

        self.session.floor_completed = True

        # Check if this was the final floor
        if self._is_final_floor():
            self._trigger_victory()
        else:
            self._transition_to_next_floor()

    def _is_final_floor(self):
        """Check if the current floor is the last floor."""
        floor_manager = self.game_manager.floor_manager
        return floor_manager.current_floor_index >= len(floor_manager.floors) - 1

    def _trigger_victory(self):
        """Trigger victory condition and transition to game over state."""
        self.game_manager.game_data["victory"] = True
        self.game_manager.game_data["run_complete"] = True
        self.game_manager.change_state("game_over")

    def _transition_to_next_floor(self):
        """Show message and schedule transition to next floor."""
        # Get floor names for message
        current_floor_name = self._format_floor_name(
            self.game_manager.floor_manager.get_current_floor()
        )
        
        next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
        next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
        next_floor_name = self._format_floor_name(next_floor_type)

        # Show completion message
        message = f"Floor {current_floor_name} completed! Moving to {next_floor_name}..."
        self.managers.game_state_controller.show_message(message)

        # Schedule floor transition after delay
        self.animation_controller.schedule_delayed_animation(
            3.0,  # 3 second delay
            lambda: self.managers.room_manager.transition_to_next_floor()
        )

    def _format_floor_name(self, floor_type):
        """
        Format floor name for display (handle apostrophes, capitalize properly).

        Args:
            floor_type: Raw floor type string (e.g. "dragon's_lair")

        Returns:
            Formatted floor name (e.g. "Dragon's Lair")
        """
        if "'" in floor_type:
            # Handle apostrophes: split, capitalize each word, rejoin
            words = floor_type.split()
            capitalized = [word.capitalize() for word in words]
            return " ".join(capitalized)
        else:
            # Simple title case
            return floor_type.title()


class CardUpdateSystem:
    """
    Handles updating all card states and animations.
    Separated from GameLogic for cleaner organization.
    """

    def __init__(self, session):
        """
        Initialize the card update system.

        Args:
            session: GameSession containing cards to update
        """
        self.session = session

    def update_all_cards(self, delta_time):
        """
        Update all cards in the game (room, inventory, equipped, defeated).

        Args:
            delta_time: Time since last frame in seconds
        """
        self._update_room_cards(delta_time)
        self._update_inventory_cards(delta_time)
        self._update_equipped_weapon(delta_time)
        self._update_defeated_monsters(delta_time)

    def _update_room_cards(self, delta_time):
        """Update all cards currently in the room."""
        for card in self.session.room.cards:
            card.update(delta_time)
            
            if hasattr(card, 'is_flipping') and card.is_flipping:
                card.update_flip(delta_time)

    def _update_inventory_cards(self, delta_time):
        """Update all cards in player inventory."""
        for card in self.session.player.inventory:
            card.update(delta_time)
            
            if hasattr(card, 'is_flipping') and card.is_flipping:
                card.update_flip(delta_time)

    def _update_equipped_weapon(self, delta_time):
        """Update equipped weapon card if present."""
        if self.session.player.has_weapon():
            weapon = self.session.player.equipped_weapon
            weapon.update(delta_time)

    def _update_defeated_monsters(self, delta_time):
        """Update all defeated monster cards."""
        for monster in self.session.player.defeated_monsters:
            monster.update(delta_time)


class MessageSystem:
    """
    Handles displaying and fading messages to the player.
    Manages message state and animations.
    """

    def __init__(self):
        """Initialize the message system."""
        self.current_message = None

    def update(self, delta_time):
        """
        Update message fade animation.

        Args:
            delta_time: Time since last frame in seconds
        """
        if not self.current_message:
            return

        if 'alpha' not in self.current_message:
            return

        # Handle fade in
        if self.current_message['fade_in']:
            self._update_fade_in(delta_time)
        else:
            self._update_fade_out(delta_time)

    def _update_fade_in(self, delta_time):
        """Fade message in to full opacity."""
        self.current_message['alpha'] = min(
            255,
            self.current_message['alpha'] + self.current_message['fade_speed'] * delta_time
        )

        # Switch to fade out mode when fully visible
        if self.current_message['alpha'] >= 255:
            self.current_message['fade_in'] = False

    def _update_fade_out(self, delta_time):
        """Wait, then fade message out."""
        # Count down display time
        self.current_message['time_remaining'] -= delta_time

        # Start fading when time expires
        if self.current_message['time_remaining'] <= 0:
            self.current_message['alpha'] = max(
                0,
                self.current_message['alpha'] - self.current_message['fade_speed'] * delta_time
            )

            # Remove message when fully faded
            if self.current_message['alpha'] <= 0:
                self.current_message = None

    def set_message(self, message_data):
        """
        Set a new message to display.

        Args:
            message_data: Dict containing message text, position, fade settings, etc.
        """
        self.current_message = message_data

    def get_current_message(self):
        """
        Get the current message for rendering.

        Returns:
            Current message dict or None
        """
        return self.current_message

    def has_message(self):
        """Check if there's currently a message to display."""
        return self.current_message is not None


class ManagerCollection:
    """
    Container for all game managers.
    Provides clean access and avoids passing individual managers around.
    """

    def __init__(self, card_action_manager, room_manager, inventory_manager, 
        player_state_manager, game_state_controller, status_ui=None
    ):
        """
        Initialize the manager collection.

        Args:
            card_action_manager: Handles card actions
            room_manager: Handles room operations
            inventory_manager: Handles inventory operations
            player_state_manager: Handles player state
            game_state_controller: Handles game state transitions
            status_ui: Optional status UI manager
        """
        self.card_action_manager = card_action_manager
        self.room_manager = room_manager
        self.inventory_manager = inventory_manager
        self.player_state_manager = player_state_manager
        self.game_state_controller = game_state_controller
        self.status_ui = status_ui