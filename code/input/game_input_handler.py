import pygame
from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN


class GameInputHandler:
    """
    Responsible for processing all player input during gameplay.
    Coordinates with managers to execute actions based on input.
    """

    def __init__(self, session, card_action_manager, room_manager, inventory_manager, run_button):
        self.session = session
        self.card_action_manager = card_action_manager
        self.room_manager = room_manager
        self.inventory_manager = inventory_manager
        self.run_button = run_button

    def handle_event(self, event, animation_manager):
        """
        Main event dispatcher.

        Args:
            event: pygame event to process
            animation_manager: Used to check if animations are blocking input
        """
        # Block input during animations
        if animation_manager.is_animating():
            return

        if event.type == MOUSEMOTION:
            self._handle_hover(event)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event)

    def _handle_hover(self, event):
        """
        Handle mouse hover events over interactive elements.
        Updates hover states for cards and buttons.

        Args:
            event: pygame MOUSEMOTION event
        """
        mouse_pos = event.pos

        # Check if inventory is full for visual feedback
        inventory_is_full = len(self.session.inventory) >= self.session.max_inventory_size

        # Collect all potentially hoverable cards
        all_hoverable_cards = []

        # Process room cards
        for card in self.session.room.cards:
            self._update_card_availability(card, inventory_is_full)
            card.is_hovered = False
            if card.rect.collidepoint(mouse_pos):
                all_hoverable_cards.append(card)

        # Process inventory cards
        for card in self.session.inventory:
            card.is_hovered = False
            if card.rect.collidepoint(mouse_pos):
                all_hoverable_cards.append(card)

        # Process equipped weapon
        if self.session.has_weapon():
            weapon_card = self.session.equipped_weapon
            weapon_card.is_hovered = False
            if weapon_card.rect.collidepoint(mouse_pos):
                all_hoverable_cards.append(weapon_card)

        # Process defeated monsters
        for monster in self.session.defeated_monsters:
            monster.is_hovered = False
            if monster.rect.collidepoint(mouse_pos):
                all_hoverable_cards.append(monster)

        # Find and highlight the closest card to cursor
        if all_hoverable_cards:
            closest_card = self._find_closest_card(mouse_pos, all_hoverable_cards)
            if closest_card:
                closest_card.check_hover(mouse_pos)

        # Update run button hover state
        self.run_button.check_hover(mouse_pos)

    def _update_card_availability(self, card, inventory_is_full):
        """
        Update card properties to show what actions are available.

        Args:
            card: Card to update
            inventory_is_full: Whether the inventory has space
        """
        # Update weapon attack options
        if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
            card.weapon_available = self.session.has_weapon()

            # Check if weapon attack is viable based on last defeated monster
            if self.session.has_weapon() and self.session.defeated_monsters:
                last_monster = self.session.defeated_monsters[-1]
                card.weapon_attack_not_viable = card.value >= last_monster.value
            else:
                card.weapon_attack_not_viable = False

        # Update inventory availability
        if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
            card.inventory_available = not inventory_is_full

    def _find_closest_card(self, pos, cards):
        """
        Find the card closest to the mouse position.
        Uses center-to-cursor distance, accounting for float animations.

        Args:
            pos: Mouse position (x, y)
            cards: List of cards to check

        Returns:
            Card closest to the position, or None
        """
        if not cards:
            return None

        closest_card = None
        closest_distance = float('inf')

        for card in cards:
            # Get card center
            card_center_x = card.rect.centerx
            card_center_y = card.rect.centery

            # Account for floating animations
            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            card_center_y -= total_float_offset

            # Calculate squared distance (no need for sqrt since we're comparing)
            dist_sq = (pos[0] - card_center_x) ** 2 + (pos[1] - card_center_y) ** 2

            if dist_sq < closest_distance:
                closest_distance = dist_sq
                closest_card = card

        return closest_card

    def _handle_click(self, event):
        """
        Handle mouse click events on interactive elements.

        Args:
            event: pygame MOUSEBUTTONDOWN event
        """
        mouse_pos = event.pos

        # Prevent actions if player is dead
        if self.session.life_points <= 0:
            return

        # Check run button
        if self._try_run_button_click(mouse_pos):
            return

        # Check room cards
        if self._try_room_card_click(mouse_pos):
            return

        # Check inventory cards
        if self._try_inventory_card_click(mouse_pos):
            return

        # Check equipped weapon
        if self._try_weapon_click(mouse_pos):
            return

    def _try_run_button_click(self, mouse_pos):
        """
        Check if run button was clicked and execute run action.

        Args:
            mouse_pos: Mouse position

        Returns:
            True if run button was clicked and action taken
        """
        can_run = (
            not self.session.ran_last_turn and
            len(self.session.room.cards) == 4
        )

        if can_run and self.run_button.is_clicked(mouse_pos):
            self.room_manager.run_from_room()
            return True

        return False

    def _try_room_card_click(self, mouse_pos):
        """
        Check if a room card was clicked and resolve it.

        Args:
            mouse_pos: Mouse position

        Returns:
            True if a card was clicked and resolved
        """
        card = self.session.room.get_card_at_position(mouse_pos)
        if card:
            self.card_action_manager.resolve_card(card, event_pos=mouse_pos)
            return True

        return False

    def _try_inventory_card_click(self, mouse_pos):
        """
        Check if an inventory card was clicked and use it.

        Args:
            mouse_pos: Mouse position

        Returns:
            True if an inventory card was used
        """
        clicked_card = self.inventory_manager.get_inventory_card_at_position(mouse_pos)
        if clicked_card:
            self.card_action_manager.use_inventory_card(clicked_card, mouse_pos)
            return True

        return False

    def _try_weapon_click(self, mouse_pos):
        """
        Check if equipped weapon was clicked to discard it.

        Args:
            mouse_pos: Mouse position

        Returns:
            True if weapon was clicked and discarded
        """
        if self.session.has_weapon():
            weapon = self.session.equipped_weapon
            if weapon.rect.collidepoint(mouse_pos):
                self.card_action_manager.discard_equipped_weapon()
                return True

        return False