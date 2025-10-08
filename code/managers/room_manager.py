from config import *
from entities.card import Card


class RoomManager:
    """
    Manages room creation, transitions, and completion.
    Refactored to use dependency injection and work with GameSession.
    """

    def __init__(self, session, animation_manager, animation_controller, game_manager):
        self.session = session
        self.animation_manager = animation_manager
        self.animation_controller = animation_controller
        self.game_manager = game_manager

    def start_new_room(self, last_card=None):

        if self.session.player.life_points <= 0:
            return

        if self.animation_manager.is_animating():
            return

        # Reset completion flag
        self.session.room_completion_in_progress = False

        # Clear the room
        self.session.room.clear()

        # Handle carried-over card from previous room
        if last_card:
            self._position_carried_card(last_card)

        # Draw new cards from deck
        self._draw_cards_to_room(last_card)

        # Update deck visuals
        self._update_deck_visuals()

    def _position_carried_card(self, card):
        # Add card to room and make it face up
        self.session.room.add_card(card)
        card.face_up = True

        # Calculate position for first card
        num_cards = min(4, len(self.session.deck.cards) + 1)
        total_width = (CARD_WIDTH * num_cards) + (self.session.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        first_position = (start_x, start_y)

        # Animate card to its position
        self.animation_controller.animate_card_movement(card, first_position)

    def _draw_cards_to_room(self, has_carried_card):
        cards_to_draw = min(
            4 - len(self.session.room.cards),
            len(self.session.deck.cards)
        )

        # Calculate target positions for all cards
        target_positions = self._calculate_card_positions(has_carried_card)

        # Draw and position each card
        for i in range(cards_to_draw):
            if self.session.deck.cards:
                self._draw_single_card(i, has_carried_card, target_positions)

        # Remove drawn cards from deck stack
        self._remove_drawn_cards_from_stack(cards_to_draw)

    def _calculate_card_positions(self, has_carried_card):
        num_cards = min(4, len(self.session.deck.cards) + len(self.session.room.cards))
        total_width = (CARD_WIDTH * num_cards) + (self.session.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        positions = []
        for i in range(num_cards):
            positions.append((
                int(start_x + i * (CARD_WIDTH + self.session.room.card_spacing)),
                int(start_y)
            ))

        return positions

    def _draw_single_card(self, index, has_carried_card, target_positions):
        # Draw card data from deck
        card_data = self.session.deck.draw_card()

        # Create card entity
        floor_type = card_data.get("floor_type", self.session.current_floor)
        card = Card(card_data["suit"], card_data["value"], floor_type)

        card.face_up = False

        if self.session.deck.card_stack:
            card.update_position(self.session.deck.card_stack[-1])
        else:
            card.update_position(self.session.deck.position)

        self.session.room.add_card(card)

        card_position_index = index + (1 if has_carried_card else 0)
        
        if card_position_index < len(target_positions):
            target_pos = target_positions[card_position_index]
        else:
            target_pos = target_positions[-1]

        delay = 0.1 * index

        self.animation_controller.schedule_delayed_animation(
            delay,
            lambda c=card, pos=target_pos: self._animate_card_draw(c, pos)
        )

    def _animate_card_draw(self, card, target_pos):
        self.animation_controller.animate_card_movement(
            card,
            target_pos,
            duration=0.3,
            on_complete=lambda c=card: self.animation_controller.start_card_flip(c)
        )

    def _remove_drawn_cards_from_stack(self, cards_to_draw):
        if self.session.deck.card_stack:
            for _ in range(cards_to_draw):
                if self.session.deck.card_stack:
                    self.session.deck.card_stack.pop()

    def _update_deck_visuals(self):
        """Update the deck's visual representation."""
        if hasattr(self.session.deck, 'initialise_visuals'):
            self.session.deck.initialise_visuals()

    def run_from_room(self):
        if not self._can_run():
            return

        # Mark as running
        self.session.is_running = True

        # Move all cards to bottom of deck
        for card in list(self.session.room.cards):
            self._move_card_to_deck_bottom(card)

        # Update deck visuals
        self._update_deck_visuals()

    def _can_run(self):
        # Must have exactly 4 cards
        if len(self.session.room.cards) != 4:
            return False

        # Animations must not be playing
        if self.animation_manager.is_animating():
            return False

        # All cards must be face up and not flipping
        for card in self.session.room.cards:
            if not card.face_up or card.is_flipping:
                return False

        return True

    def _move_card_to_deck_bottom(self, card):
        # Determine target position
        if self.session.deck.card_stack:
            target_pos = self.session.deck.card_stack[0]
        else:
            target_pos = self.session.deck.position

        # Set z-index low so card goes behind other cards
        card.z_index = -100

        # Animate card movement
        self.animation_controller.animate_card_movement(
            card,
            target_pos,
            duration=0.3
        )

        # Add card data back to deck
        card_data = {"suit": card.suit, "value": card.value}
        self.session.deck.add_to_bottom(card_data)

    def on_run_completed(self):
        # Clear the room
        self.session.room.clear()
        self.session.is_running = False

        # Update deck visuals
        self._update_deck_visuals()

        # Mark that player ran this turn (prevents running again)
        self.session.ran_last_turn = True

        # Advance to next room
        self.game_manager.advance_to_next_room()

        # Update status UI if available
        self._update_status_ui()

        # Check for hire encounter (if hire system is available)
        hire_started = self._try_hire_encounter()

        # Start new room if no hire encounter started
        if not hire_started:
            self.start_new_room()

    def _update_status_ui(self):
        if hasattr(self.session, 'status_ui'):
            status_ui = self.session.status_ui
            if hasattr(status_ui, 'update_status'):
                status_ui.update_status()

    def _try_hire_encounter(self):
        if not hasattr(self.session, 'hire_manager'):
            return False

        hire_manager = self.session.hire_manager

        # Temporarily reduce hire chance (running penalty)
        original_chance = hire_manager.hire_encounter_chance
        hire_manager.hire_encounter_chance = original_chance / 2

        # Try to start encounter
        hire_started = hire_manager.try_start_hire_encounter()

        # Restore original chance
        hire_manager.hire_encounter_chance = original_chance

        return hire_started

    def transition_to_next_floor(self):
        current_floor_index = self.game_manager.floor_manager.current_floor_index
        current_floor = self.game_manager.floor_manager.get_current_floor()

        # Clear discard pile for new floor
        self._clear_discard_pile()

        # Advance to next floor
        self.game_manager.floor_manager.advance_floor()
        next_floor_index = self.game_manager.floor_manager.current_floor_index
        next_floor = self.game_manager.floor_manager.get_current_floor()

        # Reset floor completion flag
        self.session.floor_completed = False

        # Save player state
        self._save_player_state()

        # Reset room counter
        self.session.completed_rooms = 0

        # Start first room of new floor
        # Note: This calls back to playing_state temporarily
        # This should be refactored to use GameLogic instead
        self._start_floor_initial_room()

    def _clear_discard_pile(self):
        """Clear the discard pile."""
        if hasattr(self.session, 'discard_pile') and self.session.discard_pile:
            self.session.discard_pile.cards = []
            if hasattr(self.session.discard_pile, 'card_stack'):
                self.session.discard_pile.card_stack = []

    def _save_player_state(self):
        """Save player state to game data."""
        self.game_manager.game_data["life_points"] = self.session.player.life_points
        self.game_manager.game_data["max_life"] = self.session.player.max_life

    def _start_floor_initial_room(self):
        """
        Start the initial room of a new floor.
        
        NOTE: This is a temporary implementation that reaches back to playing_state.
        Should be refactored to work entirely with GameSession and GameLogic.
        """
        # Temporary: Access playing_state for initialization
        # TODO: Move this logic to GameLogic or a FloorTransitionHandler
        if hasattr(self, '_playing_state_ref'):
            self._playing_state_ref._start_initial_room()
        else:
            # Fallback: Just start a new room
            self.start_new_room()

    def remove_and_discard(self, card):
        # Remove from room if present
        if card in self.session.room.cards:
            self.session.room.remove_card(card)

        # Remove from defeated monsters if present
        if card in self.session.player.defeated_monsters:
            self.session.player.defeated_monsters.remove(card)

        # Remove from equipped weapon if it's the equipped weapon
        if self.session.player.has_weapon() and card == self.session.player.equipped_weapon:
            self.session.player.equipped_weapon = None

        # Add to discard pile
        self.session.discard_pile.add_card(card)

    def set_playing_state_ref(self, playing_state):
        self._playing_state_ref = playing_state