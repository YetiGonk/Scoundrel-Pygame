""" Playing state for the Roguelike Scoundrel game. """
import pygame
import random
import math
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY, FONTS_PATH
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
from utils.animation import Animation, AnimationManager, MoveAnimation, DestructionAnimation, MaterializeAnimation, HealthChangeAnimation, GoldChangeAnimation, EasingFunctions

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
        self.gold = 0  # Add gold counter
        self.equipped_weapon = {}
        self.defeated_monsters = []
        
        # Player inventory (supports 2 cards max)
        self.inventory = []
        self.MAX_INVENTORY_SIZE = 2
        
        # Animation
        self.animation_manager = AnimationManager()
        self.is_running = False
        self.ran_last_turn = False
        
        # Roguelike components
        self.current_room_number = 0
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
        
        # Add flags for room state tracking
        self.gold_reward_given = False
        self.room_completion_in_progress = False
        
        # Initialize message display
        self.message = None

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
        
        # If this is a new floor, setup the appropriate deck
        if not hasattr(self, 'deck') or not self.deck:
            self.deck = Deck(self.current_floor)
            self.discard_pile = DiscardPile()
            self.room = Room(self.animation_manager)

        # Create run button (smaller and positioned below status UI, above room)
        # Make the button smaller
        run_width = 60  # Smaller width
        run_height = 30  # Smaller height
        
        # Position below status UI and above room
        run_x = SCREEN_WIDTH // 2
        run_y = 150  # Below status UI, above room
        
        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)
        self.run_button = Button(run_button_rect, "RUN", self.normal_font)  # Use smaller font too

        # Create item and spell buttons
        self.create_item_buttons()
        self.create_spell_buttons()

        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
        self.gold = self.game_manager.game_data.get("gold", 0)  # Get gold from game data
        
        # Check if coming back from merchant - restore equipped weapon and defeated monsters
        if hasattr(self.game_manager, 'equipped_weapon') and self.game_manager.equipped_weapon:
            self.equipped_weapon = self.game_manager.equipped_weapon
            self.defeated_monsters = self.game_manager.defeated_monsters
            # Clear the stored data
            self.game_manager.equipped_weapon = {}
            self.game_manager.defeated_monsters = []
        else:
            self.equipped_weapon = {}
            self.defeated_monsters = []
            
        self.damage_shield = 0

        # Initialize the deck and start the first room if not coming from merchant
        if not hasattr(self.game_manager, 'coming_from_merchant') or not self.game_manager.coming_from_merchant:
            self.deck.initialise_deck()
            self.start_new_room()
        
        # Update status UI fonts
        self.status_ui.update_fonts(self.header_font, self.normal_font)

        # Update HUD fonts
        self.hud.update_fonts(self.normal_font, self.normal_font)

        # Create item and spell panels
        self.create_item_spell_panels()

        # Reset floor completion tracking
        self.floor_completed = False

        # Reset room counter if starting a new floor
        if self.current_room_number == 0:
            self.completed_rooms = 0
        # Initialize completed_rooms if not already set
        elif not hasattr(self, 'completed_rooms'):
            self.completed_rooms = self.current_room_number

        # We'll track room completion based on cards processed, not based on a fixed total

    def exit(self):
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life
        self.game_manager.game_data["gold"] = self.gold

    # ===== UI MANAGEMENT =====

    def create_item_spell_panels(self):
        """Create panels for displaying items and spells."""
        from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, ITEM_PANEL_HEIGHT, SPELL_PANEL_WIDTH, SPELL_PANEL_HEIGHT
        # Item panel (left side)
        item_panel_rect = pygame.Rect(ITEM_PANEL_POSITION, (ITEM_PANEL_WIDTH, ITEM_PANEL_HEIGHT))
        self.item_panel = Panel(
            (item_panel_rect.width, item_panel_rect.height),
            (item_panel_rect.left, item_panel_rect.top),
            GRAY,
            180  # Semi-transparent
        )

        # Spell panel (right side)
        spell_panel_rect = pygame.Rect(SPELL_PANEL_POSITION, (SPELL_PANEL_WIDTH, SPELL_PANEL_HEIGHT))
        self.spell_panel = Panel(
            (spell_panel_rect.width, spell_panel_rect.height),
            (spell_panel_rect.left, spell_panel_rect.top),
            GRAY,
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
            
            # Check hover for inventory cards
            for card in self.inventory:
                card.check_hover(event.pos)
                
            # Check hover for equipped weapon
            if "node" in self.equipped_weapon:
                self.equipped_weapon["node"].check_hover(event.pos)
            
            # Check hover for defeated monsters
            for monster in self.defeated_monsters:
                monster.check_hover(event.pos)
            
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
            clicked_card = None
            
            # First check room cards
            card = self.room.get_card_at_position(event.pos)
            if card:
                self.resolve_card(card, event_pos=event.pos)
                return  # Important: Return to prevent checking inventory cards
            
            # If no room card was clicked, check inventory cards
            clicked_inventory_card = self.get_inventory_card_at_position(event.pos)
            if clicked_inventory_card:
                self.use_inventory_card(clicked_inventory_card)
    
    def update(self, delta_time):
        # First, update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update card animations
        for card in self.room.cards:
            # Update idle hover and hover animations
            card.update(delta_time)
            
            # Update card flip animations
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # Update inventory card animations
        for card in self.inventory:
            card.update(delta_time)
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # Update weapon and defeated monster animations
        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].update(delta_time)
            
        for monster in self.defeated_monsters:
            monster.update(delta_time)
        
        # Only process game state changes if we're not animating or animations just finished
        if not current_animating:
            # If we were running and animations finished, complete the run
            if self.is_running:
                self.on_run_completed()
                return
            
            # Process room state only when no animations are running
            if len(self.room.cards) == 0:
                # Only trigger room completion once
                if not self.room_completion_in_progress:
                    # Set flag to prevent multiple room completions
                    self.room_completion_in_progress = True
                    
                    # Increment room count when completing a room
                    self.completed_rooms += 1
                    
                    # Award gold for completing the room (2-5 gold)
                    # More difficult floors could give more gold
                    floor_bonus = min(2, self.game_manager.floor_manager.current_floor_index)  # 0-2 bonus based on floor
                    gold_reward = random.randint(2, 5) + floor_bonus
                    self.change_gold(gold_reward)

                # Check if the next room should be a merchant room
                is_merchant_next = self.completed_rooms in self.FLOOR_STRUCTURE["merchant_rooms"]
                
                if is_merchant_next:
                    # Set the floor manager's current room for the merchant (don't increment)
                    self.game_manager.floor_manager.current_room = self.completed_rooms - 1
                    # Flag that we're coming from merchant so we preserve state
                    self.game_manager.coming_from_merchant = True
                    # Advance to merchant room
                    self.game_manager.advance_to_next_room()
                elif len(self.deck.cards) > 0:
                    # More cards in deck - advance to next room
                    self.game_manager.advance_to_next_room()
                    
                    # Check if we're still in the playing state (not moved to merchant or other state)
                    if self.game_manager.current_state == self:
                        # Start a new room
                        self.start_new_room()
                else:
                    # No more cards in the deck - floor completed
                    if not self.floor_completed:
                        self.floor_completed = True
                        
                        # Mark this floor as completed
                        self.game_manager.floor_manager.current_room = self.FLOOR_STRUCTURE["rooms_per_floor"]
                        
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
                # Only trigger room completion once
                if not self.room_completion_in_progress:
                    # Set flag to prevent multiple room completions
                    self.room_completion_in_progress = True
                    
                    # Increment completed rooms because we're moving to the next room with a card
                    self.completed_rooms += 1
                    
                    # Award gold for completing the room (2-5 gold)
                    # More difficult floors could give more gold
                    floor_bonus = min(2, self.game_manager.floor_manager.current_floor_index)  # 0-2 bonus based on floor
                    gold_reward = random.randint(2, 5) + floor_bonus
                    self.change_gold(gold_reward)
                
                # Check if the next room should be a merchant room
                is_merchant_next = self.completed_rooms in self.FLOOR_STRUCTURE["merchant_rooms"]
                
                if is_merchant_next:
                    # Set the floor manager's current room for the merchant (don't increment)
                    self.game_manager.floor_manager.current_room = self.completed_rooms - 1
                    # Flag that we're coming from merchant so we preserve state
                    self.game_manager.coming_from_merchant = True
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
            weapon_card = self.equipped_weapon["node"]
            
            # Check for hover over the weapon card
            weapon_is_hovered = weapon_card.is_hovered and weapon_card.face_up
            
            # Draw the weapon card
            weapon_card.draw(surface)
            
            # Draw weapon type and name only if hovered
            if weapon_is_hovered:
                # Draw weapon type below the card
                if hasattr(weapon_card, 'weapon_type') and weapon_card.weapon_type:
                    weapon_type = weapon_card.weapon_type.upper()
                    if hasattr(weapon_card, 'damage_type') and weapon_card.damage_type:
                        damage_type = weapon_card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                    else:
                        type_text = weapon_type
                        
                    self.draw_card_type(surface, weapon_card, type_text)
                    
                # Draw weapon name above the card
                if weapon_card.name:
                    self._draw_inventory_card_info(surface, weapon_card)
            
            # Process all defeated monsters
            hovered_monsters = []
            non_hovered_monsters = []
            
            # Separate hovered and non-hovered monsters
            for monster in self.defeated_monsters:
                if monster.is_hovered and monster.face_up:
                    hovered_monsters.append(monster)
                else:
                    non_hovered_monsters.append(monster)
            
            # Draw non-hovered monsters first
            for monster in non_hovered_monsters:
                monster.draw(surface)
            
            # Draw hovered monsters and their info
            for monster in hovered_monsters:
                # Draw the monster card
                monster.draw(surface)
                
                # Draw monster type below the card
                if hasattr(monster, 'monster_type') and monster.monster_type:
                    self.draw_card_type(surface, monster, monster.monster_type.upper())
                
                # Draw monster name above the card
                if monster.name:
                    self._draw_inventory_card_info(surface, monster)
        
        # Draw inventory background panel between item and spell panels
        # Position it vertically centered between the item and spell panels
        from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, ITEM_PANEL_HEIGHT, SPELL_PANEL_HEIGHT
        
        # Calculate vertical center between spell and item panels
        vertical_center = (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT + 
                          (ITEM_PANEL_POSITION[1] - (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT)) // 2)
        
        # Create a smaller inventory panel
        inv_width = ITEM_PANEL_WIDTH
        inv_height = 120  # Smaller height
        inv_x = SCREEN_WIDTH - inv_width - 40  # Same x as item/spell panels
        inv_y = vertical_center - inv_height // 2 # Center between items and spells
        inv_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        
        # Draw panel background with border
        pygame.draw.rect(surface, GRAY, inv_rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, inv_rect, 2, border_radius=8)
        
        # Draw title
        inv_title = self.body_font.render("Inventory", True, WHITE)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)
        surface.blit(inv_title, title_rect)
        
        # First sort inventory cards so hovered ones are at the end (will be drawn on top)
        # Use a stable sort so if there are multiple cards, their original order is preserved
        sorted_cards = sorted(self.inventory, key=lambda c: 1 if c.is_hovered else 0)
        
        # First pass - draw shadows for all cards
        for card in sorted_cards:
            self._draw_card_shadow(surface, card)
        
        # Second pass - draw all cards and type information
        for card in sorted_cards:
            # Draw the card
            card.draw(surface)
            
            # Only draw card info if the card is hovered
            if card.face_up and card.is_hovered:
                # Get type text for the card
                type_text = ""
                if card.type == "weapon" and hasattr(card, 'weapon_type') and card.weapon_type:
                    weapon_type = card.weapon_type.upper()
                    # Show damage type for weapons
                    if hasattr(card, 'damage_type') and card.damage_type and card.weapon_type != "arrow":
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                    else:
                        type_text = weapon_type
                elif card.type == "potion":
                    type_text = "HEALING"
                
                # Draw type text below the card
                if type_text:
                    self.draw_card_type(surface, card, type_text)
                
                # Draw name hover info above the card
                if card.name:
                    self._draw_inventory_card_info(surface, card)
            
        # Draw room cards LAST always
        self.room.draw(surface)
        
        # Draw any visual effects (destruction/materialize animations)
        self.animation_manager.draw_effects(surface)
        
        # Draw health display
        self.draw_health_display(surface)
        
        # Draw gold display
        self.draw_gold_display(surface)
        
        # Draw UI animations (health changes, etc.)
        self.animation_manager.draw_ui_effects(surface)
        
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
            
        # Draw any active message
        if hasattr(self, 'message') and self.message:
            # Draw message background
            pygame.draw.rect(surface, BLACK, self.message["bg_rect"], border_radius=8)
            pygame.draw.rect(surface, WHITE, self.message["bg_rect"], 2, border_radius=8)
            # Draw message text
            surface.blit(self.message["text"], self.message["rect"])

        # Draw item and spell panels
        self.item_panel.draw(surface)
        self.spell_panel.draw(surface)
        
        # Draw item panel title
        item_title = self.body_font.render("Items", True, WHITE)
        item_title_rect = item_title.get_rect(centerx=self.item_panel.rect.centerx, top=self.item_panel.rect.top + 10)
        surface.blit(item_title, item_title_rect)
        
        # Draw spell panel title
        spell_title = self.body_font.render("Spells", True, WHITE)
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
        
    
    def _draw_inventory_card_info(self, surface, card):
        """Draw name and other info for inventory cards."""
        # Font for card name
        name_font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", 18)
        
        # Render card name
        card_name = card.name.upper()
        text_surface = name_font.render(card_name, True, WHITE)
        text_rect = text_surface.get_rect()
        
        # Calculate total float offset (idle + hover)
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
            
        # Position text above card with floating offset
        gap = 4
        text_rect.midbottom = (card.rect.centerx, card.rect.top - gap - total_float_offset)
        
        # Add background with padding
        padding = 8
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        
        # Draw the background and text
        pygame.draw.rect(surface, BLACK, bg_rect)
        pygame.draw.rect(surface, WHITE, bg_rect, 2)  # White border
        surface.blit(text_surface, text_rect)
        
    def _draw_card_shadow(self, surface, card):
        """Draw shadow effect for a card"""
        shadow_alpha = 60
        shadow_width = 4
        shadow_rect = card.rect.inflate(shadow_width * 2, shadow_width * 2)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=3)
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    def draw_card_type(self, surface, card, type_text):
        """Helper method to draw a card's type below the card"""
        # Only proceed if we have text to display
        if not type_text:
            return
            
        # Initialize font if needed
        if not hasattr(self, 'small_font') or self.small_font is None:
            self.small_font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", 16)
        
        padding = 6  # Smaller padding for non-hovered cards
        
        # Render the type text
        type_surface = self.small_font.render(type_text, True, WHITE)
        type_rect = type_surface.get_rect()
        
        # Calculate the total float offset for proper positioning
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
            
        # Position text below card with the float offset to move with card
        gap = 4  # Smaller consistent gap
        # Use negative offset for inventory cards to make text move with card
        type_rect.midtop = (card.rect.centerx, card.rect.bottom + gap - total_float_offset)
        
        # Create background rect and draw
        type_bg_rect = type_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(surface, BLACK, type_bg_rect)
        pygame.draw.rect(surface, WHITE, type_bg_rect, 1)  # 1px white border
        surface.blit(type_surface, type_rect)
    
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
        
    def show_message(self, message, duration=2.0):
        """Display a temporary message on screen."""
        # Create a temporary animation to display the message
        message_text = self.header_font.render(message, True, WHITE)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        
        # Create a dark background for the message
        bg_rect = message_rect.inflate(40, 20)
        
        # Store the message info
        self.message = {
            "text": message_text,
            "rect": message_rect,
            "bg_rect": bg_rect,
            "time_remaining": duration
        }
        
        # Schedule a delay to clear the message
        from utils.animation import Animation
        timer = Animation(duration, on_complete=lambda: setattr(self, 'message', None))
        self.animation_manager.add_animation(timer)
    
    # ===== CARD HANDLING =====
    
    def resolve_card(self, card, event_pos=None):
        """Process a card that has been clicked by the player."""
        # Can only resolve cards that are face up and not flipping
        if not card.face_up or card.is_flipping or self.animation_manager.is_animating():
            return
        
        # Reset the ran_last_turn flag
        self.ran_last_turn = False
        
        # Mark the card as selected to remove split colors
        card.is_selected = True
        
        # For cards that can be added to inventory, determine which part was clicked
        if card.can_add_to_inventory and event_pos:
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
            
            # Check if click is above or below midpoint
            if event_pos[1] < center_y:
                # Top half clicked - add to inventory
                self.add_to_inventory(card)
                return
            # Bottom half clicked - continue to use the card normally
        
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
        
        # Check if player has a weapon equipped
        if self.equipped_weapon:
            weapon_node = self.equipped_weapon.get("node", None)
            weapon_value = self.equipped_weapon.get("value", 0)
            
            # Check if it's a ranged weapon and if player has arrows
            has_arrow = False
            arrow_card = None
            
            # Only check for arrows if the equipped weapon is ranged
            if weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged":
                # Look for arrow cards in inventory
                for card in self.inventory:
                    if (hasattr(card, "weapon_type") and card.weapon_type == "arrow") or \
                       (card.type == "weapon" and card.value == 2):  # 2 of diamonds is arrow
                        has_arrow = True
                        arrow_card = card
                        break
            
            # Handle ranged weapon with arrow
            if weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged" and has_arrow:
                # Remove arrow from inventory if using ranged weapon
                if arrow_card:
                    self.inventory.remove(arrow_card)
                    # Discard the used arrow
                    self.animate_card_to_discard(arrow_card)
                    # Reposition remaining inventory cards
                    self.position_inventory_cards()
                
                # With ranged weapon + arrow, you don't take damage if monster value > weapon value
                if monster_value <= weapon_value:
                    # Monster defeated with no damage
                    monster.z_index = self.z_index_counter
                    self.z_index_counter += 1
                    # Add to defeated monster stack
                    self.defeated_monsters.append(monster)
                    self.position_monster_stack()
                else:
                    # Monster escapes but no damage taken (ranged weapon benefit)
                    # Animate to discard pile
                    self.animate_card_to_discard(monster)
                    
                    # Show message that ranged attack missed but no damage taken
                    self.show_message("Ranged attack missed! No damage taken.")
            
            # Handle ranged weapon without arrow (use as melee with no weapon value)
            elif weapon_node and hasattr(weapon_node, "weapon_type") and weapon_node.weapon_type == "ranged" and not has_arrow:
                # Show message about missing arrows
                self.show_message("No arrows! Fighting with bare hands.")
                
                # Take full damage from monster (as if no weapon)
                if monster_value > 0:
                    self.change_health(-monster_value)
                
                # Monster defeats player (add to discard)
                self.animate_card_to_discard(monster)
            
            # Normal melee weapon combat
            else:
                # Monster will be added to stack or discard
                if self.defeated_monsters:
                    if self.defeated_monsters[-1].value > monster_value:
                        damage = monster_value - weapon_value
                        if damage < 0:
                            damage = 0
                        
                        # Apply damage with animation
                        if damage > 0:
                            self.change_health(-damage)
                        
                        monster.z_index = self.z_index_counter
                        self.z_index_counter += 1
                        
                        # Add to defeated monster stack
                        self.defeated_monsters.append(monster)
                        self.position_monster_stack()
                    else:
                        # Apply damage with animation
                        if monster_value > 0:
                            self.change_health(-monster_value)
                        
                        # Animate to discard pile
                        self.animate_card_to_discard(monster)
                else:
                    if monster_value <= weapon_value:
                        monster.z_index = self.z_index_counter
                        self.z_index_counter += 1
                        # Add to defeated monster stack
                        self.defeated_monsters.append(monster)
                        self.position_monster_stack()
                    else:
                        damage = monster_value - weapon_value
                        if damage < 0:
                            damage = 0
                        
                        # Apply damage with animation
                        if damage > 0:
                            self.change_health(-damage)
                        
                        monster.z_index = self.z_index_counter
                        self.z_index_counter += 1
                        # Add to defeated monster stack
                        self.defeated_monsters.append(monster)
                        self.position_monster_stack()
        else:
            # No weapon equipped - take full damage
            # Apply damage with animation
            if monster_value > 0:
                self.change_health(-monster_value)
            
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
        # Check if the card is an arrow (can't be equipped as a weapon)
        if hasattr(weapon, "weapon_type") and weapon.weapon_type == "arrow":
            # Add arrow to inventory instead of equipping
            self.add_to_inventory(weapon)
            self.show_message("Arrows added to inventory")
            return
        
        # First clear previous weapon and monsters
        old_weapon = self.equipped_weapon.get("node", None)
        old_monsters = self.defeated_monsters.copy()
        
        # Update data structures first
        self.room.remove_card(weapon)
        
        # Store weapon type in the equipped_weapon dict
        weapon_type = getattr(weapon, "weapon_type", "melee")  # Default to melee if not specified
        self.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon,
            "weapon_type": weapon_type
        }
        self.defeated_monsters = []
        
        # Set z-index for new weapon
        weapon.z_index = self.z_index_counter
        self.z_index_counter += 1
        
        # Animate new weapon equipping first
        from constants import WEAPON_POSITION
        self.animate_card_movement(weapon, WEAPON_POSITION)
        
        # Show appropriate message based on weapon type
        if weapon_type == "ranged":
            has_arrow = any(card.weapon_type == "arrow" for card in self.inventory if hasattr(card, "weapon_type"))
            if has_arrow:
                self.show_message(f"Equipped {weapon.name}. Arrows ready!")
            else:
                self.show_message(f"Equipped {weapon.name}. No arrows available!")
        else:
            self.show_message(f"Equipped {weapon.name}")
        
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
        # Apply healing with animation
        self.change_health(potion.value)
        
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
        
        # Reset the room state tracking flags when starting a new room
        self.gold_reward_given = False
        self.room_completion_in_progress = False
        
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
                # Check if floor_type is included in card_data, otherwise use self.current_floor
                floor_type = card_data.get("floor_type", self.current_floor)
                card = Card(card_data["suit"], card_data["value"], floor_type)
                
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
        
    # ===== HEALTH MANAGEMENT =====
        
    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""
        # Health display parameters
        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.deck.rect.y
        health_bar_width = 160
        health_bar_height = 40
        
        # Draw background panel
        panel_rect = pygame.Rect(
            health_display_x - 10, 
            health_display_y - health_bar_height - 20,
            health_bar_width + 20,
            health_bar_height + 20
        )
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(panel_surface, WHITE, pygame.Rect(0, 0, panel_rect.width, panel_rect.height), 2, border_radius=10)
        surface.blit(panel_surface, panel_rect)
        
        # Draw health bar background
        bar_bg_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(surface, (60, 60, 60), bar_bg_rect, border_radius=5)
        
        # Calculate health percentage
        health_percent = self.life_points / self.max_life
        health_width = int(health_bar_width * health_percent)
        
        # Choose color based on health percentage
        if health_percent > 0.7:
            health_color = (0, 200, 0)  # Green
        elif health_percent > 0.3:
            health_color = (255, 165, 0)  # Orange
        else:
            health_color = (255, 40, 40)  # Red
        
        # Draw health bar
        if health_width > 0:
            health_rect = pygame.Rect(
                health_display_x,
                health_display_y - health_bar_height - 10,
                health_width,
                health_bar_height
            )
            pygame.draw.rect(surface, health_color, health_rect, border_radius=5)
        
        # Add a subtle inner shadow at the top
        shadow_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            5
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 80))
        surface.blit(shadow_surface, shadow_rect)
        
        # Add highlights at the bottom
        if health_width > 0:
            highlight_rect = pygame.Rect(
                health_display_x,
                health_display_y - 15,
                health_width,
                5
            )
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, 80))
            surface.blit(highlight_surface, highlight_rect)
        
        # Draw health text (current/max)
        health_text = self.body_font.render(f"{self.life_points}/{self.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)
        surface.blit(health_text, health_text_rect)
        
    def draw_gold_display(self, surface):
        """Draw gold display showing current gold amount."""
        # Gold display parameters - placed ABOVE health display
        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.deck.rect.y
        gold_display_x = health_display_x
        gold_display_y = health_display_y - 130  # Position above health display
        
        # Load the gold coin image
        gold_icon = ResourceLoader.load_image("ui/gold.png")
        
        # Draw the gold coin image
        surface.blit(gold_icon, (gold_display_x, gold_display_y))
        
        # Get icon dimensions
        icon_width = gold_icon.get_width()
        icon_height = gold_icon.get_height()
        
        # Draw gold amount with gold-colored text
        gold_text = self.body_font.render(f"{self.game_manager.player_gold}", True, (255, 223, 0))  # Gold text
        gold_text_rect = gold_text.get_rect(left=gold_display_x + icon_width + 15, 
            centery=gold_display_y + icon_height//2)
        
        # Add dark outline to make gold text readable
        gold_outline = self.body_font.render(f"{self.game_manager.player_gold}", True, (100, 70, 0))
        outline_offset = 1
        surface.blit(gold_outline, (gold_text_rect.x + outline_offset, gold_text_rect.y + outline_offset))
        surface.blit(gold_outline, (gold_text_rect.x - outline_offset, gold_text_rect.y + outline_offset))
        surface.blit(gold_outline, (gold_text_rect.x + outline_offset, gold_text_rect.y - outline_offset))
        surface.blit(gold_outline, (gold_text_rect.x - outline_offset, gold_text_rect.y - outline_offset))
        
        # Draw the gold text on top
        surface.blit(gold_text, gold_text_rect)
    
    def change_health(self, amount):
        """Change player health with animation."""
        old_health = self.life_points
        
        # Calculate new health value with limits
        if amount > 0:  # Healing
            # Can't heal beyond max_life
            self.life_points = min(self.life_points + amount, self.max_life)
            actual_change = self.life_points - old_health
            # Only animate if there was an actual change
            if actual_change > 0:
                self.animate_health_change(False, actual_change)  # False = healing
        else:  # Damage
            # Can't go below 0
            self.life_points = max(0, self.life_points + amount)  # amount is negative for damage
            actual_change = old_health - self.life_points
            # Only animate if there was an actual change
            if actual_change > 0:
                self.animate_health_change(True, actual_change)  # True = damage
    
    def animate_health_change(self, is_damage, amount):
        """Create animation for health change."""
        # Position for the animation
        health_display_x = self.deck.rect.x + 100  # Center of health bar
        health_display_y = SCREEN_HEIGHT - self.deck.rect.y - 30  # Middle of health bar
        
        # Create animation
        health_anim = HealthChangeAnimation(
            is_damage,
            amount,
            (health_display_x, health_display_y),
            self.body_font
        )
        
        # Add to animation manager
        self.animation_manager.add_animation(health_anim)
        
    def change_gold(self, amount):
        """Change player gold amount with animation."""
        old_gold = self.game_manager.player_gold
        
        # Update the gold amount in the game manager
        self.game_manager.player_gold += amount
        
        # Ensure gold doesn't go negative
        if self.game_manager.player_gold < 0:
            self.game_manager.player_gold = 0
            
        # Calculate actual change for animation
        actual_change = abs(amount)
        
        # Only animate if there was an actual change
        if actual_change > 0:
            self.animate_gold_change(amount < 0, actual_change)  # True = gold loss, False = gold gain
            
    # ===== INVENTORY METHODS =====
    
    def add_to_inventory(self, card):
        """Add a card to the player's inventory if space is available."""
        if len(self.inventory) >= self.MAX_INVENTORY_SIZE:
            # Inventory is full, can't add more cards
            # TODO: Show a message to the player
            return False
        
        # Mark the card as selected to remove split colors
        card.is_selected = True
        
        # Mark the card as being in inventory to reduce animation
        card.in_inventory = True
        
        # Remove the card from the room
        self.room.remove_card(card)
        
        # Add to inventory
        self.inventory.append(card)
        
        # Animate the card moving to its inventory position
        self.animate_card_to_inventory(card)
        
        # Reposition remaining room cards
        if len(self.room.cards) > 0:
            self.schedule_delayed_animation(
                0.1,
                lambda: self.room.position_cards(animate=True, animation_manager=self.animation_manager)
            )
        
        return True
    
    def animate_card_to_inventory(self, card):
        """Animate a card moving to its position in the inventory."""
        # Calculate position based on inventory panel location
        from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, SPELL_PANEL_HEIGHT
        
        # Calculate vertical center between spell and item panels
        vertical_center = (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT + 
            (ITEM_PANEL_POSITION[1] - (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT))// 2)
        
        # Create a smaller inventory panel
        inv_width = ITEM_PANEL_WIDTH
        inv_height = 120  # Smaller height
        inv_x = SCREEN_WIDTH - inv_width - 40  # Same x as item/spell panels
        inv_y = vertical_center - inv_height // 2  # Center between items and spells
        
        # Scale cards to fit inventory panel nicely
        card_scale = 0.8  # 80% of normal size
        
        # Scale the card
        card.update_scale(card_scale)
        
        # Mark card as being in inventory to reduce animations
        card.in_inventory = True
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Center cards in inventory panel with proper spacing
        margin = 10
        card_spacing = 10  # Fixed spacing between cards
        if self.MAX_INVENTORY_SIZE > 1:
            card_spacing = (inv_width - (self.MAX_INVENTORY_SIZE * scaled_card_width) - (margin * 2)) // max(1, self.MAX_INVENTORY_SIZE - 1)
        
        # Calculate position for this specific card
        inventory_index = len(self.inventory) - 1
        inventory_x = inv_x + margin + (inventory_index * (scaled_card_width + card_spacing))
        inventory_y = inv_y + margin
        
        inventory_pos = (inventory_x, inventory_y)
        
        # Animate the card movement
        self.animate_card_movement(card, inventory_pos)
    
    def position_inventory_cards(self):
        """Position all inventory cards in their proper places."""
        # Calculate position based on inventory panel location
        from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, SPELL_PANEL_HEIGHT
        
        # Calculate vertical center between spell and item panels
        vertical_center = (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT + 
            (ITEM_PANEL_POSITION[1] - (SPELL_PANEL_POSITION[1] + SPELL_PANEL_HEIGHT))// 2)
        
        # Create a smaller inventory panel
        inv_width = ITEM_PANEL_WIDTH
        inv_height = 120  # Smaller height
        inv_x = SCREEN_WIDTH - inv_width - 40  # Same x as item/spell panels
        inv_y = vertical_center - inv_height // 2  # Center between items and spells
        
        # Scale cards to fit inventory panel nicely
        card_scale = 0.8  # 80% of normal size
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Center cards in inventory panel with proper spacing
        margin = 10
        card_spacing = 10  # Fixed spacing between cards
        if self.MAX_INVENTORY_SIZE > 1:
            card_spacing = (inv_width - (self.MAX_INVENTORY_SIZE * scaled_card_width) - (margin * 2)) // max(1, self.MAX_INVENTORY_SIZE - 1)
        
        # Position each card
        for i, card in enumerate(self.inventory):
            # Apply scale to card
            card.update_scale(card_scale)
            
            # Make sure card knows it's in inventory to reduce bobbing
            card.in_inventory = True
            
            # Calculate position
            inventory_x = inv_x + margin + (i * (scaled_card_width + card_spacing))
            inventory_y = inv_y + margin
            
            card.update_position((inventory_x, inventory_y))
    
    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.inventory:
            if card.rect.collidepoint(position):
                return card
        return None
    
    def use_inventory_card(self, card):
        """Use a card from the inventory."""
        if card in self.inventory:
            # Mark the card as selected to ensure no split colors
            card.is_selected = True
            
            # Reset inventory flag since it's being removed
            card.in_inventory = False
            
            # Remove from inventory
            self.inventory.remove(card)
            
            # Reposition remaining inventory cards
            self.position_inventory_cards()
            
            # Process the card effect based on type
            if card.type == "weapon":
                # Reset the card's scale back to original size (1.0)
                card.update_scale(1.0)
                # Add the card back to the room temporarily
                self.room.add_card(card)
                # Use the standard equip weapon logic
                self.equip_weapon(card)
            elif card.type == "potion":
                # Use the potion effect directly
                self.change_health(card.value)
                # Discard the potion
                self.animate_card_to_discard(card)
                
            return True
        return False
    
    def animate_gold_change(self, is_loss, amount):
        """Create animation for gold change."""
        # Load the gold icon to get dimensions
        gold_icon = ResourceLoader.load_image("ui/gold.png")
        icon_width = gold_icon.get_width()
        icon_height = gold_icon.get_height()
        
        # Position for the animation - next to the gold display
        health_display_x = 40
        gold_display_x = health_display_x + icon_width + 30  # Center over gold amount text
        gold_display_y = SCREEN_HEIGHT - self.deck.rect.y - 100 + icon_height//2  # Match gold icon position
        
        # Create animation
        gold_anim = GoldChangeAnimation(
            is_loss,
            amount,
            (gold_display_x, gold_display_y),
            self.body_font
        )
        
        # Add to animation manager
        self.animation_manager.add_animation(gold_anim)
    
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