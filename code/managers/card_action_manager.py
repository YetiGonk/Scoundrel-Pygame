from config import *

class CardActionManager:
    """Manages card-related actions such as attacking monsters, using equipment, and potions."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def resolve_card(self, card, event_pos=None):
        """Process a card that has been clicked by the player."""
        if (not card.face_up or card.is_flipping or
                self.playing_state.animation_manager.is_animating()):
            return

        self.playing_state.ran_last_turn = False
        card.is_selected = True

        if card.can_add_to_inventory and event_pos:
            inventory_is_full = len(self.playing_state.inventory) >= self.playing_state.MAX_INVENTORY_SIZE
            card.inventory_available = not inventory_is_full

            center_x = card.rect.centerx

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            center_y = card.rect.centery - total_float_offset

            if not inventory_is_full and event_pos[1] < center_y:
                self.add_to_inventory(card)
                return

        elif card.can_show_attack_options and event_pos:
            center_x = card.rect.centerx

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            center_y = card.rect.centery - total_float_offset

            if card.weapon_available and not getattr(card, 'weapon_attack_not_viable', False):
                if event_pos[1] < center_y:
                    self.attack_monster(card)
                    return
                else:
                    self.attack_barehanded(card)
                    return
            else:
                self.attack_barehanded(card)
                return

        if card.type == "monster":
            self.attack_barehanded(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)

    def attack_barehanded(self, monster):
        """Process player attacking a monster card with bare hands (takes full damage)."""
        monster_value = monster.value
        self.playing_state.room.remove_card(monster)

        if monster_value > 0:
            self.playing_state.change_health(-monster_value)

        self.playing_state.animate_card_to_discard(monster)
        self.playing_state.show_message(f"Attacked {monster.name} bare-handed! Took full damage.")

        if len(self.playing_state.room.cards) > 0:
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def attack_monster(self, monster):
        """Process player attacking a monster card with equipped weapon."""
        monster_value = monster.value
        self.playing_state.room.remove_card(monster)

        if self.playing_state.equipped_weapon:
            weapon_node = self.playing_state.equipped_weapon.get("node", None)
            weapon_value = self.playing_state.equipped_weapon.get("value", 0)

            if self.playing_state.defeated_monsters:
                if self.playing_state.defeated_monsters[-1].value > monster_value:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0

                    if damage > 0:
                        self.playing_state.change_health(-damage)

                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:

                    if monster_value > 0:
                        self.playing_state.change_health(-monster_value)

                        self.playing_state.animate_card_to_discard(monster)
            else:
                if monster_value <= weapon_value:
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    monster.is_defeated = True

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0

                    if damage > 0:
                        self.playing_state.change_health(-damage)

                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    monster.is_defeated = True

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
        else:

            if monster_value > 0:
                self.playing_state.change_health(-monster_value)

            self.playing_state.animate_card_to_discard(monster)

        if len(self.playing_state.room.cards) > 0:

            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def equip_weapon(self, weapon):
        """Equip a weapon card."""

        old_weapon = self.playing_state.equipped_weapon.get("node", None)
        old_monsters = self.playing_state.defeated_monsters.copy()

        self.playing_state.room.remove_card(weapon)

        weapon.is_equipped = True

        self.playing_state.equipped_weapon = {
            "suit": weapon.suit,
            "value": weapon.value,
            "node": weapon,
            "difficulty": weapon.weapon_difficulty,
        }
        self.playing_state.defeated_monsters = []

        weapon.z_index = self.playing_state.z_index_counter
        self.playing_state.z_index_counter += 1

        self.playing_state.animate_card_movement(weapon, WEAPON_POSITION)

        self.playing_state.show_message(f"Equipped {weapon.name}")

        if old_weapon or old_monsters:
            for i, monster in enumerate(old_monsters):

                delay = 0.08 * i
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=monster: self.playing_state.animate_card_to_discard(card)
                )

            if old_weapon:
                delay = 0.08 * len(old_monsters)
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda: self.playing_state.animate_card_to_discard(old_weapon)
                )

    def use_potion(self, potion):
        """Use a potion card to heal the player."""

        self.playing_state.change_health(potion.value)

        self.playing_state.room.remove_card(potion)

        self.playing_state.animate_card_to_discard(potion)

        if len(self.playing_state.room.cards) > 0:

            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def add_to_inventory(self, card):
        """Add a card to the player's inventory if space is available."""
        if len(self.playing_state.inventory) >= self.playing_state.MAX_INVENTORY_SIZE:

            return False

        card.is_selected = True

        card.in_inventory = True

        self.playing_state.room.remove_card(card)

        self.playing_state.inventory.append(card)

        self.playing_state.animate_card_to_inventory(card)

        if len(self.playing_state.room.cards) > 0:
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

        return True

    def use_inventory_card(self, card, event_pos=None):
        """Use a card from the inventory with optional click position to determine action."""
        if card in self.playing_state.inventory:

            card.is_selected = True

            discard_only = False

            if event_pos:

                center_x = card.rect.centerx

                total_float_offset = 0
                if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                    total_float_offset = card.idle_float_offset + card.hover_float_offset

                center_y = card.rect.centery - total_float_offset

                if event_pos[1] < center_y:

                    discard_only = True
                    card.hover_selection = "top"
                else:

                    discard_only = False
                    card.hover_selection = "bottom"

            card.in_inventory = False

            self.playing_state.inventory.remove(card)

            self.playing_state.position_inventory_cards()

            if card.type == "weapon":
                if discard_only:

                    self.playing_state.show_message(f"{card.name} discarded")

                    self.playing_state.animate_card_to_discard(card)
                else:

                    card.update_scale(1.0)

                    self.playing_state.room.add_card(card)

                    self.equip_weapon(card)
            elif card.type == "potion":
                if discard_only:

                    self.playing_state.show_message(f"{card.name} discarded")

                    self.playing_state.animate_card_to_discard(card)
                else:

                    self.playing_state.change_health(card.value)

                    self.playing_state.show_message(f"Used {card.name}. Restored {card.value} health.")

                    self.playing_state.animate_card_to_discard(card)
            else:

                self.playing_state.show_message(f"{card.name} discarded")
                self.playing_state.animate_card_to_discard(card)

    def discard_equipped_weapon(self):
        """Discard the currently equipped weapon."""
        if self.playing_state.equipped_weapon and "node" in self.playing_state.equipped_weapon:
            weapon = self.playing_state.equipped_weapon["node"]

            self.playing_state.equipped_weapon = {}

            weapon.is_equipped = False

            self.playing_state.show_message(f"{weapon.name} discarded")

            self.playing_state.animate_card_to_discard(weapon)

            for monster in self.playing_state.defeated_monsters:
                self.playing_state.animate_card_to_discard(monster)

            self.playing_state.defeated_monsters = []

            return True
        return False
