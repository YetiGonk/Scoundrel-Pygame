"""Card Action Manager for processing card actions in the Scoundrel game."""
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, WHITE


class CardActionManager:
    """Manages card-related actions such as attacking monsters, using equipment, and potions."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
        
    def resolve_card(self, card, event_pos=None):
        """Process a card that has been clicked by the player."""
        # Can only resolve cards that are face up and not flipping
        if (not card.face_up or card.is_flipping or 
                self.playing_state.animation_manager.is_animating()):
            return
        
        # Reset the ran_last_turn flag
        self.playing_state.ran_last_turn = False
        
        # Mark the card as selected to remove split colours
        card.is_selected = True
        
        # For inventory cards, determine which part was clicked
        if card.can_add_to_inventory and event_pos:
            # Check if inventory is available
            inventory_is_full = len(self.playing_state.inventory) >= self.playing_state.MAX_INVENTORY_SIZE
            card.inventory_available = not inventory_is_full
            
            # Calculate position of the card's visual midpoint
            # This takes into account the card's current drawing position 
            # including floating and scaling effects
            
            # Get card's current visual position (centered around middle)
            center_x = card.rect.centerx 
            
            # For the Y position, we need to account for the float offset
            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset
            
            # Calculate center Y with float offset
            center_y = card.rect.centery - total_float_offset
            
            # Check if inventory is available and if click is above midpoint
            if not inventory_is_full and event_pos[1] < center_y:
                # Top half clicked with available inventory - add to inventory
                self.add_to_inventory(card)
                return
            # Bottom half clicked or inventory full - continue to use the card normally
        
        # For monster cards, determine attack method
        elif card.can_show_attack_options and event_pos:
            # Calculate position of the card's visual midpoint
            center_x = card.rect.centerx 
            
            # For the Y position, we need to account for the float offset
            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset
            
            # Calculate center Y with float offset
            center_y = card.rect.centery - total_float_offset
            
            # Check if weapon is available
            if card.weapon_available:
                # With weapon available, check which half was clicked
                if event_pos[1] < center_y:
                    # Top half clicked - attack with weapon
                    self.attack_monster(card)
                    return
                else:
                    # Bottom half clicked - attack bare-handed
                    self.attack_barehanded(card)
                    return
            else:
                # No weapon available - always attack bare-handed
                self.attack_barehanded(card)
                return
        
        # Process card effects based on type (if no specific half was clicked)
        if card.type == "monster":
            # Default to bare-handed if no specific half was clicked
            self.attack_barehanded(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)
    
    
    def attack_barehanded(self, monster):
        """Process player attacking a monster card with bare hands (takes full damage)."""
        # Calculate monster value - apply any effect from items or spells
        monster_value = monster.value
        
        # Use damage shield if available
        damage_reduction = 0
        if self.playing_state.damage_shield > 0:
            damage_reduction = min(self.playing_state.damage_shield, monster_value)
            monster_value -= damage_reduction
            self.playing_state.damage_shield -= damage_reduction
        
        # First ensure the monster is removed from the room before animations start
        self.playing_state.room.remove_card(monster)
        
        # Take full damage from monster
        if monster_value > 0:
            self.playing_state.change_health(-monster_value)
        
        # Animate to discard pile
        self.playing_state.animate_card_to_discard(monster)
        
        # Show message about bare-handed attack
        self.playing_state.show_message(f"Attacked {monster.name} bare-handed! Took full damage.")
        
        # After processing the monster, reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            # Add a slight delay before repositioning room cards
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True, 
                    animation_manager=self.playing_state.animation_manager
                )
            )
        
        # After attack is complete, update interface
        self.playing_state.ui_factory.create_item_buttons()
        self.playing_state.ui_factory.create_spell_buttons()
    
    def attack_monster(self, monster):
        """Process player attacking a monster card with equipped weapon."""
        # Calculate monster value - apply any effect from items or spells
        monster_value = monster.value
        
        # Use damage shield if available
        damage_reduction = 0
        if self.playing_state.damage_shield > 0:
            damage_reduction = min(self.playing_state.damage_shield, monster_value)
            monster_value -= damage_reduction
            self.playing_state.damage_shield -= damage_reduction

        # First ensure the monster is removed from the room before animations start
        self.playing_state.room.remove_card(monster)
        
        # Check if player has a weapon equipped
        if self.playing_state.equipped_weapon:
            weapon_node = self.playing_state.equipped_weapon.get("node", None)
            weapon_value = self.playing_state.equipped_weapon.get("value", 0)
            
            # Check if it's a ranged weapon and if player has arrows
            has_arrow = False
            arrow_card = None
            
            # Only check for arrows if the equipped weapon is ranged
            if weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged":
                # Look for arrow cards in inventory
                for card in self.playing_state.inventory:
                    if (hasattr(card, "weapon_type") and card.weapon_type == "arrow") or \
                       (card.type == "weapon" and card.value == 2):  # 2 of diamonds is arrow
                        has_arrow = True
                        arrow_card = card
                        break
            
            # Handle ranged weapon with arrow
            if weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged" and has_arrow:
                # Keep arrows in inventory - do not consume them
                
                # With ranged weapon + arrow, you don't take damage if monster value > weapon value
                if monster_value <= weapon_value:
                    # Monster defeated with no damage
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1
                    # Add to defeated monster stack
                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:
                    # Monster escapes but no damage taken (ranged weapon benefit)
                    # Animate to discard pile
                    self.playing_state.animate_card_to_discard(monster)
                    
                    # Show message that ranged attack missed but no damage taken
                    self.playing_state.show_message("Ranged attack missed! No damage taken.")
            
            # Handle ranged weapon without arrow (use as melee with no weapon value)
            elif weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged" and not has_arrow:
                # Show message about missing arrows
                self.playing_state.show_message("No arrows! Fighting with bare hands.")
                
                # Take full damage from monster (as if no weapon)
                if monster_value > 0:
                    self.playing_state.change_health(-monster_value)
                
                # Monster defeats player (add to discard)
                self.playing_state.animate_card_to_discard(monster)
            
            # Normal melee weapon combat
            else:
                # Monster will be added to stack or discard
                if self.playing_state.defeated_monsters:
                    if self.playing_state.defeated_monsters[-1].value > monster_value:
                        damage = monster_value - weapon_value
                        if damage < 0:
                            damage = 0
                        
                        # Apply damage with animation
                        if damage > 0:
                            self.playing_state.change_health(-damage)
                        
                        monster.z_index = self.playing_state.z_index_counter
                        self.playing_state.z_index_counter += 1
                        
                        # Add to defeated monster stack
                        self.playing_state.defeated_monsters.append(monster)
                        self.playing_state.position_monster_stack()
                    else:
                        # Apply damage with animation
                        if monster_value > 0:
                            self.playing_state.change_health(-monster_value)
                        
                        # Animate to discard pile
                        self.playing_state.animate_card_to_discard(monster)
                else:
                    if monster_value <= weapon_value:
                        monster.z_index = self.playing_state.z_index_counter
                        self.playing_state.z_index_counter += 1
                        # Add to defeated monster stack
                        self.playing_state.defeated_monsters.append(monster)
                        self.playing_state.position_monster_stack()
                    else:
                        damage = monster_value - weapon_value
                        if damage < 0:
                            damage = 0
                        
                        # Apply damage with animation
                        if damage > 0:
                            self.playing_state.change_health(-damage)
                        
                        monster.z_index = self.playing_state.z_index_counter
                        self.playing_state.z_index_counter += 1
                        # Add to defeated monster stack
                        self.playing_state.defeated_monsters.append(monster)
                        self.playing_state.position_monster_stack()
        else:
            # No weapon equipped - take full damage
            # Apply damage with animation
            if monster_value > 0:
                self.playing_state.change_health(-monster_value)
            
            # Animate to discard pile
            self.playing_state.animate_card_to_discard(monster)
                
        # After processing the monster, reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            # Add a slight delay before repositioning room cards
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True, 
                    animation_manager=self.playing_state.animation_manager
                )
            )
        
        # After attack is complete, update interface
        self.playing_state.ui_factory.create_item_buttons()
        self.playing_state.ui_factory.create_spell_buttons()
    
    def equip_weapon(self, weapon):
        """Equip a weapon card."""
        # Check if the card is an arrow (can't be equipped as a weapon)
        if hasattr(weapon, "weapon_type") and weapon.weapon_type == "arrow":
            # Add arrow to inventory instead of equipping
            self.add_to_inventory(weapon)
            self.playing_state.show_message("Arrows added to inventory")
            return
        
        # First clear previous weapon and monsters
        old_weapon = self.playing_state.equipped_weapon.get("node", None)
        old_monsters = self.playing_state.defeated_monsters.copy()
        
        # Update data structures first
        self.playing_state.room.remove_card(weapon)
        
        # Store weapon type in the equipped_weapon dict
        weapon_type = getattr(weapon, "weapon_type", "melee")  # Default to melee if not specified
        self.playing_state.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon,
            "weapon_type": weapon_type
        }
        self.playing_state.defeated_monsters = []
        
        # Set z-index for new weapon
        weapon.z_index = self.playing_state.z_index_counter
        self.playing_state.z_index_counter += 1
        
        # Animate new weapon equipping first
        from constants import WEAPON_POSITION
        self.playing_state.animate_card_movement(weapon, WEAPON_POSITION)
        
        # Show appropriate message based on weapon type
        if weapon_type == "ranged":
            has_arrow = any(card.weapon_type == "arrow" for card in self.playing_state.inventory if hasattr(card, "weapon_type"))
            if has_arrow:
                self.playing_state.show_message(f"Equipped {weapon.name}. Arrows ready! (Reusable)")
            else:
                self.playing_state.show_message(f"Equipped {weapon.name}. No arrows available!")
        else:
            self.playing_state.show_message(f"Equipped {weapon.name}")
        
        # Now discard old weapon and monsters
        if old_weapon or old_monsters:
            for i, monster in enumerate(old_monsters):
                # Add a slight delay for each monster
                delay = 0.08 * i
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=monster: self.playing_state.animate_card_to_discard(card)
                )
            
            # Discard old weapon last if it exists
            if old_weapon:
                delay = 0.08 * len(old_monsters)
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda: self.playing_state.animate_card_to_discard(old_weapon)
                )
    
    def use_potion(self, potion):
        """Use a potion card to heal the player."""
        # Apply healing with animation
        self.playing_state.change_health(potion.value)
        
        # First ensure the potion is removed from the room
        self.playing_state.room.remove_card(potion)
        
        # Animate potion moving to discard pile
        self.playing_state.animate_card_to_discard(potion)
        
        # After processing the potion, reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            # Add a slight delay before repositioning room cards
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
            # Inventory is full, can't add more cards
            return False
        
        # Mark the card as selected to remove split colours
        card.is_selected = True
        
        # Mark the card as being in inventory to reduce animation
        card.in_inventory = True
        
        # Remove the card from the room
        self.playing_state.room.remove_card(card)
        
        # Add to inventory
        self.playing_state.inventory.append(card)
        
        # Animate the card moving to its inventory position
        self.playing_state.animate_card_to_inventory(card)
        
        # Reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True, 
                    animation_manager=self.playing_state.animation_manager
                )
            )
        
        return True
    
    def use_inventory_card(self, card):
        """Use a card from the inventory."""
        if card in self.playing_state.inventory:
            # Mark the card as selected to ensure no split colours
            card.is_selected = True
            
            # Reset inventory flag since it's being removed
            card.in_inventory = False
            
            # Remove from inventory
            self.playing_state.inventory.remove(card)
            
            # Reposition remaining inventory cards
            self.playing_state.position_inventory_cards()
            
            # Process the card effect based on type
            if card.type == "weapon":
                # Special case for arrows - just discard them
                if hasattr(card, "weapon_type") and card.weapon_type == "arrow":
                    # Show message about discarding arrow
                    self.playing_state.show_message("Arrow discarded")
                    # Discard the arrow
                    self.playing_state.animate_card_to_discard(card)
                else:
                    # Reset the card's scale back to original size (1.0)
                    card.update_scale(1.0)
                    # Add the card back to the room temporarily
                    self.playing_state.room.add_card(card)
                    # Use the standard equip weapon logic
                    self.equip_weapon(card)
            elif card.type == "potion":
                # Use the potion effect directly
                self.playing_state.change_health(card.value)
                # Discard the potion
                self.playing_state.animate_card_to_discard(card)
            else:
                # For any other card type that doesn't have a specific use
                # Just discard it when clicked
                self.playing_state.show_message(f"{card.name} discarded")
                self.playing_state.animate_card_to_discard(card)
                
            return True
        return False