"""Card Action Manager for processing card actions in the Scoundrel game."""
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, WHITE


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
        
        # For inventory cards, determine which part was clicked
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
                    # Mark monster as defeated for proper hover behavior
                    monster.is_defeated = True
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
                    # Mark monster as defeated for proper hover behavior
                    monster.is_defeated = True
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
    
    def equip_weapon(self, weapon):
        """Equip a weapon card."""
        
        # First clear previous weapon and monsters
        old_weapon = self.playing_state.equipped_weapon.get("node", None)
        old_monsters = self.playing_state.defeated_monsters.copy()
        
        # Update data structures first
        self.playing_state.room.remove_card(weapon)
        
        # Mark the weapon as equipped (for hover text)
        weapon.is_equipped = True
        
        # Store weapon type in the equipped weapon dictionary
        self.playing_state.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon,
            "difficulty": weapon.weapon_difficulty,
        }
        self.playing_state.defeated_monsters = []
        
        # Set z-index for new weapon
        weapon.z_index = self.playing_state.z_index_counter
        self.playing_state.z_index_counter += 1
        
        # Animate new weapon equipping first
        from constants import WEAPON_POSITION
        self.playing_state.animate_card_movement(weapon, WEAPON_POSITION)
        
        # Show standard equipped message
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
    
    def use_inventory_card(self, card, event_pos=None):
        """Use a card from the inventory with optional click position to determine action."""
        if card in self.playing_state.inventory:
            # Temporarily mark the card as selected during processing
            card.is_selected = True
            
            # Default action is to use the card (equip weapon or use potion)
            discard_only = False
            
            # If click position is provided, determine which part was clicked
            if event_pos:
                # Calculate position of the card's visual midpoint
                center_x = card.rect.centerx 
                
                # For the Y position, we need to account for the float offset
                total_float_offset = 0
                if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                    total_float_offset = card.idle_float_offset + card.hover_float_offset
                
                # Calculate center Y with float offset
                center_y = card.rect.centery - total_float_offset
                
                # Check which half was clicked
                if event_pos[1] < center_y:
                    # Top half clicked - discard card
                    discard_only = True
                    card.hover_selection = "top"
                else:
                    # Bottom half clicked - use card (equip weapon or use potion)
                    discard_only = False
                    card.hover_selection = "bottom"
            
            # Reset inventory flag since it's being removed
            card.in_inventory = False
            
            # Remove from inventory
            self.playing_state.inventory.remove(card)
            
            # Reposition remaining inventory cards
            self.playing_state.position_inventory_cards()
            
            # Process the card effect based on type and action
            if card.type == "weapon":
                if discard_only:
                    # Show message about discarding
                    self.playing_state.show_message(f"{card.name} discarded")
                    # Discard the card
                    self.playing_state.animate_card_to_discard(card)
                else:
                    # Reset the card's scale back to original size (1.0)
                    card.update_scale(1.0)
                    # Add the card back to the room temporarily
                    self.playing_state.room.add_card(card)
                    # Use the standard equip weapon logic
                    self.equip_weapon(card)
            elif card.type == "potion":
                if discard_only:
                    # Show message about discarding potion
                    self.playing_state.show_message(f"{card.name} discarded")
                    # Discard the potion
                    self.playing_state.animate_card_to_discard(card)
                else:
                    # Use the potion effect directly
                    self.playing_state.change_health(card.value)
                    # Show message about using potion
                    self.playing_state.show_message(f"Used {card.name}. Restored {card.value} health.")
                    # Discard the potion
                    self.playing_state.animate_card_to_discard(card)
            else:
                # For any other card type that doesn't have a specific use
                # Just discard it when clicked
                self.playing_state.show_message(f"{card.name} discarded")
                self.playing_state.animate_card_to_discard(card)
    
    def discard_equipped_weapon(self):
        """Discard the currently equipped weapon."""
        if self.playing_state.equipped_weapon and "node" in self.playing_state.equipped_weapon:
            weapon = self.playing_state.equipped_weapon["node"]
            
            # Clear the equipped weapon
            self.playing_state.equipped_weapon = {}
            
            # Reset equipped flag
            weapon.is_equipped = False
            
            # Show message about discarding weapon
            self.playing_state.show_message(f"{weapon.name} discarded")
            
            # Discard the weapon card
            self.playing_state.animate_card_to_discard(weapon)
            
            # Also discard any defeated monsters
            for monster in self.playing_state.defeated_monsters:
                self.playing_state.animate_card_to_discard(monster)
            
            # Clear the defeated monsters list
            self.playing_state.defeated_monsters = []
            
            return True
        return False