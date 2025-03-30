""" Playing state for the Roguelike Scoundrel game. """
import pygame
import random
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, WHITE, BLACK, LIGHT_GRAY
from roguelike_constants import FLOOR_STRUCTURE
from components.card import Card
from components.deck import Deck
from components.discard_pile import DiscardPile
from components.room import Room
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from ui.status_ui import StatusUI
from ui.hud import HUD
from utils.resource_loader import ResourceLoader
from utils.animation import Animation, AnimationManager, MoveAnimation, DestructionAnimation, MaterializeAnimation, EasingFunctions

class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        
        # Game components
        self.deck = None
        self.discard_pile = None
        self.room = None
        self.current_floor = None
        
        # Player stats
        self.life_points = 20
        self.max_life = 20
        self.equipped_weapon = {}
        self.defeated_monsters = []
        
        # Animation
        self.animation_manager = AnimationManager()
        self.is_running = False
        self.ran_last_turn = False
        
        # Roguelike components
        self.current_room_number = 0
        self.is_boss_room = False
        self.damage_shield = 0
        self.FLOOR_STRUCTURE = FLOOR_STRUCTURE
        
        # UI elements
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.run_button = None
        self.item_buttons = []
        self.spell_buttons = []
        self.background = None
        self.floor = None

        # State variables
        self.show_debug = False

        # Layer management
        self.z_index_counter = 0

        # Status UI & HUD
        self.status_ui = StatusUI(game_manager)
        self.hud = HUD(game_manager)

        # Add item/spell UI elements
        self.item_panel = None
        self.spell_panel = None
        
        # Add completed room counter
        self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        
        # Add flag for completed floor
        self.floor_completed = False

    def enter(self):
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = pygame.font.SysFont(None, 20)

        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load floor
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        # Initialize game components
        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()
        self.current_room_number = floor_manager.current_room
        self.is_boss_room = floor_manager.is_boss_room()
        
        # If this is a new floor, setup the appropriate deck
        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        # Create run button
        from constants import RUN_POSITION, RUN_WIDTH, RUN_HEIGHT
        run_button_rect = pygame.Rect(RUN_POSITION[0], RUN_POSITION[1], RUN_WIDTH, RUN_HEIGHT)
        self.run_button = Button(run_button_rect, "RUN", self.body_font)

        # Create item and spell buttons
        self.create_item_buttons()
        self.create_spell_buttons()

        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
        self.equipped_weapon = {}
        self.defeated_monsters = []
        self.damage_shield = 0

        # Initialize the deck and start the first room
        self.deck.initialise_deck()
        
        # If this is a boss room, add the boss card to the deck
        if self.is_boss_room:
            boss_card = self.game_manager.floor_manager.get_boss_card()
            if boss_card:
                # Add the boss card to the bottom of the deck
                self.deck.add_to_bottom(boss_card)
        
        self.start_new_room()
        
        # Update status UI fonts
        self.status_ui.update_fonts(self.header_font, self.normal_font)

        # Update HUD fonts
        self.hud.update_fonts(self.normal_font, self.normal_font)

        # Create item and spell panels
        self.create_item_spell_panels()
        
        # Reset floor completion tracking
        self.floor_completed = False
        self.completed_rooms = self.game_manager.floor_manager.current_room
        self.total_rooms_on_floor = self.game_manager.floor_manager.FLOOR_STRUCTURE["rooms_per_floor"]
    
    def exit(self):
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life
    
    # ===== UI MANAGEMENT =====
    
    def create_item_spell_panels(self):
        """Create panels for displaying items and spells."""
        # Item panel (left side)
        item_panel_rect = pygame.Rect(20, 20, 160, 200)
        self.item_panel = Panel(
            (item_panel_rect.width, item_panel_rect.height),
            (item_panel_rect.left, item_panel_rect.top),
            WHITE,
            180  # Semi-transparent
        )
        
        # Spell panel (right side)
        spell_panel_rect = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 200)
        self.spell_panel = Panel(
            (spell_panel_rect.width, spell_panel_rect.height),
            (spell_panel_rect.left, spell_panel_rect.top),
            WHITE,
            180  # Semi-transparent
        )
        
        # Create item and spell buttons
        self.create_item_buttons()
        self.create_spell_buttons()

    def create_item_buttons(self):
        """Create buttons for player items."""
        self.item_buttons = []
        
        # Create a panel for items
        item_panel_rect = pygame.Rect(20, 20, 160, 200)
        
        # Create buttons for each item
        for i, item in enumerate(self.game_manager.item_manager.player_items):
            button_rect = pygame.Rect(
                item_panel_rect.left + 10,
                item_panel_rect.top + 40 + (i * 50),
                140,
                40
            )
            
            self.item_buttons.append({
                "item": item,
                "index": i,
                "button": Button(button_rect, item.name, self.normal_font)
            })
    
    def create_spell_buttons(self):
        """Create buttons for player spells."""
        self.spell_buttons = []
        
        # Create a panel for spells
        spell_panel_rect = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 200)
        
        # Create buttons for each spell
        for i, spell in enumerate(self.game_manager.spell_manager.player_spells):
            button_rect = pygame.Rect(
                spell_panel_rect.left + 10,
                spell_panel_rect.top + 40 + (i * 50),
                140,
                40
            )
            
            self.spell_buttons.append({
                "spell": spell,
                "index": i,
                "button": Button(button_rect, spell.name, self.normal_font)
            })
            
    # ===== EVENT HANDLING =====
    
    def handle_event(self, event):
        if self.animation_manager.is_animating():
            return  # Don't handle events while animating
        
        if event.type == MOUSEMOTION:
            # Check hover for cards in the room
            for card in self.room.cards:
                card.check_hover(event.pos)
            
            # Check hover for run button
            self.run_button.check_hover(event.pos)
            
            # Check hover for item buttons
            for item_data in self.item_buttons:
                item_data["button"].check_hover(event.pos)
            
            # Check hover for spell buttons
            for spell_data in self.spell_buttons:
                spell_data["button"].check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.life_points <= 0:
                return  # Don't handle clicks if player is dead
            
            # Check if run button was clicked
            if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
                # Cannot run from boss rooms
                if not self.is_boss_room:
                    self.run_from_room()
                return
            
            # Check if an item button was clicked
            for item_data in self.item_buttons:
                if item_data["button"].is_clicked(event.pos):
                    self.use_item(item_data["index"])
                    return
            
            # Check if a spell button was clicked
            for spell_data in self.spell_buttons:
                if spell_data["button"].is_clicked(event.pos):
                    self.cast_spell(spell_data["index"])
                    return
            
            # Check if a card was clicked
            card = self.room.get_card_at_position(event.pos)
            if card:
                self.resolve_card(card)
    
    def update(self, delta_time):
        # First, update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update card flip animations
        for card in self.room.cards:
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # Only process game state changes if we're not animating or animations just finished
        if not current_animating:
            # If we were running and animations finished, complete the run
            if self.is_running:
                self.on_run_completed()
                return
            
            # Process room state only when no animations are running
            if len(self.room.cards) == 0:               
                # Check if the next room should be a merchant room
                is_merchant_next = self.completed_rooms + 1 in self.FLOOR_STRUCTURE["merchant_rooms"]
                
                if is_merchant_next:
                    # Set the floor manager's current room for the merchant
                    self.game_manager.floor_manager.current_room = self.completed_rooms
                    # Advance to merchant room
                    self.game_manager.advance_to_next_room()
                elif len(self.deck.cards) > 0:
                    # More cards in deck - advance to next room
                    self.game_manager.advance_to_next_room()
                    
                    # Check if we're still in the playing state (not moved to merchant or other state)
                    if self.game_manager.current_state == self:
                        # Check if we're at the boss room
                        floor_manager = self.game_manager.floor_manager
                        if floor_manager.current_room == self.FLOOR_STRUCTURE["boss_room"] - 1:
                            # The next room will be the boss, prepare it
                            self.is_boss_room = True
                        
                        # Start a new room
                        self.start_new_room()
                else:
                    # No more cards in the deck - floor completed
                    if not self.floor_completed:
                        self.floor_completed = True
                        
                        # Update floor manager
                        self.game_manager.floor_manager.current_room = self.total_rooms_on_floor
                        
                        # Check if this is the last floor
                        if self.game_manager.floor_manager.current_floor_index >= len(self.game_manager.floor_manager.floors) - 1:
                            # Last floor completed - victory!
                            self.game_manager.game_data["victory"] = True
                            self.game_manager.game_data["run_complete"] = True
                            self.game_manager.change_state("game_over")
                        else:
                            # Not the last floor, advance to next floor
                            self.game_manager.floor_manager.advance_floor()
                            self.game_manager.change_state("floor_start")
            
            # If we have only one card left and animations just finished, start a new room 
            elif len(self.room.cards) == 1 and animations_just_finished and len(self.deck.cards) > 0:
                # Increment completed rooms because we're moving to the next room with a card
                self.completed_rooms += 1
                
                # Check if the next room should be a merchant room
                is_merchant_next = self.completed_rooms + 1 in self.FLOOR_STRUCTURE["merchant_rooms"]
                
                if is_merchant_next:
                    # Set the floor manager's current room for the merchant
                    self.game_manager.floor_manager.current_room = self.completed_rooms
                    # Advance to merchant room
                    self.game_manager.advance_to_next_room()
                else:
                    # Start a new room with the remaining card
                    self.start_new_room(self.room.cards[0])
        
        self.check_game_over()

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
        
        # Draw any visual effects (destruction/materialize animations)
        self.animation_manager.draw_effects(surface)
        
        # Draw health
        health_text = self.title_font.render(str(self.life_points), True, WHITE)
        health_rect = health_text.get_rect(bottomleft=(self.deck.rect.x, SCREEN_HEIGHT-self.deck.rect.y))
        surface.blit(health_text, health_rect)
        
        # Draw run button
        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:
            # Draw disabled run button
            button_rect = self.run_button.rect
            pygame.draw.rect(surface, LIGHT_GRAY, button_rect)
            pygame.draw.rect(surface, BLACK, button_rect, 2)
            button_text = self.body_font.render("RUN", True, (150, 150, 150))  # Greyed out text
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)

        # Draw item and spell panels
        self.item_panel.draw(surface)
        self.spell_panel.draw(surface)
        
        # Draw item panel title
        item_title = self.body_font.render("Items", True, BLACK)
        item_title_rect = item_title.get_rect(centerx=self.item_panel.rect.centerx, top=self.item_panel.rect.top + 10)
        surface.blit(item_title, item_title_rect)
        
        # Draw spell panel title
        spell_title = self.body_font.render("Spells", True, BLACK)
        spell_title_rect = spell_title.get_rect(centerx=self.spell_panel.rect.centerx, top=self.spell_panel.rect.top + 10)
        surface.blit(spell_title, spell_title_rect)
        
        # Draw item buttons
        for item_data in self.item_buttons:
            item_data["button"].draw(surface)
        
        # Draw spell buttons
        for spell_data in self.spell_buttons:
            spell_data["button"].draw(surface)
        
        # Draw status UI
        self.status_ui.draw(surface)
        
        # Draw boss indicator if in boss room
        if self.is_boss_room:
            boss_text = self.header_font.render("BOSS ROOM", True, (255, 0, 0))
            boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, 30))
            surface.blit(boss_text, boss_rect)
    
    # ===== ITEM AND SPELL HANDLING =====
    
    def use_item(self, item_index):
        """Use an item from the player's inventory."""
        if self.game_manager.item_manager.use_item(item_index):
            # Apply shield effect if it's a protection item
            if item_index < len(self.game_manager.item_manager.player_items):
                item = self.game_manager.item_manager.player_items[item_index]
                if item.effect == "protect_from_damage":
                    self.set_damage_shield(10)  # Set a default shield value
            
            # Refresh the UI
            self.create_item_buttons()
            return True
        return False
    
    def cast_spell(self, spell_index):
        """Cast a spell from the player's spellbook."""
        if self.game_manager.spell_manager.cast_spell(spell_index):
            # Apply shield effect if it's a protection spell
            if spell_index < len(self.game_manager.spell_manager.player_spells):
                spell = self.game_manager.spell_manager.player_spells[spell_index]
                if spell.effect == "protect_from_damage":
                    self.set_damage_shield(5)  # Set a default shield value
            
            # Refresh the UI
            self.create_spell_buttons()
            return True
        return False
    
    def set_damage_shield(self, amount):
        """Set a damage shield for the player."""
        self.damage_shield = amount
        
        # Create a visual indicator for the shield
        shield_effect = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(shield_effect, (0, 100, 255, 100), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 150, 5)
    
    # ===== CARD HANDLING =====
    
    def resolve_card(self, card):
        """Process a card that has been clicked by the player."""
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
        
        # We'll let each handler reposition the cards with proper timing
        # This prevents cards from disappearing during animations
        
    def remove_and_discard(self, card):
        """Remove a card from the room and add it to the discard pile.
        This function should be called only after an animation completes."""
        # First remove from the room if it's still there
        if card in self.room.cards:
            self.room.remove_card(card)

        if card in self.defeated_monsters:
            self.defeated_monsters.remove(card)

        if self.equipped_weapon and card == self.equipped_weapon["node"]:
            self.equipped_weapon = {}

        # Add to discard pile
        self.discard_pile.add_card(card)

    def attack_monster(self, monster):
        """Process player attacking a monster card."""
        # Calculate monster value - apply any effect from items or spells
        monster_value = monster.value
        
        # Use damage shield if available
        damage_reduction = 0
        if self.damage_shield > 0:
            damage_reduction = min(self.damage_shield, monster_value)
            monster_value -= damage_reduction
            self.damage_shield -= damage_reduction

        # First ensure the monster is removed from the room before animations start
        self.room.remove_card(monster)

        if self.equipped_weapon:
            # Monster will be added to stack or discard
            if self.defeated_monsters:
                if self.defeated_monsters[-1].value > monster_value:
                    damage = monster_value - self.equipped_weapon["value"]
                    if damage < 0:
                        damage = 0
                    if damage > self.life_points:
                        damage = self.life_points
                    self.life_points -= damage
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    
                    # Add to defeated monster stack
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                else:
                    if monster_value > self.life_points:
                        self.life_points = 0
                    else:
                        self.life_points -= monster_value
                        # Animate to discard pile
                        self.animate_card_to_discard(monster)
            else:
                if monster_value <= self.equipped_weapon["value"]:
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    # Add to defeated monster stack
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                else:
                    damage = monster_value - self.equipped_weapon["value"]
                    if damage < 0:
                        damage = 0
                    if damage > self.life_points:
                        damage = self.life_points
                    self.life_points -= damage
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    # Add to defeated monster stack
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
        else:
            if monster_value > self.life_points:
                self.life_points = 0
            else:
                self.life_points -= monster_value
                # Animate to discard pile
                self.animate_card_to_discard(monster)
                
        # After processing the monster, reposition remaining room cards
        if len(self.room.cards) > 0:
            # Add a slight delay before repositioning room cards
            self.schedule_delayed_animation(
                0.1,
                lambda: self.room.position_cards(animate=True, animation_manager=self.animation_manager)
            )
        
        # After attack is complete, update interface
        self.create_item_buttons()
        self.create_spell_buttons()

    def equip_weapon(self, weapon):
        """Equip a weapon card."""
        # First clear previous weapon and monsters
        old_weapon = self.equipped_weapon.get("node", None)
        old_monsters = self.defeated_monsters.copy()
        
        # Update data structures first
        self.room.remove_card(weapon)
        self.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon
        }
        self.defeated_monsters = []
        
        # Set z-index for new weapon
        weapon.z_index = self.z_index_counter
        self.z_index_counter += 1
        
        # Animate new weapon equipping first
        from constants import WEAPON_POSITION
        self.animate_card_movement(weapon, WEAPON_POSITION)
        
        # Now discard old weapon and monsters
        if old_weapon or old_monsters:
            for i, monster in enumerate(old_monsters):
                # Add a slight delay for each monster
                delay = 0.08 * i
                self.schedule_delayed_animation(
                    delay,
                    lambda card=monster: self.animate_card_to_discard(card)
                )
            
            # Discard old weapon last if it exists
            if old_weapon:
                delay = 0.08 * len(old_monsters)
                self.schedule_delayed_animation(
                    delay,
                    lambda: self.animate_card_to_discard(old_weapon)
                )
    
    def clear_weapon_and_monsters(self):
        """Discard the equipped weapon and all defeated monsters."""
        # Animate all monsters moving to the discard pile with staggered timing
        for i, monster in enumerate(self.defeated_monsters):
            # Add a slight delay for each monster to create a cascade effect
            delay = 0.08 * i
            self.schedule_delayed_animation(
                delay,
                lambda card=monster: self.animate_card_to_discard(card)
            )
        
        # Animate the weapon moving to the discard pile last
        if "node" in self.equipped_weapon:
            delay = 0.08 * len(self.defeated_monsters)
            self.schedule_delayed_animation(
                delay,
                lambda: self.animate_card_to_discard(self.equipped_weapon["node"])
            )
    
    def use_potion(self, potion):
        """Use a potion card to heal the player."""
        # Update health points
        self.life_points = min(self.life_points + potion.value, self.max_life)
        
        # First ensure the potion is removed from the room
        self.room.remove_card(potion)
        
        # Animate potion moving to discard pile
        self.animate_card_to_discard(potion)
        
        # After processing the potion, reposition remaining room cards
        if len(self.room.cards) > 0:
            # Add a slight delay before repositioning room cards
            self.schedule_delayed_animation(
                0.1,
                lambda: self.room.position_cards(animate=True, animation_manager=self.animation_manager)
            )
    
    # ===== ANIMATION METHODS =====
    
    def animate_card_to_discard(self, card):
        """Animate a card being destroyed and appearing in the discard pile."""
        # First create a destruction animation
        from utils.animation import DestructionAnimation
        
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
        
        self.animation_manager.add_animation(destroy_anim)
        
    def materialize_card_at_discard(self, card):
        """Materialize the card at the discard pile position."""
        # Update card position to discard pile
        card.update_position(self.discard_pile.position)
        
        # Create materialize animation
        from utils.animation import MaterializeAnimation
        materialize_anim = MaterializeAnimation(
            card,
            self.discard_pile.position,
            effect_type="sparkle",
            duration=0.3,
            on_complete=lambda: self.remove_and_discard(card)
        )
        
        self.animation_manager.add_animation(materialize_anim)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, 
        on_complete=None):
        """Create a simple, direct animation for card movement with optional callback."""
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

    def position_monster_stack(self):
        """Position defeated monsters in a stack."""
        if not self.defeated_monsters or "node" not in self.equipped_weapon:
            return
            
        from constants import MONSTER_STACK_OFFSET, MONSTER_START_OFFSET
        total_width = MONSTER_STACK_OFFSET[0] * (len(self.defeated_monsters) - 1)
        start_x = self.equipped_weapon["node"].rect.x + MONSTER_START_OFFSET[0]
        
        for i, monster in enumerate(self.defeated_monsters):
            new_stack_position = (
                start_x + i * MONSTER_STACK_OFFSET[0],
                self.equipped_weapon["node"].rect.y + MONSTER_STACK_OFFSET[1] * i
            )
            self.animate_card_movement(monster, new_stack_position)

        new_weapon_position = (
            self.equipped_weapon["node"].rect.x - MONSTER_STACK_OFFSET[1]*2,
            self.equipped_weapon["node"].rect.y
        )
        self.animate_card_movement(self.equipped_weapon["node"], new_weapon_position)
    
    # ===== ROOM MANAGEMENT =====
    
    def start_new_room(self, last_card=None):
        """Start a new room with cards from the deck."""
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
        cards_to_draw = min(4 - len(self.room.cards), len(self.deck.cards))
        
        # Calculate final target positions first
        num_cards = min(4, len(self.deck.cards)+len(self.room.cards))  # Always 4 cards in a full room
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
                
                # Add card to room
                self.room.add_card(card)
                
                # Calculate which target position to use
                if last_card:
                    if num_cards < 4:
                        target_pos = target_positions[i]
                    else:
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
        """Schedule an animation to start after a delay."""
        # Add a "timer" animation that does nothing except wait
        # When it completes, it will run the callback to create the real animation
        from utils.animation import Animation
        timer = Animation(delay, on_complete=callback)
        self.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        """Start the flip animation for a card."""
        card.start_flip()
    
    def run_from_room(self):
        """Run from the current room, moving all cards to the bottom of the deck."""
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
            
            # Set z-index and create animation
            card.z_index = -100
            
            # Use standard card movement animation
            self.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )
            
            # Add the card data back to the bottom of the deck
            card_data = {"suit": card.suit, "value": card.value}
            self.deck.add_to_bottom(card_data)
        
        # Update the deck visuals
        self.deck.initialise_visuals()
    
    def on_run_completed(self):
        """Complete the running action after animations finish."""
        # Clear the room
        self.room.clear()
        self.is_running = False
        
        # Update the deck visuals again
        self.deck.initialise_visuals()
        
        # Start a new room
        self.start_new_room()
        
        # Set the ran_last_turn flag
        self.ran_last_turn = True
    
    # ===== GAME STATE MANAGEMENT =====
    
    def check_game_over(self):
        """Check if the game is over due to player death or victory."""
        if self.life_points <= 0:
            self.end_game(False)
        elif not self.deck.cards and not self.room.cards and self.floor_completed and self.total_rooms_on_floor == self.completed_rooms:
            self.end_game(True)
    
    def end_game(self, victory):
        """End the game with either victory or defeat."""
        # Save victory state
        self.game_manager.game_data["victory"] = victory
        
        # Change to game over state
        self.game_manager.change_state("game_over")