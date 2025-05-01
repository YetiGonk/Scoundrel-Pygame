""" Treasure state for the Scoundrel game. """
import pygame
import random
import math
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY
from roguelike_constants import TREASURE_INVENTORY
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from ui.hud import HUD
from ui.status_ui import StatusUI
from utils.resource_loader import ResourceLoader
from utils.animation import Animation, EasingFunctions
from utils.treasure_chest import TreasureChest


class TreasureState(GameState):
    """The treasure room screen state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        self.shade = None
        
        # Inventory
        self.cards_for_sale = []
        
        # UI elements
        self.panels = {}
        self.buttons = {}
        self.card_buttons = []
        self.continue_button = None
        
        # Status displays
        self.hud = None
        self.status_ui = None
        
        # Treasure chest
        self.treasure_chest = None
    
    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
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
        
        # For treasure rooms, use treasure floor image
        floor_image = "floors/treasure_floor.png"
            
        # Try to load the treasure floor image, fall back to floor type or original
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            try:
                # Try loading the current floor type image
                self.floor = ResourceLoader.load_image(f"floors/{current_floor_type}_floor.png")
            except:
                # Fallback to the original floor image
                self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        # Load shade
        self.shade = Panel((SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0), colour=DARK_GRAY, alpha=100, border_radius=0)

        # Generate inventory
        self.generate_inventory()
        
        # Create UI elements
        self.create_ui()
        
        # Initialise StatusUI with custom position
        self.status_ui = StatusUI(self.game_manager)
        self.status_ui.update_fonts(self.header_font, self.normal_font)
        # Adjust StatusUI position to be on the left side and not covered by main panel
        self.status_ui.panel_rect = pygame.Rect(
            200, 40,  # Move to left side
            320, 70  # Make it a bit smaller
        )
        
        # Load gold icon
        self.gold_icon = ResourceLoader.load_image("ui/gold.png")
        
        # Create the treasure chest in the bottom left corner
        chest_pos = (120, SCREEN_HEIGHT-70)  # Position is the bottom left of the chest
        self.treasure_chest = TreasureChest(chest_pos, self.floor, scale=9)
        
        # Preserve the playing state's equipped weapon, defeated monsters and remaining card
        playing_state = self.game_manager.states["playing"]
        # Store them in the game_manager to be restored when returning to playing state
        self.game_manager.equipped_weapon = playing_state.equipped_weapon
        self.game_manager.defeated_monsters = playing_state.defeated_monsters.copy()
        
        # Also preserve the last remaining card if present
        if playing_state.room and len(playing_state.room.cards) == 1:
            # Store the remaining card data to be restored when returning to playing state
            last_card = playing_state.room.cards[0]
            self.game_manager.last_card_data = {
                "suit": last_card.suit,
                "value": last_card.value,
                "floor_type": last_card.floor_type
            }
            # Remove the card from the room so it doesn't get discarded
            playing_state.room.cards = []
    
    def generate_inventory(self):
        """Generate the treasure inventory."""
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()
        
        # Generate cards for sale - potions and weapons with higher values
        # Generate 4 cards (2 weapons, 2 potions)
        self.cards_for_sale = self.generate_cards_for_sale(4)
    
    def get_rarity_weights_for_floor(self, floor_index):
        """Get adjusted rarity weights based on floor progress."""
        # Base weights
        weights = {
            "common": 50 - (floor_index * 10),
            "uncommon": 30,
            "rare": 15 + (floor_index * 5),
            "legendary": 5 + (floor_index * 5)
        }
        
        # Ensure no negative weights
        for key in weights:
            weights[key] = max(0, weights[key])
            
        return weights
    
    def create_ui(self):
        """Create the UI elements for the treasure state."""
        # Main panel (larger and to the right side)
        self.panels["main"] = Panel(
            (500, 600),
            (SCREEN_WIDTH - 650, 40),
            colour=DARK_GRAY
        )
        
        # Cards panel (larger to display actual cards)
        self.panels["cards"] = Panel(
            (450, 450),
            (self.panels["main"].rect.left + 25, self.panels["main"].rect.top + 75),
            colour=GRAY
        )
        
        # Continue button
        continue_rect = pygame.Rect(0, 0, 200, 50)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.top = self.panels["main"].rect.bottom - continue_rect.height - 15
        self.continue_button = Button(continue_rect, "Continue", self.body_font)
        
        # Create card objects instead of buttons
        self.create_card_display()
        
    def create_card_display(self):
        """Create actual card objects for display in the treasure room."""
        from components.card import Card
        
        self.card_objects = []
        
        # Calculate positioning for the cards
        panel_center_x = self.panels["cards"].rect.centerx
        panel_center_y = self.panels["cards"].rect.centery
        
        # Width for button labels under each card
        self.unlock_buttons = []
        
        # Calculate number of cards per row (up to 2) and spacing
        cards_per_row = min(2, len(self.cards_for_sale))
        x_spacing = 160  # Horizontal spacing between cards
        y_spacing = 180  # Vertical spacing between rows
        
        # Calculate starting positions
        start_x = panel_center_x - ((cards_per_row - 1) * x_spacing / 2)
        start_y = panel_center_y - (((len(self.cards_for_sale) - 1) // 2) * y_spacing / 2)
        
        for i, card_data in enumerate(self.cards_for_sale):
            # Determine row and column for positioning
            row = i // 2
            col = i % 2
            
            # Create a real card object
            card = Card(card_data['suit'], card_data['value'])
            card.face_up = True  # Always show the card face up
            
            # Calculate position
            x_pos = start_x + (col * x_spacing)
            y_pos = start_y + (row * y_spacing)
            
            # Center the card at the calculated position
            card_x = x_pos - (card.width // 2)
            card_y = y_pos - (card.height // 2)
            
            # Update card position
            card.update_position((card_x, card_y))
            
            # Create "Unlock" button below the card
            button_rect = pygame.Rect(
                card_x + (card.width // 2) - 50,  # Center button under card
                card_y + card.height + 10,        # Position below card with padding
                100,                             # Button width
                30                               # Button height
            )
            
            unlock_button = Button(button_rect, "Unlock", self.normal_font, bg_colour=(60, 150, 60))
            
            # Store both the card and button
            self.card_objects.append({
                "card": card,
                "data": card_data,
                "button": unlock_button
            })
    
    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            # Check button hover states
            self.continue_button.check_hover(event.pos)
            
            # Check unlock buttons hover
            for card_object in self.card_objects:
                card_object["button"].check_hover(event.pos)
                
                # Also check if the card itself is being hovered
                card = card_object["card"]
                card.is_hovered = card.rect.collidepoint(event.pos)
                
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if continue button was clicked
            if self.continue_button.is_clicked(event.pos):
                # Explicitly set the flag to indicate we're coming from treasure
                self.game_manager.coming_from_treasure = True
                
                # Only increment room number if this is a natural treasure room
                # (not one that appears after floor completion or game completion)
                is_natural_treasure = hasattr(self.game_manager, 'is_bonus_treasure') and not self.game_manager.is_bonus_treasure
                
                if is_natural_treasure:
                    # Increment the room counter to advance to the next room after treasure
                    # This ensures we don't stay on the same room number
                    self.game_manager.floor_manager.advance_room()
                
                # Change state to playing
                self.game_manager.change_state("playing")
                return
            
            # Check if a card's unlock button was clicked
            for card_object in self.card_objects:
                if card_object["button"].is_clicked(event.pos):
                    self.acquire_card(card_object["data"], card_object["card"])
                    return
                
            # Check if a card itself was clicked
            for card_object in self.card_objects:
                card = card_object["card"]
                if card.rect.collidepoint(event.pos):
                    self.acquire_card(card_object["data"], card)
                    return
        
    def generate_cards_for_sale(self, count):
        """Generate cards available in the treasure chest.
        
        Args:
            count: Number of cards to generate
            
        Returns:
            List of card data dictionaries with suit, value, and price
        """
        cards = []
        
        # Get current floor index to determine card rarity/value
        floor_index = self.game_manager.floor_manager.current_floor_index
        
        # Always generate at least 4 cards for display (2 weapons, 2 potions)
        actual_count = max(count, 4)
        
        # Generate some weapon cards (diamonds)
        for i in range(actual_count // 2):
            # Higher floor index means access to better cards
            # Values 8-14 (face cards are stronger)
            min_value = min(8 + floor_index, 11)  # Start higher on later floors
            max_value = min(14, min_value + 3)    # Cap at Ace (14)
            value = random.randint(min_value, max_value)
            
            # Create card data
            card_data = {
                "suit": "diamonds",
                "value": value,
                "price": 0,  # Free in treasure room
                "floor_type": self.game_manager.floor_manager.get_current_floor()
            }
            
            # Add card to list
            cards.append(card_data)
        
        # Generate some potion cards (hearts)
        for i in range(actual_count - (actual_count // 2)):
            # Higher floor index means access to better cards
            # Values 8-14 (face cards heal more)
            min_value = min(8 + floor_index, 11)  # Start higher on later floors
            max_value = min(14, min_value + 3)    # Cap at Ace (14)
            value = random.randint(min_value, max_value)
            
            # Create card data
            card_data = {
                "suit": "hearts",
                "value": value,
                "price": 0,  # Free in treasure room
                "floor_type": self.game_manager.floor_manager.get_current_floor()
            }
            
            # Add card to list
            cards.append(card_data)
        
        # Shuffle the cards to mix potions and weapons
        random.shuffle(cards)
        
        return cards
        
    def acquire_card(self, card_data, card_object):
        """Acquire a special card from the treasure chest.
        
        Args:
            card_data: The dictionary containing card properties
            card_object: The Card instance representing the card
        """
        # Play a visual effect for card acquisition
        self.animate_card_acquisition(card_object)
        
        # Add to player's temporary card collection
        # This will be added to their library when they complete the floor
        if not hasattr(self.game_manager, 'purchased_cards'):
            self.game_manager.purchased_cards = []
        
        self.game_manager.purchased_cards.append(card_data)
        
        # Add to player's permanent card library immediately
        if not hasattr(self.game_manager, 'card_library'):
            self.game_manager.card_library = []
            
        # Make sure we don't add duplicates
        if card_data not in self.game_manager.card_library:
            self.game_manager.card_library.append(card_data)
        
        # Remove from available cards
        if card_data in self.cards_for_sale:
            self.cards_for_sale.remove(card_data)
        
        # Show a feedback message
        self.add_message("Card added to your collection!", 2.0)
        
        # Refresh UI
        self.create_card_display()
        
    def animate_card_acquisition(self, card):
        """Play an animation for card acquisition.
        
        Args:
            card: The Card object to animate
        """
        # Add a pulsing glow effect that fades out
        # (You would implement this if you have animation capabilities)
        
        # For now, we'll just change the card color by setting a flag
        card.is_acquired = True
        
    def add_message(self, text, duration=2.0):
        """Display a temporary message on the screen.
        
        Args:
            text: The message text to display
            duration: How long to show the message in seconds
        """
        # Create a message surface with the text
        text_surface = self.body_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        
        # Create a background surface with some padding
        padding = 20
        bg_rect = pygame.Rect(
            text_rect.left - padding//2,
            text_rect.top - padding//2,
            text_rect.width + padding,
            text_rect.height + padding
        )
        
        # Store the message data
        self.message = {
            "text": text_surface,
            "rect": text_rect,
            "bg_rect": bg_rect,
            "alpha": 0,
            "fade_in": True,
            "fade_speed": 500,  # Alpha units per second
            "time_remaining": duration
        }
        
    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""
        # Get player life points from playing_state
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return
            
        # Health display parameters
        health_display_x = 210
        health_display_y = 200
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
        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int(health_bar_width * health_percent)
        
        # Choose colour based on health percentage
        if health_percent > 0.7:
            health_colour = (0, 200, 0)  # Green
        elif health_percent > 0.3:
            health_colour = (255, 165, 0)  # Orange
        else:
            health_colour = (255, 40, 40)  # Red
        
        # Draw health bar
        if health_width > 0:
            health_rect = pygame.Rect(
                health_display_x,
                health_display_y - health_bar_height - 10,
                health_width,
                health_bar_height
            )
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)
        
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
        health_text = self.body_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)
        surface.blit(health_text, health_text_rect)
        
    def draw_gold_display(self, surface):
        """Draw gold display showing current gold amount."""
        # Gold display parameters - placed right of health display
        gold_display_x = 410
        gold_display_y = 145
        
        # Create background panel
        icon_width = self.gold_icon.get_width()
        icon_height = self.gold_icon.get_height()
        text_width = 50  # Estimated width for the gold text
        
        panel_rect = pygame.Rect(
            gold_display_x - 10, 
            gold_display_y - 10,
            icon_width + text_width + 20,
            icon_height + 20
        )
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(panel_surface, DARK_GRAY, pygame.Rect(0, 0, panel_rect.width, panel_rect.height), 2, border_radius=10)
        surface.blit(panel_surface, panel_rect)
        
        # Draw the gold coin image
        surface.blit(self.gold_icon, (gold_display_x, gold_display_y))
        
        # Get icon dimensions
        icon_width = self.gold_icon.get_width()
        icon_height = self.gold_icon.get_height()
        
        # Draw gold amount with gold-coloured text
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
    
    def update(self, delta_time):
        # Update treasure chest animation
        if self.treasure_chest:
            self.treasure_chest.update(delta_time)
            
        # Update card animations
        for card_obj in self.card_objects:
            card = card_obj["card"]
            card.update(delta_time)
            
        # Update message fade animation
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
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw status UI (floor and room info)
        if self.status_ui:
            self.status_ui.draw(surface)
        
        # Draw health display (like in PlayingState)
        self.draw_health_display(surface)
        
        # Draw gold display (like in PlayingState)
        self.draw_gold_display(surface)
        
        # Draw treasure chest
        if self.treasure_chest:
            self.treasure_chest.draw(surface)
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
            
        # Draw treasure title
        floor_type = self.game_manager.floor_manager.get_current_floor() or "unknown"
        title_text = self.header_font.render(f"{floor_type.capitalize()} Treasure", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 20)
        surface.blit(title_text, title_rect)
        
        # Draw section heading
        cards_text = self.body_font.render("Treasures to Unlock", True, WHITE)
        cards_rect = cards_text.get_rect(centerx=self.panels["cards"].rect.centerx, top=self.panels["cards"].rect.top + 10)
        surface.blit(cards_text, cards_rect)
        
        # Draw cards first (so buttons appear on top)
        for card_obj in self.card_objects:
            card = card_obj["card"]
            
            # First draw card shadow
            self.draw_card_shadow(surface, card)
            
            # Then draw the card itself
            card.draw(surface)
            
            # Draw hover text if card is hovered
            if card.is_hovered:
                card.draw_hover_text(surface)
            
            # Draw the unlock button
            card_obj["button"].draw(surface)
        
        # Draw continue button
        self.continue_button.draw(surface)
        
        # Draw any active message with fade effect
        if hasattr(self, 'message') and self.message:
            # Handle fade-in/fade-out message style
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
                
    def draw_card_shadow(self, surface, card):
        """Draw a shadow under a card for visual effect.
        
        Args:
            surface: The surface to draw on
            card: The card object to draw shadow for
        """
        # Calculate total floating offset
        total_float_offset = 0
        if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
            total_float_offset = card.idle_float_offset + card.hover_float_offset
            
        # Calculate shadow properties based on float height
        # As the card floats higher, shadow moves further away and gets more transparent
        shadow_alpha = 40 + int(10 * (total_float_offset / 10))
        shadow_offset = 4 + int(total_float_offset * 0.5)  # Shadow moves more with higher float
        
        # Scale shadow based on height for perspective effect
        shadow_scale = 1.05  # Slight scaling for perspective
        shadow_width = int(card.width * shadow_scale)
        shadow_height = int(card.height * shadow_scale)
        
        # Create shadow surface
        shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, shadow_alpha))
        
        # Calculate shadow position (centered under the card)
        shadow_x = card.rect.centerx - shadow_width / 2 + shadow_offset
        shadow_y = card.rect.centery - shadow_height / 2 + shadow_offset
        
        # Draw the shadow
        surface.blit(shadow_surf, (shadow_x, shadow_y))