"""
managers/card_action_manager.py - CLEAN VERSION

Works directly with GameSession.
No more dict nonsense, no more z_index madness.
"""

from config import WEAPON_POSITION


class CardActionManager:
    """Manages card-related actions."""

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

    def resolve_card(self, card, event_pos=None):
        """Process a clicked card."""
        if not card.face_up or card.is_flipping:
            return
        
        if self.playing_state.animation_manager.is_animating():
            return
        
        self.session.ran_last_turn = False
        card.is_selected = True
        
        # Check for inventory add (click top half)
        if card.can_add_to_inventory and event_pos:
            if self._clicked_top_half(card, event_pos):
                if self.session.can_add_to_inventory():
                    self.add_to_inventory(card)
                    return
        
        # Check for weapon attack (click top half)
        elif card.can_show_attack_options and event_pos:
            can_weapon_attack = (
                self.session.has_weapon() and
                self._can_defeat_with_weapon(card)
            )
            
            if can_weapon_attack and self._clicked_top_half(card, event_pos):
                self.attack_with_weapon(card)
                return
            else:
                self.attack_barehanded(card)
                return
        
        # Default actions based on card type
        if card.type == "monster":
            self.attack_barehanded(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)

    def _clicked_top_half(self, card, event_pos):
        """Check if click was on top half of card."""
        total_float = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float = card.idle_float_offset + card.hover_float_offset
        
        center_y = card.rect.centery - total_float
        return event_pos[1] < center_y

    def _can_defeat_with_weapon(self, monster):
        """Check if weapon can defeat monster without taking damage."""
        if not self.session.equipped_weapon:
            return False
        
        weapon_value = self.session.equipped_weapon.value
        
        # Check if can add to stack
        if self.session.defeated_monsters:
            last_monster = self.session.defeated_monsters[-1]
            # Can only stack if this monster is weaker than last defeated
            return last_monster.value > monster.value
        else:
            # First monster - can defeat if weapon is strong enough
            return monster.value <= weapon_value

    # ========================================================================
    # Attack Actions
    # ========================================================================

    def attack_barehanded(self, monster):
        """Attack monster without weapon - take full damage."""
        damage = monster.value
        
        # Remove from room
        self.session.room.remove_card(monster)
        
        # Take damage
        if damage > 0:
            self.session.change_health(-damage)
            self.animation_controller.animate_health_change(True, damage)
        
        # Discard monster
        self.animation_controller.animate_card_to_discard(monster)
        self.playing_state.show_message(f"Attacked {monster.name} bare-handed! Took {damage} damage.")
        
        # Reposition remaining cards
        self._reposition_room_cards()

    def attack_with_weapon(self, monster):
        """Attack monster with equipped weapon."""
        weapon = self.session.equipped_weapon
        weapon_value = weapon.value
        monster_value = monster.value
        
        # Remove from room
        self.session.room.remove_card(monster)
        
        # Calculate damage (weapon reduces it)
        damage = max(0, monster_value - weapon_value)
        
        if damage > 0:
            self.session.change_health(-damage)
            self.animation_controller.animate_health_change(True, damage)
        
        # Add to defeated stack
        monster.is_defeated = True
        self.session.add_defeated_monster(monster)
        
        # Position monster on weapon stack
        self.animation_controller.position_monster_stack()
        
        if damage > 0:
            self.playing_state.show_message(
                f"Defeated {monster.name}! Took {damage} damage."
            )
        else:
            self.playing_state.show_message(f"Defeated {monster.name}!")
        
        # Reposition remaining cards
        self._reposition_room_cards()

    # ========================================================================
    # Equipment Actions
    # ========================================================================

    def equip_weapon(self, weapon):
        """Equip a weapon card."""
        # Get old equipment
        old_weapon, old_monsters = self.session.equip_weapon(weapon)
        
        # Mark as equipped
        weapon.is_equipped = True
        
        # Animate to weapon position
        def finalize():
            self.session.room.remove_card(weapon)
        
        self.animation_controller.animate_card_movement(
            weapon,
            WEAPON_POSITION,
            on_complete=finalize
        )
        
        self.playing_state.show_message(f"Equipped {weapon.name}")
        
        # Discard old equipment
        self._discard_old_equipment(old_weapon, old_monsters)

    def _discard_old_equipment(self, old_weapon, old_monsters):
        """Discard old weapon and defeated monsters."""
        # Discard old monsters
        for i, monster in enumerate(old_monsters):
            delay = 0.08 * i
            self.animation_controller.schedule_delayed_animation(
                delay,
                lambda m=monster: self.animation_controller.animate_card_to_discard(m)
            )
        
        # Discard old weapon
        if old_weapon:
            delay = 0.08 * len(old_monsters)
            self.animation_controller.schedule_delayed_animation(
                delay,
                lambda: self.animation_controller.animate_card_to_discard(old_weapon)
            )

    def discard_equipped_weapon(self):
        """Discard currently equipped weapon."""
        weapon, monsters = self.session.unequip_weapon()
        
        if weapon:
            weapon.is_equipped = False
            self.playing_state.show_message(f"{weapon.name} discarded")
            self.animation_controller.animate_card_to_discard(weapon)
            
            # Discard defeated monsters too
            for monster in monsters:
                self.animation_controller.animate_card_to_discard(monster)
            
            return True
        
        return False

    # ========================================================================
    # Item Actions
    # ========================================================================

    def use_potion(self, potion):
        """Use a potion to heal."""
        heal_amount = potion.value
        
        # Remove from room
        self.session.room.remove_card(potion)
        
        # Heal player
        actual = self.session.change_health(heal_amount)
        if actual > 0:
            self.animation_controller.animate_health_change(False, actual)
        
        # Discard potion
        self.animation_controller.animate_card_to_discard(potion)
        self.playing_state.show_message(f"Used {potion.name}. Restored {actual} health.")
        
        # Reposition remaining cards
        self._reposition_room_cards()

    def add_to_inventory(self, card):
        """Add card to inventory."""
        if not self.session.add_to_inventory(card):
            return False
        
        card.is_selected = True
        card.in_inventory = True
        
        # Remove from room
        self.session.room.remove_card(card)
        
        # Animate to inventory
        self.animation_controller.animate_card_to_inventory(card)
        
        # Reposition remaining cards
        self._reposition_room_cards()
        
        return True

    def use_inventory_card(self, card, event_pos=None):
        """Use a card from inventory."""
        if card not in self.session.inventory:
            return
        
        card.is_selected = True
        
        # Determine action (top = discard, bottom = use)
        discard_only = False
        if event_pos:
            discard_only = self._clicked_top_half(card, event_pos)
        
        # Remove from inventory
        card.in_inventory = False
        self.session.remove_from_inventory(card)
        self.playing_state.inventory_manager.position_inventory_cards()
        
        # Execute action
        if card.type == "weapon":
            if discard_only:
                self.playing_state.show_message(f"{card.name} discarded")
                self.animation_controller.animate_card_to_discard(card)
            else:
                card.update_scale(1.0)
                self.session.room.add_card(card)
                self.equip_weapon(card)
        
        elif card.type == "potion":
            if discard_only:
                self.playing_state.show_message(f"{card.name} discarded")
                self.animation_controller.animate_card_to_discard(card)
            else:
                actual = self.session.change_health(card.value)
                if actual > 0:
                    self.animation_controller.animate_health_change(False, actual)
                self.playing_state.show_message(f"Used {card.name}. Restored {actual} health.")
                self.animation_controller.animate_card_to_discard(card)
        
        else:
            # Unknown type - just discard
            self.playing_state.show_message(f"{card.name} discarded")
            self.animation_controller.animate_card_to_discard(card)

    # ========================================================================
    # Helpers
    # ========================================================================

    def _reposition_room_cards(self):
        """Reposition remaining room cards with animation."""
        if len(self.session.room.cards) > 0:
            self.animation_controller.schedule_delayed_animation(
                0.1,
                lambda: self.session.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )
