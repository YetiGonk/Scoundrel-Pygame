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
from utils.animation import AnimationManager, MoveAnimation, EasingFunctions

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
        
        # Draw discard pile
        self.discard_pile.draw(surface)
        
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
        
        # Draw weapon and defeated monsters
        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].draw(surface)
            for monster in self.defeated_monsters:
                monster.draw(surface)
        
        # Draw order matters!
        # When running animation, draw cards first then deck
        # When drawing cards, draw deck first then cards
        if self.is_running:
            self.room.draw(surface)
            self.deck.draw(surface)
        else:
            self.deck.draw(surface)
            self.room.draw(surface)
        
        # Debug visuals if enabled
        if self.show_debug:
            # Draw center reference point
            pygame.draw.circle(surface, (255, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 3)
            
            # Draw expected card positions
            if self.room.cards:
                num_cards = 4
                total_cards_width = num_cards * CARD_WIDTH
                total_gaps_width = (num_cards - 1) * self.room.card_spacing
                total_width = total_cards_width + total_gaps_width
                
                start_x = (SCREEN_WIDTH - total_width) // 2
                start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 30
                
                for i in range(4):
                    expected_pos = (start_x + i * (CARD_WIDTH + self.room.card_spacing), start_y)
                    pygame.draw.rect(surface, (0, 255, 0), 
                                    (expected_pos[0], expected_pos[1], CARD_WIDTH, CARD_HEIGHT), 1)

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
                
                # Add card to room (this will NOT position cards anymore)
                self.room.add_card(card)
        
        # Position all cards at once after adding them all
        self.room.position_cards()
        
        # Now create animations to move cards to their positions
        for i, card in enumerate(self.room.cards):
            # Store the target position
            target_pos = card.rect.topleft
            
            # Reset to deck position for animation
            if self.deck.card_stack and i >= (len(self.room.cards) - cards_to_draw):
                card.update_position(self.deck.card_stack[-1])
            elif i >= (len(self.room.cards) - cards_to_draw):
                card.update_position(self.deck.position)
            
            # Only animate newly added cards
            if i >= (len(self.room.cards) - cards_to_draw):
                # Create animation to move card to position
                animation = MoveAnimation(
                    card, 
                    card.rect.topleft, 
                    target_pos, 
                    0.3 + 0.1 * (i - (len(self.room.cards) - cards_to_draw)),  # Stagger animations
                    EasingFunctions.ease_out_quad,
                    on_complete=lambda c=card: self.start_card_flip(c)
                )
                
                self.animation_manager.add_animation(animation)
        
        # Update deck display
        if self.deck.card_stack:
            for i in range(cards_to_draw):
                if self.deck.card_stack:
                    self.deck.card_stack.pop()
        self.deck.initialise_visuals()
    
    def start_card_flip(self, card):
        card.start_flip()
    
    def resolve_card(self, card):
        # Can only resolve cards that are face up and not flipping
        if not card.face_up or card.is_flipping or self.animation_manager.is_animating():
            return
        
        # Reset the ran_last_turn flag
        self.ran_last_turn = False
        
        # Process card effects based on type
        if card.type == "monster":
            self.attack_monster(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)
        
        # Remove the card from the room
        self.room.remove_card(card)
        
        # Debug print to check if we have cards left to animate
        print(f"Cards left after removal: {len(self.room.cards)}")
        
        # Animate remaining cards to new positions
        if len(self.room.cards) > 0:
            print("Animating card repositioning")
            self.room.position_cards(animate=True, animation_manager=self.animation_manager)
            print(f"Animation manager has {len(self.animation_manager.animations)} animations")
        
        # Wait to start a new room until animations complete
        if len(self.room.cards) == 1 and not self.animation_manager.is_animating():
            self.start_new_room(self.room.cards[0])
    
    def attack_monster(self, monster):
        if self.equipped_weapon:
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
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                    self.check_game_over()
                else:
                    if monster.value > self.life_points:
                        self.life_points = 0
                    else:
                        self.life_points -= monster.value
                    self.check_game_over()
                    self.discard_pile.add_card(monster)
            else:
                if monster.value <= self.equipped_weapon["value"]:
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
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
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                    self.check_game_over()
        else:
            if monster.value > self.life_points:
                self.life_points = 0
            else:
                self.life_points -= monster.value
            self.discard_pile.add_card(monster)
            self.check_game_over()
    
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
        
        # Set weapon position
        from constants import WEAPON_POSITION
        weapon.update_position(WEAPON_POSITION)
    
    def clear_weapon_and_monsters(self):
        for monster in self.defeated_monsters:
            self.discard_pile.add_card(monster)
        self.defeated_monsters.clear()
        
        if "node" in self.equipped_weapon:
            self.discard_pile.add_card(self.equipped_weapon["node"])
            self.equipped_weapon = {}
    
    def use_potion(self, potion):
        # Update health points
        self.life_points = min(self.life_points + potion.value, self.max_life)
        
        # Add to discard pile
        self.discard_pile.add_card(potion)
    
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