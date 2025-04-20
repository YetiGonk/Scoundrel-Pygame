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
from utils.save_manager import save_manager


class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""
    
    def __init__(self, game_manager):
        """Initialize the playing state."""
        super().__init__(game_manager)
        
        # Make constants accessible to the class
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_GRAY = LIGHT_GRAY
        
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
        self.animation_manager = None  # Will be initialized in enter()
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

        # Status UI & HUD - these will be reinitialized in enter()
        self.status_ui = None
        self.hud = None

        # Add item/spell UI elements
        self.item_panel = None
        self.spell_panel = None
        
    def _initialize_card_visuals(self):
        """Initialize visual properties for all cards in the game state.
        This is crucial for cards loaded from save files, which might be
        missing visual/display properties."""
        # Define standard visual properties for cards
        hover_props = {
            "hover_selection": True,
            "idle_float_amount": 2,
            "idle_float_speed": 0.5,
            "hover_float_offset": 0,
            "idle_float_offset": 0,
            "is_hovered": False,
            "face_up": True
        }
        
        # Update equipped weapon if it exists
        if self.equipped_weapon and "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]
            
            # Set position for the weapon card
            weapon_card.update_position((100, 100))
                
            # Set visual properties
            for prop, value in hover_props.items():
                if not hasattr(weapon_card, prop):
                    setattr(weapon_card, prop, value)
        
        # Update defeated monsters
        for i, monster in enumerate(self.defeated_monsters):
            # Set position for each monster
            new_pos_x = 100 + i * 30
            monster.update_position((new_pos_x, 200))
            
            # Set visual properties
            for prop, value in hover_props.items():
                if not hasattr(monster, prop):
                    setattr(monster, prop, value)
        
        # Update inventory cards
        for i, card in enumerate(self.inventory):
            # Make sure inventory cards have positions
            # Position will be properly set by UI renderer, just initialize
            card.update_position((300 + i * 80, 500))
            
            # Set visual properties
            for prop, value in hover_props.items():
                if not hasattr(card, prop):
                    setattr(card, prop, value)
        
        # Add completed room counter
        # Don't initialize completed_rooms here, as it will be properly initialized in enter()
        # The enter() method will set this based on the current_room_number
        if not hasattr(self, 'completed_rooms'):
            self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        
        # Add flag for completed floor - ALWAYS start with False
        self.floor_completed = False
        
        # Add flags for room state tracking
        self.gold_reward_given = False
        self.room_completion_in_progress = False
        self.merchant_transition_started = False
        
        # Initialize message display
        self.message = None
        
        # Initialize resource loader
        self.resource_loader = ResourceLoader

        # Modular managers will be initialized in enter()
        self.card_action_manager = None
        self.room_manager = None
        self.animation_controller = None
        self.player_state_manager = None
        self.inventory_manager = None
        self.ui_renderer = None
        self.game_state_controller = None
        self.ui_factory = None

    def enter(self):
        """Initialize the playing state when entering."""
        print("Entering playing state - initializing components...")
        
        try:
            # Initialize animation manager first as others depend on it
            self.animation_manager = AnimationManager()
            
            # Initialize our modular managers in a specific order based on dependencies
            # We need to make sure all managers are created before we try to use them,
            # especially room_manager which is used at the end of this method
            self.card_action_manager = CardActionManager(self)
            self.room_manager = RoomManager(self)  # Used for start_new_room() later
            self.animation_controller = AnimationController(self)
            self.player_state_manager = PlayerStateManager(self)
            self.inventory_manager = InventoryManager(self)
            self.ui_renderer = UIRenderer(self)
            self.game_state_controller = GameStateController(self)
            self.ui_factory = UIFactory(self)
            
            # Verify all managers were properly initialized
            if (self.animation_manager is None or self.room_manager is None or
                self.card_action_manager is None or self.player_state_manager is None or
                self.inventory_manager is None or self.ui_renderer is None or
                self.game_state_controller is None or self.ui_factory is None):
                print("WARNING: Some managers failed to initialize. Using fallback initialization.")
                self._ensure_managers_initialized()
                
        except Exception as e:
            print(f"ERROR during manager initialization: {e}")
            # Try to recover using our safe initialization method
            self._ensure_managers_initialized()
        
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = pygame.font.SysFont(None, 20)
        
        # Initialize UI
        self.status_ui = StatusUI(self.game_manager)
        self.hud = HUD(self.game_manager)

        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load floor based on current floor type
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()
        is_merchant = floor_manager.is_merchant_room()
        
        # Choose the appropriate floor image
        if is_merchant:
            floor_image = "floors/merchant_floor.png"
        else:
            floor_image = f"floors/{current_floor_type}_floor.png"
            
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        # Initialize game components
        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()
        
        # CRITICAL FIX: When floor_manager.current_room = rooms_per_floor (floor completed),
        # we need to set current_room_number to avoid auto-completion
        from roguelike_constants import FLOOR_STRUCTURE
        if floor_manager.current_room >= FLOOR_STRUCTURE["rooms_per_floor"]:
            # At floor end, set to one less to avoid auto-completion
            self.current_room_number = FLOOR_STRUCTURE["rooms_per_floor"] - 1
            print(f"[DEBUG] Prevented auto-completion: current_room_number set to {self.current_room_number}")
        else:
            self.current_room_number = floor_manager.current_room
        
        # Setup/reset the game components with the newly initialized animation manager
        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        # Create run button
        self.ui_factory.create_run_button()

        # Create UI elements in the correct order
        self.ui_factory.create_item_spell_panels()  # First create the panels
        self.ui_factory.create_item_buttons()       # Then create the buttons
        self.ui_factory.create_spell_buttons()
        
        # Update status UI fonts
        self.status_ui.update_fonts(self.header_font, self.normal_font)
        # Update HUD fonts
        self.hud.update_fonts(self.normal_font, self.normal_font)

        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
        self.gold = self.game_manager.player_gold  # Get gold directly 
        
        # Check if new game/floor or coming back from merchant or loading a saved game
        if self.current_room_number == 0:
            # Starting a new floor, clear weapons and monsters
            self.equipped_weapon = {}
            self.defeated_monsters = []
        elif hasattr(self.game_manager, 'equipped_weapon') and self.game_manager.equipped_weapon:
            self.equipped_weapon = self.game_manager.equipped_weapon
        else:
            self.equipped_weapon = {}
            
        # Restore defeated monsters if they exist
        if self.current_room_number == 0:
            # Starting a new floor, clear defeated monsters
            self.defeated_monsters = []
        elif hasattr(self.game_manager, 'defeated_monsters') and self.game_manager.defeated_monsters:
            self.defeated_monsters = self.game_manager.defeated_monsters
        else:
            self.defeated_monsters = []
            
        # Make sure cards have the proper visual properties
        # This is crucial for loaded cards to display correctly
        self._initialize_card_visuals()
            
        # Don't clear the stored data from game_manager anymore - we need it for saving
        # We'll let the exit method handle updating the game_manager with our state
            
        self.damage_shield = 0
        
        # Check if we're coming from merchant room
        coming_from_merchant = hasattr(self.game_manager, 'coming_from_merchant') and self.game_manager.coming_from_merchant
        
        # Initialize the deck if needed
        if not coming_from_merchant:
            # Get player's delving deck if it exists
            player_deck = self.game_manager.delving_deck if hasattr(self.game_manager, 'delving_deck') else None
            
            # Check if we're resuming a saved game mid-floor
            resuming_saved_game = hasattr(self, 'completed_rooms') and self.completed_rooms > 0
            
            # If we're not resuming a saved game, or if the deck is empty, reinitialize it
            # This prevents the deck from being re-initialized when loading a saved game mid-floor
            if not resuming_saved_game or len(self.deck.cards) == 0:
                # Initialize deck with player cards shuffled in
                self.deck.initialise_deck(player_deck)
                
                # Also clear the discard pile when starting a new floor (not from merchant)
                if self.discard_pile:
                    self.discard_pile.cards = []
                    if hasattr(self.discard_pile, 'card_stack'):
                        self.discard_pile.card_stack = []
        
        # Initialize last_card variable
        last_card_from_merchant = None
        
        # Debug: print our current state when coming from merchant
        if coming_from_merchant:
            print("Coming from merchant room")
            print(f"Has last_card_data: {hasattr(self.game_manager, 'last_card_data')}")
            if hasattr(self.game_manager, 'last_card_data'):
                print(f"last_card_data is None: {self.game_manager.last_card_data is None}")
        
        # If we have preserved card data, prepare it for the next room
        if coming_from_merchant and hasattr(self.game_manager, 'last_card_data') and self.game_manager.last_card_data:
            # Create a card object from the stored data
            card_data = self.game_manager.last_card_data
            last_card_from_merchant = Card(card_data["suit"], card_data["value"], card_data.get("floor_type", self.current_floor))
            last_card_from_merchant.face_up = True
            
            # Set initial position for the card (will be positioned properly by start_new_room)
            # This ensures it doesn't appear in the top-left corner before being properly positioned
            # Use a position that would be reasonable for a room card
            num_cards = 1  # Just this card initially
            total_width = (CARD_WIDTH * num_cards)
            start_x = (SCREEN_WIDTH - total_width) // 2
            start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
            last_card_from_merchant.update_position((start_x, start_y))
            
            # Now clear the stored card data
            self.game_manager.last_card_data = None
            
            try:
                # Start a new room with the preserved card
                self.room_manager.start_new_room(last_card_from_merchant)
            except Exception as e:
                print(f"Error starting room with preserved card: {e}")
                # Fallback to empty room if there's an error
                self.room_manager.start_new_room()
        else:
            try:
                # No card was preserved or not coming from merchant, start a normal room
                self.room_manager.start_new_room()
            except Exception as e:
                print(f"Error starting new room: {e}")
        
        # Reset coming_from_merchant flag after handling the transition
        self.game_manager.coming_from_merchant = False
        
        # Reset floor completion tracking - ALWAYS FALSE on entry
        self.floor_completed = False
        self.merchant_transition_started = False
        self.room_completion_in_progress = False
        self.gold_reward_given = False

        # Reset room counter if starting a new floor
        if self.current_room_number == 0:
            self.completed_rooms = 0
        # Initialize completed_rooms if not already set - avoid using current_room_number directly
        elif not hasattr(self, 'completed_rooms'):
            # CRITICAL FIX: We cannot set completed_rooms = current_room_number directly
            # If current_room_number is at max (from floor completion), it would auto-complete
            from roguelike_constants import FLOOR_STRUCTURE
            
            # Always set to at least 1 less than max, or to current_room_number if less
            # This ensures we always have at least one more room to complete
            if self.current_room_number >= FLOOR_STRUCTURE["rooms_per_floor"] - 1:
                self.completed_rooms = FLOOR_STRUCTURE["rooms_per_floor"] - 2
                print(f"[DEBUG] Set completed_rooms to {self.completed_rooms} to ensure at least one more room")
            else:
                self.completed_rooms = self.current_room_number
                
        # Make sure deck is not empty when loading a saved game mid-floor
        # Empty deck + non-zero completed_rooms would trigger floor completion
        if len(self.deck.cards) == 0 and self.current_room_number > 0 and not self.room.cards:
            # Re-initialize the deck with a few cards to prevent auto-completion
            print("[DEBUG] Adding cards to prevent empty deck auto-completion")
            player_deck = self.game_manager.delving_deck if hasattr(self.game_manager, 'delving_deck') else None
            self.deck.initialise_deck(player_deck)

    def exit(self):
        """Save state when exiting playing state."""
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life
        self.game_manager.player_gold = self.gold  # Save to player_gold, not game_data["gold"]
        
        # Store equipped weapon and defeated monsters to preserve between states
        if hasattr(self, 'equipped_weapon') and self.equipped_weapon:
            self.game_manager.equipped_weapon = self.equipped_weapon
        
        if hasattr(self, 'defeated_monsters') and self.defeated_monsters:
            self.game_manager.defeated_monsters = self.defeated_monsters
            
        # Save the complete game state when exiting the playing state
        # This ensures the game can be continued from this point later
        save_manager.save_game_state(self.game_manager)

    def handle_event(self, event):
        """Handle player input events."""
        if self.animation_manager.is_animating():
            return  # Don't handle events while animating
        
        if event.type == MOUSEMOTION:
            # Check hover for cards in the room
            inventory_is_full = len(self.inventory) >= self.MAX_INVENTORY_SIZE
            
            for card in self.room.cards:
                # For monster cards, set the weapon_available flag based on equipped weapon
                if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
                    card.weapon_available = bool(self.equipped_weapon)
                
                # For cards that can be added to inventory, check if inventory is full
                if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
                    card.inventory_available = not inventory_is_full
                
                # Check hover status for all cards
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
                self.room_manager.run_from_room()
                return
            
            # Check if an item button was clicked
            for item_data in self.item_buttons:
                if item_data["button"].is_clicked(event.pos):
                    self.player_state_manager.use_item(item_data["index"])
                    return
            
            # Check if a spell button was clicked
            for spell_data in self.spell_buttons:
                if spell_data["button"].is_clicked(event.pos):
                    self.player_state_manager.cast_spell(spell_data["index"])
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
                self.card_action_manager.use_inventory_card(clicked_inventory_card)
    
    def update(self, delta_time):
        """Update game state for this frame."""
        # Ensure all managers are properly initialized FIRST before any game logic
        # This is critical to prevent NoneType errors
        self._ensure_managers_initialized()
        
        # Safety check - if we still don't have critical managers, return early
        if (self.animation_manager is None or self.room_manager is None or 
            self.card_action_manager is None or self.player_state_manager is None):
            print("CRITICAL ERROR: Unable to initialize essential managers. Skipping update.")
            return
            
        # Now it's safe to update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update any active message fade animation
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
                self.room_manager.on_run_completed()
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
                    
                    # Safely update gold
                    try:
                        if self.player_state_manager:
                            self.player_state_manager.change_gold(gold_reward)
                        else:
                            # Fallback - update gold directly
                            print("Using direct gold update fallback")
                            self.gold += gold_reward
                    except Exception as e:
                        print(f"Error updating gold: {e}")
                        # Emergency fallback
                        self.gold += gold_reward

                # Go directly to the next room if we have cards
                if len(self.deck.cards) > 0:
                    # More cards in deck - advance to next room
                    self.game_manager.advance_to_next_room()
                    
                    # Check if we're still in the playing state (not moved to merchant or other state)
                    if self.game_manager.current_state == self:
                        # Start a new room
                        self.room_manager.start_new_room()
                else:
                    # No more cards in the deck - floor completed
                    # SAFETY CHECK: Only complete the floor if we've completed enough rooms
                    # This prevents auto-completion when loading a saved game
                    from roguelike_constants import FLOOR_STRUCTURE
                    if not self.floor_completed and self.completed_rooms >= FLOOR_STRUCTURE["rooms_per_floor"] - 1:
                        print(f"[DEBUG] Floor completed with {self.completed_rooms} completed rooms")
                        self.floor_completed = True
                        
                        # Mark this floor as completed
                        self.game_manager.floor_manager.current_room = self.FLOOR_STRUCTURE["rooms_per_floor"]
                        
                        # Check if this is the last floor
                        if self.game_manager.floor_manager.current_floor_index >= len(self.game_manager.floor_manager.floors) - 1:
                            # Last floor completed - victory!
                            # Add any purchased cards to the player's permanent collection
                            self._add_purchased_cards_to_library()
                            
                            self.game_manager.game_data["victory"] = True
                            self.game_manager.game_data["run_complete"] = True
                            self.game_manager.change_state("game_over")
                        else:
                            # Not the last floor, show a brief message and advance to next floor
                            # Add any purchased cards to the player's permanent collection
                            self._add_purchased_cards_to_library()
                            
                            floor_type = self.game_manager.floor_manager.get_current_floor()
                            next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
                            next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
                            self.game_state_controller.show_message(f"Floor {floor_type.capitalize()} completed! Moving to {next_floor_type.capitalize()}...")
                            
                            # Schedule transition to next floor after a short delay
                            self.animation_controller.schedule_delayed_animation(
                                3.0,  # 3 second delay to show the message
                                lambda: self.room_manager.transition_to_next_floor()
                            )
            
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
                    
                    # Safely update gold with error handling
                    try:
                        if self.player_state_manager is not None:
                            self.player_state_manager.change_gold(gold_reward)
                        else:
                            # Fallback - update gold directly if manager is not available
                            print("Using direct gold update (player_state_manager is None)")
                            self.gold += gold_reward
                    except Exception as e:
                        print(f"Error updating gold during room transition: {e}")
                        # Emergency fallback
                        self.gold += gold_reward
                
                # Start a new room with the remaining card - merchant check happens inside start_new_room
                self.room_manager.start_new_room(self.room.cards[0])
        
        # Check for game over
        self.game_state_controller.check_game_over()

    def draw(self, surface):
        """Draw game elements to the screen."""
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
                        
                    self.ui_renderer.draw_card_type(surface, weapon_card, type_text)
                    
                # Draw weapon name above the card
                if weapon_card.name:
                    self.ui_renderer._draw_inventory_card_info(surface, weapon_card)
            
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
                    self.ui_renderer.draw_card_type(surface, monster, monster.monster_type.upper())
                
                # Draw monster name above the card
                if monster.name:
                    self.ui_renderer._draw_inventory_card_info(surface, monster)
        
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
                    if hasattr(card, 'damage_type') and card.damage_type and card.weapon_type != "arrow":
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                    else:
                        type_text = weapon_type
                elif card.type == "potion":
                    type_text = "HEALING"
                
                # Draw type text below the card
                if type_text:
                    self.ui_renderer.draw_card_type(surface, card, type_text)
                
                # Draw name hover info above the card
                if card.name:
                    self.ui_renderer._draw_inventory_card_info(surface, card)
            
        # Draw room cards LAST always
        self.room.draw(surface)
        
        # Draw any visual effects (destruction/materialize animations)
        self.animation_manager.draw_effects(surface)
        
        # Draw health display
        self.ui_renderer.draw_health_display(surface)
        
        # Draw gold display
        self.ui_renderer.draw_gold_display(surface)
        
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
    
    # Forward key methods to our modular components
    def change_health(self, amount):
        """Forward health change to player state manager."""
        self.player_state_manager.change_health(amount)
    
    def change_gold(self, amount):
        """Forward gold change to player state manager."""
        self.player_state_manager.change_gold(amount)
    
    def set_damage_shield(self, amount):
        """Forward damage shield to player state manager."""
        self.player_state_manager.set_damage_shield(amount)
    
    def position_inventory_cards(self):
        """Forward inventory positioning to inventory manager."""
        self.inventory_manager.position_inventory_cards()
    
    def animate_card_to_discard(self, card):
        """Forward card discard animation to animation controller."""
        self.animation_controller.animate_card_to_discard(card)
    
    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, on_complete=None):
        """Forward card movement animation to animation controller."""
        self._ensure_managers_initialized()  # Ensure we have all managers
        self.animation_controller.animate_card_movement(card, target_pos, duration, easing, on_complete)
        
    def _ensure_managers_initialized(self):
        """Ensure all managers are initialized before use.
        This is a safety mechanism in case they weren't properly set in enter()"""
        try:
            # AnimationManager must be initialized first as other managers depend on it
            if self.animation_manager is None:
                print("Initializing animation_manager in safe mode")
                self.animation_manager = AnimationManager()
                
            # Initialize other managers in dependency order
            if self.card_action_manager is None:
                print("Initializing card_action_manager in safe mode")
                self.card_action_manager = CardActionManager(self)
                
            if self.room_manager is None:
                print("Initializing room_manager in safe mode")
                self.room_manager = RoomManager(self)
                
            if self.animation_controller is None:
                print("Initializing animation_controller in safe mode")
                self.animation_controller = AnimationController(self)
                
            if self.player_state_manager is None:
                print("Initializing player_state_manager in safe mode")
                self.player_state_manager = PlayerStateManager(self)
                
            if self.inventory_manager is None:
                print("Initializing inventory_manager in safe mode")
                self.inventory_manager = InventoryManager(self)
                
            if self.ui_renderer is None:
                print("Initializing ui_renderer in safe mode")
                self.ui_renderer = UIRenderer(self)
                
            if self.game_state_controller is None:
                print("Initializing game_state_controller in safe mode")
                self.game_state_controller = GameStateController(self)
                
            if self.ui_factory is None:
                print("Initializing ui_factory in safe mode")
                self.ui_factory = UIFactory(self)
                
            # Also ensure basic game components exist
            if self.deck is None:
                print("Initializing deck in safe mode")
                self.deck = Deck(self.current_floor or "dungeon")  # Default to dungeon if no floor set
                
            if self.discard_pile is None:
                print("Initializing discard_pile in safe mode")
                self.discard_pile = DiscardPile()
                
            if self.room is None:
                print("Initializing room in safe mode")
                # We know animation_manager exists from above
                self.room = Room(self.animation_manager)
                
            # Verify critical UI components
            if self.run_button is None and self.ui_factory is not None:
                print("Creating run button in safe mode")
                self.ui_factory.create_run_button()
                
            if (self.item_panel is None or self.spell_panel is None) and self.ui_factory is not None:
                print("Creating item/spell panels in safe mode")
                self.ui_factory.create_item_spell_panels()
                
            if not self.item_buttons and self.ui_factory is not None:
                print("Creating item buttons in safe mode")
                self.ui_factory.create_item_buttons()
                
            if not self.spell_buttons and self.ui_factory is not None:
                print("Creating spell buttons in safe mode")
                self.ui_factory.create_spell_buttons()
                
        except Exception as e:
            print(f"ERROR during safe initialization: {e}")
            # Even if there's an error, we continue and let the safety check in update() handle it
    
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
        
    def _add_purchased_cards_to_library(self):
        """Add any cards purchased from merchants to the player's card library."""
        # Check if there are any purchased cards to add
        if hasattr(self.game_manager, 'purchased_cards') and self.game_manager.purchased_cards:
            # Make sure card_library exists
            if not hasattr(self.game_manager, 'card_library'):
                self.game_manager.card_library = []
                
            # Add each purchased card to the library
            for card in self.game_manager.purchased_cards:
                self.game_manager.card_library.append(card)
                
            # Show a message about the cards being added
            card_count = len(self.game_manager.purchased_cards)
            self.game_state_controller.show_message(
                f"Added {card_count} purchased cards to your collection!",
                duration=3.0
            )
            
            # Clear the purchased cards list
            self.game_manager.purchased_cards = []