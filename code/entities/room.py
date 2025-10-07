from animations.animation_base import Animation, EasingFunctions
from animations.specific_animations import *

from config import *

class Room:
    """Represents a room containing cards in the game."""

    def __init__(self, animation_manager=None, card_spacing=35):
        self.cards = []
        self.card_spacing = card_spacing
        self.z_index_counter = 0
        self.animation_manager = animation_manager

        self.name_font = None

    def add_card(self, card):
        self.cards.append(card)

        card.z_index = self.z_index_counter
        self.z_index_counter += 1

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)

            if len(self.cards) > 0:
                self.position_cards(animate=True, animation_manager=self.animation_manager)

    def clear(self):
        self.cards.clear()

    def get_card_count(self):
        return len(self.cards)

    def position_cards(self, animate=False, animation_manager=None):
        if not self.cards:
            return

        num_cards = len(self.cards)
        total_width = (CARD_WIDTH * num_cards) + (self.card_spacing * (num_cards - 1))

        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)

        for i, card in enumerate(sorted_cards):
            card_position = (0, 0)
            if num_cards == 1:

                card_position = (
                    int(start_x - (CARD_WIDTH + self.card_spacing) * 1.5),
                    int(start_y)
                )
            else:
                card_position = (
                    int(start_x + i * (CARD_WIDTH + self.card_spacing)),
                    int(start_y)
                )

            if animate and animation_manager is not None:

                animation = MoveAnimation(
                    card,
                    card.rect.topleft,
                    card_position,
                    0.3,
                    EasingFunctions.ease_out_quad
                )
                animation_manager.add_animation(animation)
            else:

                card.update_position(card_position)

    def get_card_at_position(self, position):
        for card in reversed(sorted(self.cards, key=lambda c: c.z_index)):
            if card.rect.collidepoint(position):
                return card
        return None

    def draw(self, surface):

        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)

        for card in sorted_cards:
            card.draw(surface)

        for card in sorted_cards:
            if card.is_hovered and card.face_up:

                if (hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory) or \
                    (hasattr(card, 'can_show_attack_options') and card.can_show_attack_options):
                    card.draw_hover_text(surface)