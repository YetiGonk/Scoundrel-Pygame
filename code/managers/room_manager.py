class RoomManager:
    """Manages room creation, transitions, and completion."""

    def __init__(self, playing_state):
        self.playing_state = playing_state

    def start_new_room(self, last_card=None):
        """Start a new room with cards from the deck."""

        if self.playing_state.life_points <= 0:
            return

        if self.playing_state.animation_manager.is_animating():
            return

        if hasattr(self.playing_state, 'room_started_in_enter') and self.playing_state.room_started_in_enter:
            return

        self.playing_state.room_completion_in_progress = False

        self.playing_state.room.clear()

        if last_card:
            self.playing_state.room.add_card(last_card)
            last_card.face_up = True

            num_cards = min(4, len(self.playing_state.deck.cards) + 1)
            total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
            start_x = (SCREEN_WIDTH - total_width) // 2
            start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

            first_position = (start_x, start_y)

            self.playing_state.animate_card_movement(last_card, first_position)

        cards_to_draw = min(4 - len(self.playing_state.room.cards), len(self.playing_state.deck.cards))

        num_cards = min(4, len(self.playing_state.deck.cards) + len(self.playing_state.room.cards))
        total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        target_positions = []
        for i in range(num_cards):
            target_positions.append((
                int(start_x + i * (CARD_WIDTH + self.playing_state.room.card_spacing)),
                int(start_y)
            ))

        for i in range(cards_to_draw):
            if self.playing_state.deck.cards:
                card_data = self.playing_state.deck.draw_card()

                floor_type = card_data.get("floor_type", self.playing_state.current_floor)
                card = Card(card_data["suit"], card_data["value"], floor_type)

                card.face_up = False

                if self.playing_state.deck.card_stack:
                    card.update_position(self.playing_state.deck.card_stack[-1])
                else:
                    card.update_position(self.playing_state.deck.position)

                self.playing_state.room.add_card(card)

                card_position_index = i + (1 if last_card else 0)

                if card_position_index < len(target_positions):
                    target_pos = target_positions[card_position_index]
                else:

                    target_pos = target_positions[-1]

                delay = 0.1 * i

                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=card, pos=target_pos: self.playing_state.animate_card_movement(
                        card,
                        pos,
                        duration=0.3,
                        on_complete=lambda c=card: self.playing_state.start_card_flip(c)
                    )
                )

        if self.playing_state.deck.card_stack:
            for i in range(cards_to_draw):
                if self.playing_state.deck.card_stack:
                    self.playing_state.deck.card_stack.pop()
        self.playing_state.deck.initialise_visuals()

    def run_from_room(self):
        """Run from the current room, moving all cards to the bottom of the deck."""
        if len(self.playing_state.room.cards) != 4 or self.playing_state.animation_manager.is_animating():
            return

        for card in self.playing_state.room.cards:
            if not card.face_up or card.is_flipping:
                return

        self.playing_state.is_running = True

        for card in list(self.playing_state.room.cards):

            if self.playing_state.deck.card_stack:
                target_pos = self.playing_state.deck.card_stack[0]
            else:
                target_pos = self.playing_state.deck.position

            card.z_index = -100

            self.playing_state.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )

            card_data = {"suit": card.suit, "value": card.value}
            self.playing_state.deck.add_to_bottom(card_data)

        self.playing_state.deck.initialise_visuals()

    def on_run_completed(self):
        """Complete the running action after animations finish."""

        self.playing_state.room.clear()
        self.playing_state.is_running = False

        self.playing_state.deck.initialise_visuals()

        self.playing_state.ran_last_turn = True

        self.playing_state.game_manager.advance_to_next_room()

        if hasattr(self.playing_state, 'status_ui') and hasattr(self.playing_state.status_ui, 'update_status'):
            self.playing_state.status_ui.update_status()

        if hasattr(self.playing_state, 'hire_manager'):

            original_chance = self.playing_state.hire_manager.hire_encounter_chance
            self.playing_state.hire_manager.hire_encounter_chance = original_chance / 2

            hire_encounter_started = self.playing_state.hire_manager.try_start_hire_encounter()

            self.playing_state.hire_manager.hire_encounter_chance = original_chance

            if hire_encounter_started:

                return

        self.start_new_room()

    def transition_to_next_floor(self):
        """Helper method to transition to the next floor."""

        current_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        current_floor = self.playing_state.game_manager.floor_manager.get_current_floor()

        if hasattr(self.playing_state, 'discard_pile') and self.playing_state.discard_pile:
            self.playing_state.discard_pile.cards = []
            if hasattr(self.playing_state.discard_pile, 'card_stack'):
                self.playing_state.discard_pile.card_stack = []

        self.playing_state.game_manager.floor_manager.advance_floor()
        next_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        next_floor = self.playing_state.game_manager.floor_manager.get_current_floor()

        self.playing_state.floor_completed = False

        self.playing_state.game_manager.game_data["life_points"] = self.playing_state.life_points
        self.playing_state.game_manager.game_data["max_life"] = self.playing_state.max_life

        self.playing_state.completed_rooms = 0

        self.playing_state._start_initial_room()

    def remove_and_discard(self, card):
        """Remove a card from the room and add it to the discard pile."""
        if card in self.playing_state.room.cards:
            self.playing_state.room.remove_card(card)

        if card in self.playing_state.defeated_monsters:
            self.playing_state.defeated_monsters.remove(card)

        if self.playing_state.equipped_weapon and card == self.playing_state.equipped_weapon["node"]:
            self.playing_state.equipped_weapon = {}

        self.playing_state.discard_pile.add_card(card)
