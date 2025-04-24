"""Animation Controller for managing animations in the Scoundrel game."""
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT, INVENTORY_PANEL_X, INVENTORY_PANEL_Y, FLOOR_WIDTH

from utils.animation import (
    Animation, MoveAnimation, DestructionAnimation, MaterializeAnimation, 
    HealthChangeAnimation, GoldChangeAnimation, EasingFunctions
)


class AnimationController:
    """Manages all animations in the game."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
    
    def animate_card_to_discard(self, card):
        """Animate a card being destroyed and appearing in the discard pile."""
        # First create a destruction animation
        
        # Choose a random destruction effect based on card type
        if card.type == "monster":
            effect_type = "slash"  # Monsters get slashed
        elif card.type == "weapon":
            effect_type = "shatter"  # Weapons shatter
        elif card.type == "potion":
            effect_type = "burn"  # Potions burn away
        else:
            effect_type = random.choice(["slash", "burn", "shatter"])
            
        destroy_anim = DestructionAnimation(
            card,
            effect_type,
            duration=0.5,
            on_complete=lambda: self.materialize_card_at_discard(card)
        )
        
        self.playing_state.animation_manager.add_animation(destroy_anim)
    
    def materialize_card_at_discard(self, card):
        """Materialize the card at the discard pile position."""
        # Update card position to discard pile
        card.update_position(self.playing_state.discard_pile.position)
        
        # Create materialize animation
        materialize_anim = MaterializeAnimation(
            card,
            self.playing_state.discard_pile.position,
            effect_type="sparkle",
            duration=0.3,
            on_complete=lambda: self.playing_state.room_manager.remove_and_discard(card)
        )
        
        self.playing_state.animation_manager.add_animation(materialize_anim)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, 
        on_complete=None):
        """Create a simple, direct animation for card movement with optional callback."""
        if easing is None:
            easing = EasingFunctions.ease_out_quad
        
        animation = MoveAnimation(
            card,
            card.rect.topleft,
            target_pos,
            duration,
            easing,
            on_complete
        )
        
        self.playing_state.animation_manager.add_animation(animation)

    def position_monster_stack(self):
        """Position defeated monsters in a stack."""
        if not self.playing_state.defeated_monsters or "node" not in self.playing_state.equipped_weapon:
            return
            
        from constants import MONSTER_STACK_OFFSET, MONSTER_START_OFFSET
        total_width = MONSTER_STACK_OFFSET[0] * (len(self.playing_state.defeated_monsters) - 1)
        start_x = self.playing_state.equipped_weapon["node"].rect.x + MONSTER_START_OFFSET[0]
        
        for i, monster in enumerate(self.playing_state.defeated_monsters):
            new_stack_position = (
                start_x + i * MONSTER_STACK_OFFSET[0],
                self.playing_state.equipped_weapon["node"].rect.y + MONSTER_STACK_OFFSET[1] * i
            )
            self.animate_card_movement(monster, new_stack_position)

        new_weapon_position = (
            self.playing_state.equipped_weapon["node"].rect.x - MONSTER_STACK_OFFSET[1]*2,
            self.playing_state.equipped_weapon["node"].rect.y
        )
        self.animate_card_movement(self.playing_state.equipped_weapon["node"], new_weapon_position)
    
    def schedule_delayed_animation(self, delay, callback):
        """Schedule an animation to start after a delay."""
        # Add a "timer" animation that does nothing except wait
        # When it completes, it will run the callback to create the real animation
        timer = Animation(delay, on_complete=callback)
        self.playing_state.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        """Start the flip animation for a card."""
        card.start_flip()
    
    def animate_health_change(self, is_damage, amount):
        """Create animation for health change."""
        # Position for the animation
        health_display_x = self.playing_state.deck.rect.x + 100  # Center of health bar
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y - 30  # Middle of health bar
        
        # Create animation
        health_anim = HealthChangeAnimation(
            is_damage,
            amount,
            (health_display_x, health_display_y),
            self.playing_state.body_font
        )
        
        # Add to animation manager
        self.playing_state.animation_manager.add_animation(health_anim)
    
    def animate_gold_change(self, is_loss, amount):
        """Create animation for gold change."""
        # Load the gold icon to get dimensions
        from utils.resource_loader import ResourceLoader
        gold_icon = ResourceLoader.load_image("ui/gold.png")
        icon_width = gold_icon.get_width()
        icon_height = gold_icon.get_height()
        
        # Position for the animation - next to the gold display
        health_display_x = 40
        gold_display_x = health_display_x + icon_width + 30  # Center over gold amount text
        gold_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y - 100 + icon_height//2  # Match gold icon position
        
        # Create animation
        gold_anim = GoldChangeAnimation(
            is_loss,
            amount,
            (gold_display_x, gold_display_y),
            self.playing_state.body_font
        )
        
        # Add to animation manager
        self.playing_state.animation_manager.add_animation(gold_anim)
    
    def animate_card_to_inventory(self, card):
        """Animate a card moving to its position in the inventory."""
        # Define inventory panel location - match the dimensions in playing_state.py
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Use standard card size (no scaling) for inventory cards
        card_scale = 1.0
        
        # Scale the card
        card.update_scale(card_scale)
        
        # Mark card as being in inventory to reduce animations
        card.in_inventory = True
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Center X position (horizontally centered in panel)
        inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)
        
        # Get number of cards in inventory (including this new one)
        num_cards = len(self.playing_state.inventory)
        
        # Calculate Y position based on number of cards
        if num_cards == 1:
            # Single card - center vertically in panel
            inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
        elif num_cards == 2:
            # If this is the second card, position cards one above center, one below center
            # Reposition existing card to top position
            existing_card = self.playing_state.inventory[0]
            top_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
            
            # Only reposition if it's not already at the right position
            if existing_card.rect.y != top_y:
                self.animate_card_movement(existing_card, (inventory_x, top_y))
            
            # Position new card in bottom half
            inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)
        
        inventory_pos = (inventory_x, inventory_y)
        
        # Animate the card movement
        self.animate_card_movement(card, inventory_pos, on_complete=lambda: self.playing_state.position_inventory_cards())