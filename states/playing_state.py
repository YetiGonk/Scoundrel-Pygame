""" Playing state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, WHITE, BLACK, LIGHT_GRAY
from components.card import Card
from components.deck import Deck
from components.discard_pile import DiscardPile
from components.room import Room
from states.game_state import GameState
from ui.button import Button
from utils.resource_loader import ResourceLoader
from utils.animation import Animation, AnimationManager, MoveAnimation, EasingFunctions

class PlayingState(GameState):
    """The main gameplay state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # Game components
        self.deck = None
        self.discard_pile = None
        self.room = None
        
        # Player stats
        self.life_points = 20
        self.max_life = 20
        self.equipped_weapon = {}
        self.defeated_monsters = []
        
        # Animation
        self.animation_manager = AnimationManager()
        self.is_running = False
        self.ran_last_turn = False
        
        # UI elements
        self.header_font = None
        self.body_font = None
        self.run_button = None
        self.background = None
        self.floor = None

        # State variables
        self.show_debug = False

        # Layer management
        self.z_index_counter = 0

    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)

        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load floor
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        # Initialize game components
        self.deck = Deck()
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        # Create run button
        from constants import RUN_POSITION, RUN_WIDTH, RUN_HEIGHT
        run_button_rect = pygame.Rect(RUN_POSITION[0], RUN_POSITION[1], RUN_WIDTH, RUN_HEIGHT)
        self.run_button = Button(run_button_rect, "RUN", self.body_font)

        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
        self.equipped_weapon = {}
        self.defeated_monsters = []

        # Initialize the deck and start the first room
        self.deck.initialise_deck()
        self.start_new_room()
    
    def exit(self):
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life
    
    def handle_event(self, event):
        if self.animation_manager.is_animating():
            return  # Don't handle events while animating
        
        if event.type == MOUSEMOTION:
            # Check hover for cards in the room
            for card in self.room.cards:
                card.check_hover(event.pos)
            
            # Check hover for run button
            self.run_button.check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.life_points <= 0:
                return  # Don't handle clicks if player is dead
            
            # Check if run button was clicked
            if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
                self.run_from_room()
                return
            
            # Check if a card was clicked
            card = self.room.get_card_at_position(event.pos)
            if card:
                self.resolve_card(card)
    
    def update(self, delta_time):
        # Update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update card flip animations
        for card in self.room.cards:
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # If we were running and animations finished, complete the run
        if self.is_running and animations_just_finished:
            self.on_run_completed()
        
        # If we have only one card left and animations just finished, start a new room
        elif len(self.room.cards) == 1 and animations_just_finished:
            self.start_new_room(self.room.cards[0])
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw deck first
        self.deck.draw(surface)
        
        # Draw discard pile
        self.discard_pile.draw(surface)
        
        # Draw equipped weapon and defeated monsters
        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].draw(surface)
            for monster in self.defeated_monsters:
                monster.draw(surface)
        
        # Draw room cards LAST always
        self.room.draw(surface)
        
        # Draw health
        health_text = self.header_font.render(str(self.life_points), True, WHITE)
        health_rect = health_text.get_rect(topleft=(75, 527))
        surface.blit(health_text, health_rect)
        
        # Draw run button
        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:
            # Draw disabled run button
            button_rect = self.run_button.rect
            pygame.draw.rect(surface, LIGHT_GRAY, button_rect)
            pygame.draw.rect(surface, BLACK, button_rect, 2)
            button_text = self.body_font.render("RUN", True, (150, 150, 150))  # Grayed out text
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)

    def start_new_room(self, last_card=None):
        if len(self.deck.cards) < 4:
            self.end_game(True)
            return
        
        if self.life_points <= 0:
            return
        
        if self.animation_manager.is_animating():
            return  # Don't start a new room if animations are running
        
        # Clear the room
        self.room.clear()
        
        # Keep the last card if provided
        if last_card:
            self.room.add_card(last_card)
            last_card.face_up = True
        
        # Calculate how many cards to draw
        cards_to_draw = 4 - len(self.room.cards)
        
        # Calculate final target positions first
        num_cards = 4  # Always 4 cards in a full room
        total_width = (CARD_WIDTH * num_cards) + (self.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
        
        target_positions = []
        for i in range(num_cards):
            target_positions.append((
                int(start_x + i * (CARD_WIDTH + self.room.card_spacing)),
                int(start_y)
            ))
        
        # Draw cards one by one with animations
        for i in range(cards_to_draw):
            if self.deck.cards:
                card_data = self.deck.draw_card()
                card = Card(card_data["suit"], card_data["value"])
                
                # Cards start face down
                card.face_up = False
                
                # Set the initial position to the top of the deck
                if self.deck.card_stack:
                    card.update_position(self.deck.card_stack[-1])
                else:
                    card.update_position(self.deck.position)
                
                # Add card to room (this won't position cards yet)
                self.room.add_card(card)
                
                # Calculate which target position to use
                if last_card:
                    target_pos = target_positions[i + 1]  # Skip position 0 for last_card
                else:
                    target_pos = target_positions[i]
                
                # Create animation to move card to position with staggered timing
                delay = 0.1 * i  # Stagger the dealing animations
                
                # Create a delayed animation
                self.schedule_delayed_animation(
                    delay,
                    lambda card=card, pos=target_pos: self.animate_card_movement(
                        card, 
                        pos, 
                        duration=0.3,
                        on_complete=lambda c=card: self.start_card_flip(c)
                    )
                )
        
        # Update deck display
        if self.deck.card_stack:
            for i in range(cards_to_draw):
                if self.deck.card_stack:
                    self.deck.card_stack.pop()
        self.deck.initialise_visuals()

    def schedule_delayed_animation(self, delay, callback):
        """Schedule an animation to start after a delay"""
        # Add a "timer" animation that does nothing except wait
        # When it completes, it will run the callback to create the real animation
        from utils.animation import Animation
        timer = Animation(delay, on_complete=callback)
        self.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        card.start_flip()
        
    def resolve_card(self, card):
        # Can only resolve cards that are face up and not flipping
        if not card.face_up or card.is_flipping or self.animation_manager.is_animating():
            return
        
        # Reset the ran_last_turn flag
        self.ran_last_turn = False
        
        # Create a copy of the card for animation purposes
        card_copy = None
        if card.type == "monster" and self.equipped_weapon:
            # Only for monsters that will be stacked
            card_copy = card
        
        # Process card effects based on type
        if card.type == "monster":
            self.attack_monster(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)
        
        # Only remove the card from the room if we're not animating it
        if card != card_copy:
            self.room.remove_card(card)
        
        # Animate remaining cards to new positions
        self.room.position_cards(animate=True, animation_manager=self.animation_manager)

    def attack_monster(self, monster):
        if self.equipped_weapon:
            # Monster will be added to stack or discard
            if self.defeated_monsters:
                if self.defeated_monsters[-1].value > monster.value:
                    damage = monster.value - self.equipped_weapon["value"]
                    if damage < 0:
                        damage = 0
                    if damage > self.life_points:
                        damage = self.life_points
                    self.life_points -= damage
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    
                    # Add to defeated monsters AFTER removing from room
                    self.room.remove_card(monster)
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                    self.check_game_over()
                else:
                    if monster.value > self.life_points:
                        self.life_points = 0
                    else:
                        self.life_points -= monster.value
                    self.check_game_over()
                    # Add to discard AFTER removing from room
                    self.room.remove_card(monster)
                    self.discard_pile.add_card(monster)
            else:
                if monster.value <= self.equipped_weapon["value"]:
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    # Add to defeated monsters AFTER removing from room
                    self.room.remove_card(monster)
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                else:
                    damage = monster.value - self.equipped_weapon["value"]
                    if damage < 0:
                        damage = 0
                    if damage > self.life_points:
                        damage = self.life_points
                    self.life_points -= damage
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    # Add to defeated monsters AFTER removing from room
                    self.room.remove_card(monster)
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                    self.check_game_over()
        else:
            if monster.value > self.life_points:
                self.life_points = 0
            else:
                self.life_points -= monster.value
            # Add to discard AFTER removing from room
            self.room.remove_card(monster)
            self.discard_pile.add_card(monster)
            self.check_game_over()

    def add_to_defeated_monsters(self, monster):
        """Callback after animation to actually add monster to defeated stack"""
        monster.z_index = self.z_index_counter
        self.z_index_counter += 1
        self.defeated_monsters.append(monster)

    def calculate_monster_stack_position(self, index):
        """Calculate position for a monster in the defeated monster stack"""
        if not self.equipped_weapon or "node" not in self.equipped_weapon:
            # Default position if no weapon equipped
            from constants import WEAPON_POSITION
            weapon_pos = WEAPON_POSITION
        else:
            weapon_pos = self.equipped_weapon["node"].rect.topleft
        
        monster_start_offset = (150, 0)
        monster_stack_offset = (30, 10)
        
        return (
            weapon_pos[0] + monster_start_offset[0] + index * monster_stack_offset[0],
            weapon_pos[1] + index * monster_stack_offset[1]
        )

    def position_monster_stack(self):
        if not self.defeated_monsters or "node" not in self.equipped_weapon:
            return
            
        monster_start_offset = (150, 0)
        monster_stack_offset = (30, 10)
        total_width = monster_stack_offset[0] * (len(self.defeated_monsters) - 1)
        start_x = self.equipped_weapon["node"].rect.x + monster_start_offset[0] - total_width / 2
        
        weapon_adjustment = (-total_width / 2, 0)
        weapon_pos = (self.equipped_weapon["node"].rect.x + weapon_adjustment[0], 
            self.equipped_weapon["node"].rect.y + weapon_adjustment[1]
        )
        self.equipped_weapon["node"].update_position(weapon_pos)
        
        for i, monster in enumerate(self.defeated_monsters):
            stack_position = (
                start_x + i * monster_stack_offset[0],
                self.equipped_weapon["node"].rect.y + monster_stack_offset[1] * i
            )
            monster.update_position(stack_position)
    
    def equip_weapon(self, weapon):
        self.clear_weapon_and_monsters()
        
        self.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon
        }
        
        weapon.z_index = self.z_index_counter
        self.z_index_counter += 1
        
        # Animate weapon equipping with a flourish
        from constants import WEAPON_POSITION
        self.animate_card_movement(weapon, WEAPON_POSITION)
    
    def clear_weapon_and_monsters(self):
        """Discard the equipped weapon and all defeated monsters"""
        # Animate all monsters moving to the discard pile
        for monster in self.defeated_monsters:
            self.animate_card_to_discard(monster)
        
        # Clear the defeated_monsters list
        self.defeated_monsters.clear()
        
        # Animate the weapon moving to the discard pile
        if "node" in self.equipped_weapon:
            self.animate_card_to_discard(self.equipped_weapon["node"])
            self.equipped_weapon = {}
    
    def use_potion(self, potion):
        # Update health points
        self.life_points = min(self.life_points + potion.value, self.max_life)
        
        # Animate potion moving to discard pile
        self.animate_card_to_discard(potion)
        
    def animate_card_to_discard(self, card):
        """Animate a card moving to the discard pile with a spin effect"""
        # Get discard pile position
        discard_pos = self.discard_pile.position
        
        # Calculate a slightly elevated position for the arc
        mid_height = -100  # Higher than both start and end
        
        # Create an arc animation with rotation
        self.animate_card_arc(
            card, 
            discard_pos, 
            mid_height,
            duration=0.6,
            rotation_end=360,  # Full spin
            on_complete=lambda: self.discard_pile.add_card(card)
        )

    def animate_card_arc(self, card, target_pos, arc_height, duration=0.5, 
                        rotation_start=0, rotation_end=0, scale_start=1.0, scale_end=1.0,
                        on_complete=None):
        """Animate a card in an arc trajectory with rotation and scaling"""
        start_pos = card.rect.topleft
        
        # Custom animation class for arc movement
        class ArcAnimation(Animation):
            def __init__(self, card, start_pos, target_pos, arc_height, duration, 
                        rotation_start, rotation_end, scale_start, scale_end, on_complete=None):
                super().__init__(duration, on_complete)
                self.card = card
                self.start_pos = start_pos
                self.target_pos = target_pos
                self.arc_height = arc_height
                self.rotation_start = rotation_start
                self.rotation_end = rotation_end
                self.scale_start = scale_start
                self.scale_end = scale_end
                
                # Initialize rotation and scale
                if hasattr(card, 'rotation'):
                    self.card.rotation = rotation_start
                if hasattr(card, 'scale'):
                    self.card.scale = scale_start
                    self.card.update_scale(scale_start)
            
            def update(self, delta_time):
                completed = super().update(delta_time)
                
                # Get normalized progress (0.0 to 1.0)
                progress = self.get_progress()
                
                # Calculate horizontal position (linear)
                x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * progress
                
                # Calculate vertical position (parabolic arc)
                # Use a parabola that peaks at the middle of the animation
                y_start = self.start_pos[1]
                y_end = self.target_pos[1]
                
                # Quadratic function: y = a*t^2 + b*t + c where t is progress (0 to 1)
                # When t=0, y=start_y
                # When t=1, y=end_y
                # When t=0.5, y=peak_y (which is min_y plus arc_height)
                
                # Solve for a, b, c
                # Simplified parabola for arc trajectory: y = 4*h*t*(1-t) + start*(1-t) + end*t
                # Where h is the height difference from the straight line
                
                # Calculate linear interpolation between start and end
                linear_y = y_start * (1 - progress) + y_end * progress
                
                # Calculate parabolic arc component (maximum at progress = 0.5)
                arc_component = 4 * self.arc_height * progress * (1 - progress)
                
                # Combine to get final y position
                y = linear_y - arc_component  # Subtract because negative is up in PyGame
                
                # Update card position
                self.card.update_position((int(x), int(y)))
                
                # Update rotation
                if hasattr(self.card, 'rotation') and self.rotation_start != self.rotation_end:
                    current_rotation = self.rotation_start + (self.rotation_end - self.rotation_start) * progress
                    self.card.rotation = current_rotation
                    
                    # Apply rotation if the card has a rotate method
                    if hasattr(self.card, 'rotate'):
                        self.card.rotate(current_rotation)
                
                # Update scale
                if hasattr(self.card, 'scale') and self.scale_start != self.scale_end:
                    current_scale = self.scale_start + (self.scale_end - self.scale_start) * progress
                    
                    # Apply scaling
                    if hasattr(self.card, 'update_scale'):
                        self.card.update_scale(current_scale)
                
                return completed
        
        # Create and add the animation
        animation = ArcAnimation(
            card, start_pos, target_pos, arc_height, duration,
            rotation_start, rotation_end, scale_start, scale_end, on_complete
        )
        self.animation_manager.add_animation(animation)

    def animate_card_flourish(self, card, target_pos, duration=0.8, on_complete=None):
        """Animated card flourish with scaling and rotation effects"""
        # We'll create a multi-part sequence of animations
        
        # 1. First animate the card floating up slightly with rotation
        start_pos = card.rect.topleft
        float_up_pos = (start_pos[0], start_pos[1] - 50)  # 50 pixels up
        
        from utils.animation import Animation

        # Define the sequence of animations
        def start_rotation_animation():
            # 2. Now animate rotation
            # Create a special animation that just handles rotation
            class RotationAnimation(Animation):
                def __init__(self, card, start_angle, end_angle, duration, on_complete=None):
                    super().__init__(duration, on_complete)
                    self.card = card
                    self.start_angle = start_angle
                    self.end_angle = end_angle
                
                def update(self, delta_time):
                    completed = super().update(delta_time)
                    progress = self.get_progress()
                    
                    # Ease in-out for rotation
                    if progress < 0.5:
                        eased_progress = 2 * progress * progress  # Ease in
                    else:
                        eased_progress = 1 - pow(-2 * progress + 2, 2) / 2  # Ease out
                    
                    # Apply rotation
                    current_angle = self.start_angle + (self.end_angle - self.start_angle) * eased_progress
                    if hasattr(self.card, 'rotate'):
                        self.card.rotate(current_angle)
                    
                    return completed
            
            # Add the rotation animation (two full spins)
            rotation_anim = RotationAnimation(card, 0, 720, duration / 2, on_complete=start_final_move)
            self.animation_manager.add_animation(rotation_anim)
        
        def start_final_move():
            # 3. Finally move to target position with scale effect
            self.animate_card_arc(
                card, target_pos, 20, duration=duration / 2,
                scale_start=1.2, scale_end=1.0,
                on_complete=on_complete
            )
        
        # Start the sequence with the first animation
        self.animate_card_movement(
            card, float_up_pos, duration=duration / 4,
            scale_start=1.0, scale_end=1.2,
            on_complete=start_rotation_animation
        )

    def animate_monster_defeat(self, monster, weapon):
        """Animate a monster being defeated by a weapon"""
        # Calculate a position above the weapon for the monster to move to first
        weapon_pos = weapon.rect.topleft if weapon else (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        above_weapon_pos = (weapon_pos[0], weapon_pos[1] - 80)
        
        # Create a sequence of animations:
        # 1. Monster moves up above weapon
        # 2. Monster shakes (damage effect)
        # 3. Monster moves to final position
        
        from utils.animation import Animation
        
        def start_shake_animation():
            # Create a shake animation
            class ShakeAnimation(Animation):
                def __init__(self, card, center_pos, intensity, duration, on_complete=None):
                    super().__init__(duration, on_complete)
                    self.card = card
                    self.center_pos = center_pos
                    self.intensity = intensity
                    self.last_offset = (0, 0)
                
                def update(self, delta_time):
                    import random
                    completed = super().update(delta_time)
                    
                    # Get the current intensity based on progress
                    # Start strong, then fade out
                    progress = self.get_progress()
                    current_intensity = self.intensity * (1 - progress)
                    
                    # Calculate random offset
                    offset_x = random.uniform(-current_intensity, current_intensity)
                    offset_y = random.uniform(-current_intensity, current_intensity)
                    
                    # Apply the new position
                    new_pos = (self.center_pos[0] + offset_x, self.center_pos[1] + offset_y)
                    self.card.update_position((int(new_pos[0]), int(new_pos[1])))
                    
                    # Reset to center position when done
                    if completed:
                        self.card.update_position((int(self.center_pos[0]), int(self.center_pos[1])))
                    
                    return completed
            
            # Create and add the shake animation
            shake_anim = ShakeAnimation(monster, above_weapon_pos, 10, 0.5, on_complete=start_final_move)
            self.animation_manager.add_animation(shake_anim)
        
        def start_final_move():
            # Calculate the final position for the monster
            if weapon:
                # Position next to other defeated monsters
                target_pos = self.calculate_monster_stack_position(len(self.defeated_monsters))
            else:
                # No weapon, move to discard pile
                target_pos = self.discard_pile.position
            
            # For weapon defeats, use arc animation
            if weapon:
                self.animate_card_arc(
                    monster, target_pos, 20, duration=0.4,
                    on_complete=lambda: self.add_to_defeated_monsters(monster)
                )
            else:
                # For bare-handed defeats, go to discard with spin
                self.animate_card_to_discard(monster)
        
        # Start with the first animation in sequence
        self.animate_card_movement(
            monster, above_weapon_pos, duration=0.3,
            on_complete=start_shake_animation
        )

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, 
            on_complete=None, rotation_start=0, rotation_end=0,
            scale_start=1.0, scale_end=1.0):
        """Create an animation for card movement with optional callback"""
        if easing is None:
            from utils.animation import EasingFunctions
            easing = EasingFunctions.ease_out_quad
        
        from utils.animation import MoveAnimation
        animation = MoveAnimation(
            card,
            card.rect.topleft,
            target_pos,
            duration,
            easing,
            on_complete
        )
        
        self.animation_manager.add_animation(animation)

    def run_from_room(self):
        if len(self.room.cards) != 4 or self.animation_manager.is_animating():
            return
        
        # Only allow running if all cards are face up
        for card in self.room.cards:
            if not card.face_up or card.is_flipping:
                return
        
        self.is_running = True
        
        # Animate cards moving to the bottom of the deck
        for card in list(self.room.cards):
            # Calculate target position (bottom of deck)
            if self.deck.card_stack:
                target_pos = self.deck.card_stack[0]
            else:
                target_pos = self.deck.position
            
            # Handle card flip animation
            card.animation_phase = "shrink"
            card.original_width = 1.0
            card.halfway_point = ((target_pos[0] + card.rect.x) // 2, 
                                (target_pos[1] + card.rect.y) // 2)
            
            # Create animation
            animation = MoveAnimation(
                card, 
                card.rect.topleft, 
                target_pos, 
                0.5,
                EasingFunctions.ease_in_out_quad
            )
            
            self.animation_manager.add_animation(animation)
            
            # Add the card data back to the bottom of the deck
            card_data = {"suit": card.suit, "value": card.value}
            self.deck.add_to_bottom(card_data)
        
        # Update the deck visuals
        self.deck.initialise_visuals()
    
    def on_run_completed(self):
        # Clear the room
        self.room.clear()
        self.is_running = False
        
        # Update the deck visuals again
        self.deck.initialise_visuals()
        
        # Start a new room
        self.start_new_room()
        
        # Set the ran_last_turn flag
        self.ran_last_turn = True
    
    def check_game_over(self):
        if self.life_points <= 0:
            self.end_game(False)
        elif not self.deck.cards:
            self.end_game(True)
    
    def end_game(self, victory):
        # Save victory state
        self.game_manager.game_data["victory"] = victory
        
        # Change to game over state
        self.game_manager.change_state("game_over")