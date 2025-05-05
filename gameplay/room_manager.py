"""Room Manager for handling room transitions and management in the Scoundrel game."""
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
from components.card import Card


class RoomManager:
    """Manages room creation, transitions, and completion."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def start_new_room(self, last_card=None):
        """Start a new room with cards from the deck."""
        print(f"RoomManager.start_new_room called - current room: {self.playing_state.game_manager.floor_manager.current_room}")
        
        if self.playing_state.life_points <= 0:
            print("  Player is dead, not starting room")
            return
        
        if self.playing_state.animation_manager.is_animating():
            print("  Animations running, not starting room")
            return  # Don't start a new room if animations are running
            
        # If we're re-entering the playing state and the flag is already set, we've already started a room
        # in the enter method, so we should avoid starting a new one again in an upcoming update
        if hasattr(self.playing_state, 'room_started_in_enter') and self.playing_state.room_started_in_enter:
            print("  Room already started in enter(), not starting again")
            return
        
        # Treasure room functionality removed
        
        # Reset the room state tracking flags when starting a new room
        self.playing_state.gold_reward_given = False
        self.playing_state.room_completion_in_progress = False
        self.playing_state.treasure_transition_started = False
        
        # Clear the room
        self.playing_state.room.clear()
        
        # Keep the last card if provided
        if last_card:
            self.playing_state.room.add_card(last_card)
            last_card.face_up = True
            
            # Position the card correctly in the center of the room
            # Calculate the target position for the first card
            num_cards = min(4, len(self.playing_state.deck.cards) + 1)  # +1 for the last_card
            total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
            start_x = (SCREEN_WIDTH - total_width) // 2
            start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
            
            # The first position is for the last_card
            first_position = (start_x, start_y)
            
            # Position the last_card with animation
            self.playing_state.animate_card_movement(last_card, first_position)
        
        # Calculate how many cards to draw
        cards_to_draw = min(4 - len(self.playing_state.room.cards), len(self.playing_state.deck.cards))
        
        # Calculate final target positions first - this is AFTER adding the last_card if it exists
        num_cards = min(4, len(self.playing_state.deck.cards) + len(self.playing_state.room.cards))  # Always 4 cards in a full room
        total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
        
        target_positions = []
        for i in range(num_cards):
            target_positions.append((
                int(start_x + i * (CARD_WIDTH + self.playing_state.room.card_spacing)),
                int(start_y)
            ))

        # Draw cards one by one with animations
        for i in range(cards_to_draw):
            if self.playing_state.deck.cards:
                card_data = self.playing_state.deck.draw_card()
                # Check if floor_type is included in card_data, otherwise use self.current_floor
                floor_type = card_data.get("floor_type", self.playing_state.current_floor)
                card = Card(card_data["suit"], card_data["value"], floor_type)
                
                # Cards start face down
                card.face_up = False
                
                # Set the initial position to the top of the deck
                if self.playing_state.deck.card_stack:
                    card.update_position(self.playing_state.deck.card_stack[-1])
                else:
                    card.update_position(self.playing_state.deck.position)
                
                # Add card to room
                self.playing_state.room.add_card(card)
                
                # Calculate which target position to use
                # i is the index of the new card we're drawing (0-based)
                # If we have a last_card, it's already in position 0
                # So new cards should start at position 1 (index 1)
                card_position_index = i + (1 if last_card else 0)
                
                # Ensure we don't go out of bounds
                if card_position_index < len(target_positions):
                    target_pos = target_positions[card_position_index]
                else:
                    # Fallback to last position if somehow we have too many cards
                    target_pos = target_positions[-1]
                
                # Create animation to move card to position with staggered timing
                delay = 0.1 * i  # Stagger the dealing animations
                
                # Create a delayed animation
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=card, pos=target_pos: self.playing_state.animate_card_movement(
                        card, 
                        pos, 
                        duration=0.3,
                        on_complete=lambda c=card: self.playing_state.start_card_flip(c)
                    )
                )
        
        # Update deck display
        if self.playing_state.deck.card_stack:
            for i in range(cards_to_draw):
                if self.playing_state.deck.card_stack:
                    self.playing_state.deck.card_stack.pop()
        self.playing_state.deck.initialise_visuals()
    
    def run_from_room(self):
        """Run from the current room, moving all cards to the bottom of the deck."""
        if len(self.playing_state.room.cards) != 4 or self.playing_state.animation_manager.is_animating():
            return

        # Only allow running if all cards are face up
        for card in self.playing_state.room.cards:
            if not card.face_up or card.is_flipping:
                return

        self.playing_state.is_running = True

        # Animate cards moving to the bottom of the deck
        for card in list(self.playing_state.room.cards):
            # Calculate target position (bottom of deck)
            if self.playing_state.deck.card_stack:
                target_pos = self.playing_state.deck.card_stack[0]
            else:
                target_pos = self.playing_state.deck.position
            
            # Set z-index and create animation
            card.z_index = -100
            
            # Use standard card movement animation
            self.playing_state.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )
            
            # Add the card data back to the bottom of the deck
            card_data = {"suit": card.suit, "value": card.value}
            self.playing_state.deck.add_to_bottom(card_data)
        
        # Update the deck visuals
        self.playing_state.deck.initialise_visuals()
    
    def on_run_completed(self):
        """Complete the running action after animations finish."""
        # Clear the room
        self.playing_state.room.clear()
        self.playing_state.is_running = False
        
        # Update the deck visuals again
        self.playing_state.deck.initialise_visuals()
        
        # Start a new room
        self.start_new_room()
        
        # Set the ran_last_turn flag
        self.playing_state.ran_last_turn = True
    
    def transition_to_next_floor(self):
        """Helper method to transition to the next floor."""
        # Clear the discard pile as we're moving to a new floor
        if hasattr(self.playing_state, 'discard_pile') and self.playing_state.discard_pile:
            # Reset the discard pile's cards
            self.playing_state.discard_pile.cards = []
            # Reset any visual representations
            if hasattr(self.playing_state.discard_pile, 'card_stack'):
                self.playing_state.discard_pile.card_stack = []

        # Advance to the next floor
        self.playing_state.game_manager.floor_manager.advance_floor()
        
        # Change back to playing state
        self.playing_state.game_manager.change_state("playing")
    
    def remove_and_discard(self, card):
        """Remove a card from the room and add it to the discard pile.
        This function should be called only after an animation completes."""
        # First remove from the room if it's still there
        if card in self.playing_state.room.cards:
            self.playing_state.room.remove_card(card)

        if card in self.playing_state.defeated_monsters:
            self.playing_state.defeated_monsters.remove(card)

        if self.playing_state.equipped_weapon and card == self.playing_state.equipped_weapon["node"]:
            self.playing_state.equipped_weapon = {}

        # Add to discard pile
        self.playing_state.discard_pile.add_card(card)