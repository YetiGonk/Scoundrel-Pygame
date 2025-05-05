""" Playing state for the Roguelike Scoundrel game. """
import pygame
import random
from pygame.locals import *

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_WIDTH, CARD_WIDTH, CARD_HEIGHT,
    INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT, INVENTORY_PANEL_X, INVENTORY_PANEL_Y,
    WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY, FONTS_PATH, WEAPON_POSITION
)

from roguelike_constants import FLOOR_STRUCTURE, WEAPON_RANKS, WEAPON_RANK_MAP, WEAPON_DAMAGE_TYPES, MONSTER_RANKS, MONSTER_DIFFICULTY_MAP
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
from utils.animation import AnimationManager

# Import our modular gameplay classes
from gameplay.card_action_manager import CardActionManager
from gameplay.room_manager import RoomManager
from gameplay.animation_controller import AnimationController
from gameplay.player_state_manager import PlayerStateManager
from gameplay.inventory_manager import InventoryManager
from gameplay.ui_renderer import UIRenderer
from gameplay.game_state_controller import GameStateController
from gameplay.ui_factory import UIFactory


class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""
    
    def __init__(self, game_manager):
        """Initialise the playing state."""
        super().__init__(game_manager)
        
        # Initialise managers and controllers
        self._initialise_managers()
        
        # Initialise game state variables
        self._initialise_state_variables()
        
        # Initialise player state
        self._initialise_player_state()
        
        # Initialise game components
        self._initialise_game_components()
        
        # Initialise UI elements
        self._initialise_ui_elements()
    
    def _initialise_managers(self):
        """Initialise all manager and controller classes."""
        # Initialise animation manager
        self.animation_manager = AnimationManager()
        
        # Initialise resource loader
        self.resource_loader = ResourceLoader
        
        # Initialise our modular managers
        self.card_action_manager = CardActionManager(self)
        self.room_manager = RoomManager(self)
        self.animation_controller = AnimationController(self)
        self.player_state_manager = PlayerStateManager(self)
        self.inventory_manager = InventoryManager(self)
        self.ui_renderer = UIRenderer(self)
        self.game_state_controller = GameStateController(self)
        self.ui_factory = UIFactory(self)
    
    def _initialise_state_variables(self):
        """Initialise general state variables."""
        # Make constants accessible to the class
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_GRAY = LIGHT_GRAY
        
        # Animation and state flags
        self.is_running = False
        self.ran_last_turn = False
        self.show_debug = False
        self.z_index_counter = 0
        
        # Roguelike components
        self.FLOOR_STRUCTURE = FLOOR_STRUCTURE
        
        # Room state tracking
        self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        self.floor_completed = False
        self.gold_reward_given = False
        self.room_completion_in_progress = False 
        self.treasure_transition_started = False
        self.room_started_in_enter = False  # Flag to track if a room was started in enter()
        
        # Message display
        self.message = None
    
    def _initialise_player_state(self):
        """Initialise player stats and inventory."""
        # Player stats
        self.life_points = 20
        self.max_life = 20
        self.gold = 0
        self.equipped_weapon = {}
        self.defeated_monsters = []
        
        # Player inventory
        self.inventory = []
        self.MAX_INVENTORY_SIZE = 2
    
    def _initialise_game_components(self):
        """Initialise game components like deck, discard pile, room."""
        self.deck = None
        self.discard_pile = None
        self.room = None
        self.current_floor = None
    
    def _initialise_ui_elements(self):
        """Initialise UI elements and resources."""
        self.header_font = None
        self.body_font = None
        self.caption_font = None
        self.normal_font = None
        self.run_button = None
        self.background = None
        self.floor = None
        
        # Status UI & HUD
        self.status_ui = StatusUI(self.game_manager)
        self.hud = HUD(self.game_manager)

    def enter(self):
        """Initialise the playing state when entering."""
        print(f"PlayingState.enter() called - current room: {self.game_manager.floor_manager.current_room}")
        
        # Load resources
        self._load_resources()
        
        # Initialise game components 
        self._setup_game_components()
        
        # Handle player state setup
        self._setup_player_state()
        
        # Handle treasure room transition if needed
        self._handle_treasure_transition()
        
        # Start initial room
        self._start_initial_room()
        
        # Reset state tracking
        self._reset_state_tracking()
    
    def _load_resources(self):
        """Load fonts, background and floor image."""
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.caption_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.normal_font = pygame.font.SysFont(None, 20)

        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load floor based on current floor type
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()
        
        # Choose the appropriate floor image
        floor_image = f"floors/{current_floor_type}_floor.png"
            
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def _setup_game_components(self):
        """Initialise deck, discard pile, and room."""
        # Initialise floor information
        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()
        
        # Make sure we have a valid floor
        if not self.current_floor:
            print(f"Warning: Floor is not initialised. Using fallback.")
            self.current_floor = "dungeon"  # Fallback to dungeon if floor is None
        
        # Create a new deck and discard pile
        self.deck = Deck(self.current_floor, self.game_manager.floor_manager)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)
        
        # Initialise the visual representation for deck and discard pile
        if hasattr(self.deck, "initialise_visuals"):
            self.deck.initialise_visuals()
            
        if hasattr(self.discard_pile, "initialise_visuals"):
            self.discard_pile.initialise_visuals()
            
        # Position inventory cards
        if hasattr(self, "inventory_manager") and hasattr(self.inventory_manager, "position_inventory_cards"):
            self.inventory_manager.position_inventory_cards()

        # Create UI buttons
        self.ui_factory.create_run_button()
    
    def _setup_player_state(self):
        """Set up player stats and equipped weapon."""
        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
        self.gold = self.game_manager.game_data.get("gold", 0)  # Get gold from game data
    
    def _handle_treasure_transition(self):
        """Initialize weapons and monsters (treasure room functionality removed)."""
        # Initialize equipped weapon and defeated monsters
        self.equipped_weapon = {}
        self.defeated_monsters = []
        return  # Early return - treasure rooms removed
            self.equipped_weapon = self.game_manager.equipped_weapon
            
            # Ensure weapon has all required properties
            if "node" in self.equipped_weapon:
                weapon_card = self.equipped_weapon["node"]
                
                # Make sure type is set
                weapon_card.type = "weapon"
                weapon_card.is_equipped = True
                
                # Make sure weapon_type is set
                if not hasattr(weapon_card, 'weapon_type') or not weapon_card.weapon_type:
                    import random
                    rank = WEAPON_RANKS.get(weapon_card.value, "novice")
                    weapon_options = WEAPON_RANK_MAP.get(rank, ["dagger"])
                    weapon_card.weapon_type = random.choice(weapon_options)
                
                # Make sure weapon_difficulty is set
                if not hasattr(weapon_card, 'weapon_difficulty') or not weapon_card.weapon_difficulty:
                    weapon_card.weapon_difficulty = WEAPON_RANKS.get(weapon_card.value, "novice")
                
                # Make sure damage_type is set
                if not hasattr(weapon_card, 'damage_type') or not weapon_card.damage_type:
                    weapon_card.damage_type = WEAPON_DAMAGE_TYPES.get(weapon_card.weapon_type, "slashing")
                
                # Make sure name is set
                if not hasattr(weapon_card, 'name') or not weapon_card.name:
                    weapon_display_name = weapon_card.weapon_type.capitalize()
                    weapon_card.name = f"{weapon_display_name} {weapon_card._to_roman(weapon_card.value)}"
                    
                # Set default position for the weapon
                weapon_card.update_position(WEAPON_POSITION)
        
            # Handle defeated monsters
            if hasattr(self.game_manager, 'defeated_monsters') and self.game_manager.defeated_monsters:
                # Get monsters from treasure room
                self.defeated_monsters = self.game_manager.defeated_monsters
                
                # Ensure all defeated monsters have the required properties set
                for monster in self.defeated_monsters:
                    monster.is_defeated = True
                    monster.type = "monster"
                    
                    # Set sprite file path if missing
                    if not hasattr(monster, 'sprite_file_path') or not monster.sprite_file_path:
                        import random
                        difficulty = MONSTER_RANKS.get(monster.value, "easy")
                        monster.sprite_file_path = random.choice(MONSTER_DIFFICULTY_MAP[difficulty])
                    
                    # Set monster type if missing
                    if not hasattr(monster, 'monster_type') or not monster.monster_type:
                        monster.monster_type = monster.sprite_file_path.split("/")[-2] if hasattr(monster, 'sprite_file_path') and monster.sprite_file_path else "Unknown"
                    
                    # Set name if missing
                    if not hasattr(monster, 'name') or not monster.name:
                        sprite_name = monster.sprite_file_path.split("/")[-1].split(".")[0].upper() if hasattr(monster, 'sprite_file_path') and monster.sprite_file_path else "Monster"
                        monster.name = f"{sprite_name} {monster._to_roman(monster.value)}"
                
                # Position monster stack
                if hasattr(self, "animation_controller") and hasattr(self.animation_controller, "position_monster_stack"):
                    self.animation_controller.position_monster_stack()
            
            # Clear the stored data
            self.game_manager.equipped_weapon = {}
            self.game_manager.defeated_monsters = []
        else:
            self.equipped_weapon = {}
            self.defeated_monsters = []
    
    def _start_initial_room(self):
        """Start the initial room either with a preserved card or fresh."""
        # Treasure room transitions removed
        
        # Initialize deck with no player cards
        self.deck.initialise_deck(None)
        
        # Clear the discard pile when starting a new floor
        if self.discard_pile:
            self.discard_pile.cards = []
            if hasattr(self.discard_pile, 'card_stack'):
                self.discard_pile.card_stack = []
        
        # Card preservation removed - no treasure rooms
        
        # Start a normal room
        print(f"Starting room in enter() - room: {self.game_manager.floor_manager.current_room}")
        self.room_manager.start_new_room()
        # Set flag that we've started a room in enter
        self.room_started_in_enter = True
        
        # Treasure and merchant functionality removed
        
        # Update status UI fonts
        self.status_ui.update_fonts(self.header_font, self.normal_font)

        # Update HUD fonts
        self.hud.update_fonts(self.normal_font, self.normal_font)
    
    def _reset_state_tracking(self):
        """Reset game state tracking variables."""
        # Reset floor completion tracking
        self.floor_completed = False
        self.treasure_transition_started = False

        # Reset completed_rooms counter if starting a new floor
        if self.game_manager.floor_manager.current_room == 1:
            self.completed_rooms = 0

    def exit(self):
        """Save state when exiting playing state."""
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life
        self.game_manager.game_data["gold"] = self.gold

    def handle_event(self, event):
        """Handle player input events."""
        if self.animation_manager.is_animating():
            return  # Don't handle events while animating
        
        if event.type == MOUSEMOTION:
            self._handle_hover(event)
                    
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self._handle_click(event)
    
    def _handle_hover(self, event):
        """Handle mouse hover events over cards and buttons."""
        # Check hover for cards in the room
        inventory_is_full = len(self.inventory) >= self.MAX_INVENTORY_SIZE
        
        # Prepare all cards for hover detection
        all_hoverable_cards = []
        
        # Setup room cards
        for card in self.room.cards:
            # For monster cards, set the weapon_available flag based on equipped weapon
            if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
                card.weapon_available = bool(self.equipped_weapon)
                
                if self.equipped_weapon and self.defeated_monsters:
                    card.weapon_attack_not_viable = card.value >= self.defeated_monsters[-1].value
                else:
                    card.weapon_attack_not_viable = False
            
            # For cards that can be added to inventory, check if inventory is full
            if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
                card.inventory_available = not inventory_is_full
            
            # Add card to hoverable cards if it collides with mouse
            # Reset hover status first
            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)
        
        # Setup inventory cards
        for card in self.inventory:
            # Reset hover status first
            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)
            
        # Setup equipped weapon
        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]
            # Reset hover status first
            weapon_card.is_hovered = False
            if weapon_card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(weapon_card)
        
        # Setup defeated monsters
        for monster in self.defeated_monsters:
            # Reset hover status first
            monster.is_hovered = False
            if monster.rect.collidepoint(event.pos):
                all_hoverable_cards.append(monster)
        
        # Find the closest card to mouse cursor
        if all_hoverable_cards:
            closest_card = self._find_closest_card(event.pos, all_hoverable_cards)
            # Only set the closest card as hovered
            if closest_card:
                closest_card.check_hover(event.pos)
        
        # Check hover for buttons
        self.run_button.check_hover(event.pos)
    
    def _find_closest_card(self, pos, cards):
        """Find the card closest to the given position."""
        if not cards:
            return None
            
        closest_card = None
        closest_distance = float('inf')
        
        for card in cards:
            # Calculate distance from mouse to card center
            card_center_x = card.rect.centerx
            card_center_y = card.rect.centery
            
            # Calculate total float offset for more accurate hover detection
            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset
            
            # Adjust center Y with float offset
            card_center_y -= total_float_offset
            
            # Calculate squared distance (faster than sqrt)
            dist_sq = (pos[0] - card_center_x) ** 2 + (pos[1] - card_center_y) ** 2
            
            if dist_sq < closest_distance:
                closest_distance = dist_sq
                closest_card = card
        
        return closest_card
    
    def _handle_click(self, event):
        """Handle mouse click events."""
        if self.life_points <= 0:
            return  # Don't handle clicks if player is dead
            
        # Check if run button was clicked
        if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
            self.room_manager.run_from_room()
            return
                    
        # Check if a card was clicked
        clicked_card = None
        
        # First check room cards
        card = self.room.get_card_at_position(event.pos)
        if card:
            self.card_action_manager.resolve_card(card, event_pos=event.pos)
            return  # Important: Return to prevent checking inventory cards
        
        # If no room card was clicked, check inventory cards
        clicked_inventory_card = self.inventory_manager.get_inventory_card_at_position(event.pos)
        if clicked_inventory_card:
            self.card_action_manager.use_inventory_card(clicked_inventory_card, event.pos)
            return  # Important: Return to prevent checking equipped weapon
        
        # If no room card or inventory card was clicked, check equipped weapon
        if "node" in self.equipped_weapon and self.equipped_weapon["node"].rect.collidepoint(event.pos):
            self.card_action_manager.discard_equipped_weapon()

    def update(self, delta_time):
        """Update game state for this frame."""
        # Update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update message and cards
        self._update_message(delta_time)
        self._update_cards(delta_time)
        
        # Only process game state changes if we're not animating or animations just finished
        if not current_animating:
            self._process_game_state(animations_just_finished)
        
        # Check for game over
        self.game_state_controller.check_game_over()
    
    def _update_message(self, delta_time):
        """Update any active message fade animation."""
        if hasattr(self, 'message') and self.message and 'alpha' in self.message:
            # Update fade-in/fade-out animation
            if self.message['fade_in']:
                # Fading in
                self.message['alpha'] = min(255, self.message['alpha'] + self.message['fade_speed'] * delta_time)
                # Check if fade-in is complete
                if self.message['alpha'] >= 255:
                    self.message['fade_in'] = False
            else:
                # Update timer
                self.message['time_remaining'] -= delta_time
                # If timer expired, start fading out
                if self.message['time_remaining'] <= 0:
                    self.message['alpha'] = max(0, self.message['alpha'] - self.message['fade_speed'] * delta_time)
                    # Clear message when fully transparent
                    if self.message['alpha'] <= 0:
                        self.message = None
    
    def _update_cards(self, delta_time):
        """Update all card animations."""
        # Update room cards
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
    
    def _process_game_state(self, animations_just_finished):
        """Process game state changes after animations."""
        # If we were running and animations finished, complete the run
        if self.is_running:
            self.room_manager.on_run_completed()
            return
        
        # Process room state only when no animations are running
        # If we just started a room in enter, room_started_in_enter will be True
        if self.room_started_in_enter:
            print(f"Skipping room completion in update because room_started_in_enter=True")
            self.room_started_in_enter = False
            return
        
        # Handle empty room - check for room completion
        if len(self.room.cards) == 0:
            self._handle_empty_room()
        
        # If we have only one card left and animations just finished, start a new room
        # But only if we didn't just start one in enter()
        elif len(self.room.cards) == 1 and animations_just_finished and len(self.deck.cards) > 0:
            self._handle_single_card_room()
    
    def _handle_empty_room(self):
        """Handle logic for when the room is empty (all cards processed)."""
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
            self.player_state_manager.change_gold(gold_reward)

        # Go directly to the next room if we have cards
        if len(self.deck.cards) > 0:
            print(f"Room completed with empty room, advancing to next room. Cards in deck: {len(self.deck.cards)}")
            # More cards in deck - advance to next room
            self.game_manager.advance_to_next_room()
            
            # Check if we're still in the playing state (not moved to another state)
            if self.game_manager.current_state == self:
                # Start a new room
                self.room_manager.start_new_room()
        else:
            # No more cards in the deck - floor completed
            self._handle_floor_completion()
    
    def _handle_single_card_room(self):
        """Handle logic for rooms with a single card remaining."""
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
            self.player_state_manager.change_gold(gold_reward)
        
        # Start a new room with the remaining card - merchant check happens inside start_new_room
        self.room_manager.start_new_room(self.room.cards[0])
    
    def _handle_floor_completion(self):
        """Handle logic for when the floor is completed."""
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
                # Not the last floor, show a brief message and advance to next floor
                floor_type = self.game_manager.floor_manager.get_current_floor()
                next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
                next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
                self.game_state_controller.show_message(f"Floor {floor_type.capitalize()} completed! Moving to {next_floor_type.capitalize()}...")
                
                # Schedule transition to next floor after a short delay
                self.animation_controller.schedule_delayed_animation(
                    3.0,  # 3 second delay to show the message
                    lambda: self.room_manager.transition_to_next_floor()
                )

    def draw(self, surface):
        """Draw game elements to the screen."""
        # Draw background and floor
        self._draw_background(surface)
        
        # Draw game components
        self._draw_cards_and_piles(surface)
        
        # Draw inventory panel and cards
        self._draw_inventory(surface)
        
        # Draw UI elements
        self._draw_ui_elements(surface)
    
    def _draw_background(self, surface):
        """Draw background and floor."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
    
    def _draw_cards_and_piles(self, surface):
        """Draw deck, discard pile, equipped weapon, and defeated monsters."""
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
    
    def _draw_inventory(self, surface):
        """Draw inventory panel and cards."""
        vertical_center = SCREEN_HEIGHT // 2
        
        # Create an inventory panel - taller and wider to accommodate full-size vertical card stack
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Create the inventory panel using the Panel class
        if not hasattr(self, 'inventory_panel'):
            # Define a slightly more brown colour for the inventory panel to look more like aged parchment
            parchment_colour = (60, 45, 35)
            self.inventory_panel = Panel(
                (inv_width, inv_height), 
                (inv_x, inv_y),
                colour=parchment_colour,
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)  # Slightly lighter brown for border
            )
        
        # Draw the panel
        self.inventory_panel.draw(surface)
        
        # Get the rect for positioning
        inv_rect = self.inventory_panel.rect
        
        # Draw title with a slight glow effect for a magical appearance
        inv_title = self.body_font.render("Inventory", True, WHITE)
        # Create a subtle glow
        glow_surface = pygame.Surface((inv_title.get_width() + 10, inv_title.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (255, 240, 200, 50)  # Soft golden glow
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        
        # Position the glow and title text
        glow_rect = glow_surface.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 35)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)
        
        # Draw the glow and title
        surface.blit(glow_surface, glow_rect)
        surface.blit(inv_title, title_rect)
        
        # First sort inventory cards so hovered ones are at the end (will be drawn on top)
        # Use a stable sort so if there are multiple cards, their original order is preserved
        sorted_cards = sorted(self.inventory, key=lambda c: 1 if c.is_hovered else 0)
        
        # First pass - draw shadows for all cards
        for card in sorted_cards:
            self.ui_renderer._draw_card_shadow(surface, card)
        
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
                    if hasattr(card, 'damage_type') and card.damage_type:
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                elif card.type == "potion":
                    type_text = "HEALING"
    
    def _draw_ui_elements(self, surface):
        """Draw room cards, UI elements, and status displays."""
        # Draw room cards LAST always
        self.room.draw(surface)
        
        # Draw any visual effects (destruction/materialise animations)
        self.animation_manager.draw_effects(surface)
        
        # Draw hover text for inventory cards
        for card in self.inventory:
            if card.is_hovered and card.face_up:
                card.draw_hover_text(surface)
        
        # Draw hover text for equipped weapon
        if "node" in self.equipped_weapon and self.equipped_weapon["node"].is_hovered and self.equipped_weapon["node"].face_up:
            self.equipped_weapon["node"].draw_hover_text(surface)
        
        # Ensure all monsters in defeated_monsters have the is_defeated flag set
        for monster in self.defeated_monsters:
            monster.is_defeated = True
            
        # Draw hover text for defeated monsters
        for monster in self.defeated_monsters:
            if monster.is_hovered and monster.face_up:
                monster.draw_hover_text(surface)
        
        # Draw health display
        self.ui_renderer.draw_health_display(surface)
        
        # Draw gold display
        self.ui_renderer.draw_gold_display(surface)

        # Draw deck count display
        self.ui_renderer.draw_deck_count(surface)

        # Draw UI animations (health changes, etc.)
        self.animation_manager.draw_ui_effects(surface)
            
        # Draw run button
        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:
            # Draw disabled run button with consistent styling
            button_rect = self.run_button.rect
            
            # Button background
            pygame.draw.rect(surface, LIGHT_GRAY, button_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=5)
            
            # Render disabled text with the same font as the active button
            button_text = self.body_font.render("RUN", True, (150, 150, 150))  # Greyed out text
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)
            
        # Draw any active message with fade effect
        self._draw_message(surface)
        
        # Draw status UI
        self.status_ui.draw(surface)
    
    def _draw_message(self, surface):
        """Draw any active message with fade effect."""
        if hasattr(self, 'message') and self.message:
            # Handle new fade-in/fade-out message style
            if "alpha" in self.message:
                # Create a temporary copy of the message for this frame with current alpha value
                current_alpha = self.message["alpha"]
                text_with_alpha = self.message["text"].copy()
                text_with_alpha.set_alpha(current_alpha)
                
                # Create a semi-transparent background
                bg_surface = pygame.Surface((self.message["bg_rect"].width, self.message["bg_rect"].height), pygame.SRCALPHA)
                bg_colour = (0, 0, 0, int(current_alpha * 0.7))  # Background slightly more transparent than text
                pygame.draw.rect(bg_surface, bg_colour, bg_surface.get_rect(), border_radius=8)
                
                # Create a very subtle border
                border_colour = (200, 200, 200, int(current_alpha * 0.5))
                pygame.draw.rect(bg_surface, border_colour, bg_surface.get_rect(), 1, border_radius=8)
                
                # Draw the message
                surface.blit(bg_surface, self.message["bg_rect"])
                surface.blit(text_with_alpha, self.message["rect"])
            else:
                # Fallback for old message format (just in case)
                pygame.draw.rect(surface, BLACK, self.message["bg_rect"], border_radius=8)
                pygame.draw.rect(surface, WHITE, self.message["bg_rect"], 2, border_radius=8)
                surface.blit(self.message["text"], self.message["rect"])
    
    # Forward key methods to our modular components
    def change_health(self, amount):
        """Forward health change to player state manager."""
        self.player_state_manager.change_health(amount)
    
    def change_gold(self, amount):
        """Forward gold change to player state manager."""
        self.player_state_manager.change_gold(amount)
    
    def position_inventory_cards(self):
        """Forward inventory positioning to inventory manager."""
        self.inventory_manager.position_inventory_cards()
    
    def animate_card_to_discard(self, card):
        """Forward card discard animation to animation controller."""
        self.animation_controller.animate_card_to_discard(card)
    
    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, on_complete=None):
        """Forward card movement animation to animation controller."""
        self.animation_controller.animate_card_movement(card, target_pos, duration, easing, on_complete)
    
    def schedule_delayed_animation(self, delay, callback):
        """Forward delayed animation to animation controller."""
        self.animation_controller.schedule_delayed_animation(delay, callback)
    
    def start_card_flip(self, card):
        """Forward card flip to animation controller."""
        self.animation_controller.start_card_flip(card)
    
    def position_monster_stack(self):
        """Forward monster stack positioning to animation controller."""
        self.animation_controller.position_monster_stack()
    
    def animate_card_to_inventory(self, card):
        """Forward card inventory animation to animation controller."""
        self.animation_controller.animate_card_to_inventory(card)
    
    def show_message(self, message, duration=2.0):
        """Forward message display to game state controller."""
        self.game_state_controller.show_message(message, duration)
        
    # Treasure functionality removed