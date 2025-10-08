"""
managers/room_manager.py - CLEAN VERSION

Works directly with GameSession.
No more fake sessions, no more set_playing_state_ref hacks!
"""

from config import *
from entities.card import Card


class RoomManager:
    """Manages room creation and transitions."""

    def __init__(self, playing_state):
        """Initialize with reference to playing state."""
        self.playing_state = playing_state

    @property
    def session(self):
        """Quick access to game session."""
        return self.playing_state.session

    @property
    def animation_controller(self):
        """Quick access to animation controller."""
        return self.playing_state.animation_controller

    @property
    def animation_manager(self):
        """Quick access to animation manager."""
        return self.playing_state.animation_manager

    def start_new_room(self, carried_card=None):
        """Start a new room with cards from deck."""
        # Don't start if player is dead or animations playing
        if self.session.is_player_dead():
            return
        
        if self.animation_manager.is_animating():
            return
        
        # Mark new room started
        self.session.start_new_room()
        
        # Clear room
        self.session.room.clear()
        
        # Handle carried card
        if carried_card:
            self._position_carried_card(carried_card)
        
        # Draw new cards
        cards_in_room = 1 if carried_card else 0
        cards_to_draw = min(4 - cards_in_room, len(self.session.deck.cards))
        
        if cards_to_draw > 0:
            self._draw_cards(cards_to_draw, has_carried=carried_card is not None)
        
        # Update deck visuals
        self._update_deck_visuals()

    def _position_carried_card(self, card):
        """Position a card carried from previous room."""
        self.session.room.add_card(card)
        card.face_up = True
        
        # Calculate first position
        num_cards = min(4, len(self.session.deck.cards) + 1)
        positions = self._calculate_positions(num_cards)
        
        # Animate to position
        self.animation_controller.animate_card_movement(card, positions[0])

    def _draw_cards(self, count, has_carried=False):
        """Draw cards from deck to room."""
        # Calculate positions
        total_cards = count + (1 if has_carried else 0)
        positions = self._calculate_positions(total_cards)
        
        # Draw each card
        for i in range(count):
            if not self.session.deck.cards:
                break
            
            # Draw card data
            card_data = self.session.deck.draw_card()
            
            # Create card
            floor_type = card_data.get("floor_type", self.session.current_floor)
            card = Card(card_data["suit"], card_data["value"], floor_type)
            card.face_up = False
            
            # Position at deck
            if self.session.deck.card_stack:
                card.update_position(self.session.deck.card_stack[-1])
            else:
                card.update_position(self.session.deck.position)
            
            # Add to room
            self.session.room.add_card(card)
            
            # Calculate target position
            pos_index = i + (1 if has_carried else 0)
            target_pos = positions[pos_index] if pos_index < len(positions) else positions[-1]
            
            # Animate with delay
            delay = 0.1 * i
            self.animation_controller.schedule_delayed_animation(
                delay,
                lambda c=card, p=target_pos: self._animate_card_draw(c, p)
            )
        
        # Remove drawn cards from deck visual stack
        if self.session.deck.card_stack:
            for _ in range(min(count, len(self.session.deck.card_stack))):
                self.session.deck.card_stack.pop()

    def _animate_card_draw(self, card, target_pos):
        """Animate card moving and flipping."""
        self.animation_controller.animate_card_movement(
            card,
            target_pos,
            duration=0.3,
            on_complete=lambda c=card: self.animation_controller.start_card_flip(c)
        )

    def _calculate_positions(self, num_cards):
        """Calculate positions for cards in room."""
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

    def _update_deck_visuals(self):
        """Update deck visual representation."""
        if hasattr(self.session.deck, 'initialise_visuals'):
            self.session.deck.initialise_visuals()

    # ========================================================================
    # Run Action
    # ========================================================================

    def run_from_room(self):
        """Run from room, moving all cards to bottom of deck."""
        # Can only run with 4 face-up cards
        if len(self.session.room.cards) != 4:
            return
        
        if self.animation_manager.is_animating():
            return
        
        # Check all cards are face up
        for card in self.session.room.cards:
            if not card.face_up or card.is_flipping:
                return
        
        # Start running
        # (Use a simple flag instead of session.is_running)
        self.playing_state.room_started_in_enter = True  # Reuse this flag
        
        # Get target position
        if self.session.deck.card_stack:
            target_pos = self.session.deck.card_stack[0]
        else:
            target_pos = self.session.deck.position
        
        # Animate all cards to deck
        for card in list(self.session.room.cards):
            card.z_index = -100  # Behind everything
            
            self.animation_controller.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )
            
            # Add to bottom of deck
            card_data = {"suit": card.suit, "value": card.value}
            self.session.deck.add_to_bottom(card_data)
        
        # Update deck visuals
        self._update_deck_visuals()
        
        # Schedule room clear and restart
        self.animation_controller.schedule_delayed_animation(
            0.4,
            self._complete_run
        )

    def _complete_run(self):
        """Complete the run action."""
        # Clear room
        self.session.room.clear()
        
        # Mark that we ran
        self.session.ran_last_turn = True
        
        # Advance room
        self.playing_state.game_manager.advance_to_next_room()
        
        # Update status UI
        if hasattr(self.playing_state, 'status_ui'):
            if hasattr(self.playing_state.status_ui, 'update_status'):
                self.playing_state.status_ui.update_status()
        
        # Start new room
        self.start_new_room()

    # ========================================================================
    # Card Removal
    # ========================================================================

    def remove_and_discard(self, card):
        """Remove a card from play and discard it."""
        # Remove from room
        if card in self.session.room.cards:
            self.session.room.remove_card(card)
        
        # Remove from defeated monsters
        if card in self.session.defeated_monsters:
            self.session.defeated_monsters.remove(card)
        
        # Remove from equipped weapon
        if self.session.equipped_weapon == card:
            self.session.equipped_weapon = None
        
        # Add to discard pile
        self.session.discard_pile.add_card(card)
