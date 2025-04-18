""" Delving Deck State for managing the player's card collection in Scoundrel. """
import pygame
import random
from pygame.locals import *

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, DARK_GRAY, GOLD_COLOR,
    PANEL_BORDER_RADIUS, PANEL_ALPHA, PANEL_BORDER_WIDTH, CARD_WIDTH, CARD_HEIGHT
)
from states.game_state import GameState
from ui.panel import Panel
from ui.button import Button
from components.card import Card
from utils.resource_loader import ResourceLoader

class DelvingDeckState(GameState):
    """State for viewing and managing the player's delving deck."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        # Fonts
        self.title_font = None
        self.header_font = None
        self.body_font = None
        
        # Visual elements
        self.background = None
        self.floor = None
        self.main_panel = None
        self.back_button = None
        
        # Card collections
        self.delving_deck_cards = []  # Cards in current delving deck
        self.card_library = []  # All available cards in the player's collection
        self.card_catalog = []  # Complete catalog of all possible cards
        
        # Rarity colors
        self.rarity_colors = {
            "common": (255, 255, 255),        # White
            "rare": (120, 255, 120),      # Green
            "epic": (120, 120, 255),          # Blue
            "relic": (255, 120, 255)         # Purple
        }
        
        # Interaction tracking
        self.dragging_card = None
        self.drag_offset = (0, 0)
        self.hovered_item = None  # Could be a card or a placeholder
        
        # UI state
        self.show_library = False  # Toggle between delving deck and library views
        self.toggle_button = None
    
    def enter(self):
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 48)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 32)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load a random floor image for visual variety
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        from roguelike_constants import FLOOR_TYPES
        import random
        
        # Select a random floor type for display
        random_floor_type = random.choice(FLOOR_TYPES)
        floor_image = f"floors/{random_floor_type}_floor.png"
        
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        # Create main panel
        panel_width = 1000
        panel_height = 600
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        self.main_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 30),  # Dark stone colour
            alpha=230,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=(120, 100, 80)  # Gold-ish border
        )
        
        # Create buttons with dungeon styling
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        # Position at the bottom of the panel
        buttons_y = panel_y + panel_height - button_height - button_spacing
        
        # Create toggle button to switch between delving deck and library
        # Position to the left of back button
        toggle_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width - button_width - button_spacing) // 2,
            buttons_y,
            button_width,
            button_height
        )
        
        # Set the proper button text based on current view
        toggle_text = "SHOW DELVING DECK" if self.show_library else "SHOW CARD LIBRARY"
        
        self.toggle_button = Button(
            toggle_button_rect,
            toggle_text,
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 60, 80),  # Dark blue
            border_colour=(80, 120, 160)  # Brighter blue border
        )
        
        # Back button (positioned to the right of toggle button)
        back_button_rect = pygame.Rect(
            toggle_button_rect.right + button_spacing,
            buttons_y,
            button_width, 
            button_height
        )
        self.back_button = Button(
            back_button_rect,
            "BACK",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(80, 40, 40),  # Dark red
            border_colour=(150, 70, 70)  # Brighter red border
        )
        
        # Load player's cards from game manager
        self._load_player_cards()
        
        # Position the cards for display
        self._position_cards()
    
    def _load_player_cards(self):
        """Load the player's cards from the game manager"""
        
        # Check if delving deck exists in game manager
        if hasattr(self.game_manager, 'delving_deck') and self.game_manager.delving_deck:
            self.delving_deck_cards = []
            
            # Convert dictionary format to Card objects
            for card_data in self.game_manager.delving_deck:
                new_card = Card(card_data["suit"], card_data["value"])
                new_card.face_up = True
                # Disable split button functionality in this state
                new_card.can_add_to_inventory = False
                new_card.can_show_attack_options = False
                self.delving_deck_cards.append(new_card)
        else:
            # Initialize with default cards for a new player
            self._initialize_default_deck()
        
        # Load the player's card library
        if hasattr(self.game_manager, 'card_library') and self.game_manager.card_library:
            self.card_library = []
            
            # Count duplicates of each card
            card_counts = {}
            for card_data in self.game_manager.card_library:
                card_key = f"{card_data['suit']}_{card_data['value']}"
                if card_key in card_counts:
                    card_counts[card_key] += 1
                else:
                    card_counts[card_key] = 1
            
            # Create unique Card objects and store counts
            unique_cards = {}
            for card_data in self.game_manager.card_library:
                card_key = f"{card_data['suit']}_{card_data['value']}"
                
                # Only add each unique card once
                if card_key not in unique_cards:
                    new_card = Card(card_data["suit"], card_data["value"])
                    new_card.face_up = True
                    # Disable split button functionality in this state
                    new_card.can_add_to_inventory = False
                    new_card.can_show_attack_options = False
                    # Store count of duplicates
                    new_card.count = card_counts[card_key]
                    
                    unique_cards[card_key] = new_card
                    self.card_library.append(new_card)
    
    def _initialize_default_deck(self):
        """Initialize the default starter deck for a new player"""
        self.delving_deck_cards = []
        self.card_library = []
        
        # Add 5 potion cards (hearts) of values 3, 4, 5, 7, 9
        potion_values = [3, 4, 5, 7, 9]
        for value in potion_values:
            # Add to delving deck
            new_card = Card("hearts", value)
            new_card.face_up = True
            # Disable split button functionality in this state
            new_card.can_add_to_inventory = False
            new_card.can_show_attack_options = False
            self.delving_deck_cards.append(new_card)
            
            # Add to card library (create a new card object, don't use the same reference)
            lib_card = Card("hearts", value)
            lib_card.face_up = True
            # Disable split button functionality in this state
            lib_card.can_add_to_inventory = False
            lib_card.can_show_attack_options = False
            self.card_library.append(lib_card)
            
            # Add duplicate cards for certain values (for testing)
            if value == 3 or value == 5:
                # Add 2 more copies of hearts 3 and 5
                for _ in range(2):
                    dup_card = Card("hearts", value)
                    dup_card.face_up = True
                    dup_card.can_add_to_inventory = False
                    dup_card.can_show_attack_options = False
                    self.card_library.append(dup_card)
        
        # Add 5 weapon cards (diamonds) of values 3, 4, 5, 7, 9
        weapon_values = [3, 4, 5, 7, 9]
        for value in weapon_values:
            # Add to delving deck
            new_card = Card("diamonds", value)
            new_card.face_up = True
            # Disable split button functionality in this state
            new_card.can_add_to_inventory = False
            new_card.can_show_attack_options = False
            self.delving_deck_cards.append(new_card)
            
            # Add to card library (create a new card object, don't use the same reference)
            lib_card = Card("diamonds", value)
            lib_card.face_up = True
            # Disable split button functionality in this state
            lib_card.can_add_to_inventory = False
            lib_card.can_show_attack_options = False
            self.card_library.append(lib_card)
            
            # Add duplicate diamond cards for certain values (for testing)
            if value == 4 or value == 7:
                # Add 3 more copies of diamonds 4 and 1 more copy of diamonds 7
                for _ in range(3 if value == 4 else 1):
                    dup_card = Card("diamonds", value)
                    dup_card.face_up = True
                    dup_card.can_add_to_inventory = False
                    dup_card.can_show_attack_options = False
                    self.card_library.append(dup_card)
        
        # Count duplicates and create unique card list with counts
        card_counts = {}
        for card in self.card_library:
            card_key = f"{card.suit}_{card.value}"
            if card_key in card_counts:
                card_counts[card_key] += 1
            else:
                card_counts[card_key] = 1
        
        # Create a new library with unique cards and counts
        unique_library = []
        processed_keys = set()
        
        for card in self.card_library:
            card_key = f"{card.suit}_{card.value}"
            if card_key not in processed_keys:
                # This is the first time we're seeing this card
                processed_keys.add(card_key)
                # Set the count property
                card.count = card_counts[card_key]
                # Add to our new unique library
                unique_library.append(card)
        
        # Replace the library with our deduplicated version
        self.card_library = unique_library
        
        # Save both collections to game manager
        self._save_delving_deck()
        self._save_card_library()
    
    def _position_cards(self):
        """Position the cards for display based on the current view (delving deck or library)"""
        if not self.show_library:
            # Just show the delving deck cards (always exactly 10 cards in 2 rows of 5)
            cards_to_display = self.delving_deck_cards
            
            # Fixed layout for delving deck - 5 cards per row, 2 rows
            card_spacing_x = 30
            card_spacing_y = 40
            cards_per_row = 5
            rows = 2
            
            # Calculate dimensions of the entire grid
            grid_width = (CARD_WIDTH * cards_per_row) + (card_spacing_x * (cards_per_row - 1))
            grid_height = (CARD_HEIGHT * rows) + (card_spacing_y * (rows - 1))
            
            # Center the grid in the panel
            start_x = (SCREEN_WIDTH - grid_width) // 2
            
            # Position the grid with enough space for title and info at top and buttons at bottom
            panel_content_height = self.main_panel.rect.height - 200  # Reserve space for header and buttons
            start_y = self.main_panel.rect.top + 120 + ((panel_content_height - grid_height) // 2)
            
            # Position each card in the grid
            for i, card in enumerate(cards_to_display):
                row = i // cards_per_row
                col = i % cards_per_row
                
                x = start_x + col * (CARD_WIDTH + card_spacing_x)
                y = start_y + row * (CARD_HEIGHT + card_spacing_y)
                
                card.update_position((x, y))
        else:
            # Library view - create and position full card catalog
            self._setup_card_catalog()
    
    def _setup_card_catalog(self):
        """Sets up the full card catalog view with owned and placeholder cards in a 4-column layout"""
        # Clear any existing catalog before rebuilding
        if hasattr(self, 'card_catalog'):
            self.card_catalog = []
        else:
            self.card_catalog = []
            
        # Track which cards the player owns (convert library to a lookup dict)
        owned_cards = {}
        for card in self.card_library:
            key = f"{card.suit}_{card.value}"
            owned_cards[key] = card
            
        # Make cards much smaller for catalog view (40% of normal size)
        self.catalog_card_width = int(CARD_WIDTH * 0.4)
        self.catalog_card_height = int(CARD_HEIGHT * 0.4)
        
        # Grid layout - 4 columns side by side
        card_spacing_x = 8   # Minimal spacing between cards
        card_spacing_y = 12  # Reduced space between rows
        cards_per_row = 3    # Cards per row in each column
        column_spacing = 30  # Spacing between rarity columns
        
        # Calculate total width of all columns
        column_width = (self.catalog_card_width * cards_per_row) + (card_spacing_x * (cards_per_row - 1))
        total_width = (column_width * 4) + (column_spacing * 3)
        
        # Starting position (centered in the panel)
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = self.main_panel.rect.top + 100  # Space for title
        
        # Helper function to add a header for a section
        def add_header(title, rarity, position):
            # Add to catalog so we can render it later
            self.card_catalog.append({
                "type": "header",
                "title": title,
                "rarity": rarity,
                "position": position
            })
            
        # Helper function to add a card to the catalog
        def add_card_slot(suit, value, rarity, position):
            # Check if player owns this card
            key = f"{suit}_{value}"
            owned = key in owned_cards
            
            # If owned, use the actual card from library
            card = owned_cards.get(key, None)
            
            # Add to catalog
            self.card_catalog.append({
                "type": "card",
                "card": card,
                "suit": suit,
                "value": value,
                "owned": owned,
                "rarity": rarity,
                "position": position,
                "small": True  # Flag that this is a catalog card (smaller size)
            })
            
        # Helper to add placeholder
        def add_placeholder(rarity, position):
            self.card_catalog.append({
                "type": "unknown",
                "rarity": rarity,
                "position": position,
                "small": True  # Flag that this is a catalog item (smaller size)
            })
            
        # Helper function to position a column of cards
        def position_column(column_index, rarity, title, card_count, add_func):
            # Calculate column position
            column_x = start_x + (column_width + column_spacing) * column_index
            column_y = start_y
            
            # Add header for this column centered above the cards
            header_x = column_x + column_width // 2
            add_header(title, rarity, (header_x, column_y))
            column_y += 30  # Space after header
            
            # Setup card grid (filling by rows)
            for i in range(card_count):
                row = i // cards_per_row  # Move down after filling a row
                col = i % cards_per_row   # Position within a row
                
                card_x = column_x + col * (self.catalog_card_width + card_spacing_x)
                card_y = column_y + row * (self.catalog_card_height + card_spacing_y)
                
                # Call appropriate add function with position and index
                add_func(card_x, card_y, i)
        
        # 1. COMMON CARDS (Hearts & Diamonds 2-10) - 18 cards total
        def add_common(x, y, i):
            if i < 9:  # Hearts 2-10
                add_card_slot("hearts", i+2, "common", (x, y))
            elif i < 18:  # Diamonds 2-10
                add_card_slot("diamonds", i-7, "common", (x, y))
            # Leave any extra slots empty
                
        position_column(0, "common", "COMMON", 18, add_common)
        
        # 2. RARE CARDS (Hearts & Diamonds J-A) - 18 cards
        def add_rare(x, y, i):
            if i < 4:  # Hearts J-A
                add_card_slot("hearts", i+11, "rare", (x, y))
            elif i < 8:  # Diamonds J-A
                add_card_slot("diamonds", i+7, "rare", (x, y))
            elif i < 18:  # Placeholders for remaining rare slots
                add_placeholder("rare", (x, y))
                
        position_column(1, "rare", "RARE", 18, add_rare)
        
        # 3. EPIC CARDS (Placeholders) - 18 cards
        position_column(2, "epic", "EPIC", 18, 
            lambda x, y, i: add_placeholder("epic", (x, y))
        )
            
        # 4. RELIC CARDS (Placeholders) - 12 cards
        position_column(3, "relic", "RELIC", 12, 
            lambda x, y, i: add_placeholder("relic", (x, y))
        )
        
        # After building the catalog, update all position for owned cards to match catalog positions
        for catalog_item in self.card_catalog:
            if catalog_item.get("type") == "card" and catalog_item.get("owned") and catalog_item.get("card"):
                # Update card's position to match catalog position
                catalog_item["card"].update_position(catalog_item["position"])
                # Set a flag on the card to indicate it's shown in small size
                catalog_item["card"].catalog_display = True
    
    def _save_delving_deck(self):
        """Save the current delving deck to the game manager"""
        # Convert Card objects to dictionary format for storage
        delving_deck_data = []
        for card in self.delving_deck_cards:
            delving_deck_data.append({
                "suit": card.suit,
                "value": card.value
            })
        
        # Save to game manager
        self.game_manager.delving_deck = delving_deck_data
    
    def _save_card_library(self):
        """Save the card library to the game manager"""
        # Convert Card objects to dictionary format for storage
        library_data = []
        
        for card in self.card_library:
            # If card has a count property, duplicate it in the saved data
            count = getattr(card, 'count', 1)
            
            # Add multiple copies of the card based on the count
            for _ in range(count):
                library_data.append({
                    "suit": card.suit,
                    "value": card.value
                })
        
        # Save to game manager
        self.game_manager.card_library = library_data
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if back button was clicked
            if self.back_button.is_clicked(mouse_pos):
                self.game_manager.change_state("title")
                return
            
            # Check if toggle button was clicked
            if self.toggle_button.is_clicked(mouse_pos):
                self.show_library = not self.show_library
                
                # Update button text based on which view we're switching to
                if self.show_library:
                    # We are now in library view, so button should show option to go back to delving deck
                    self.toggle_button.update_text("SHOW DELVING DECK")
                else:
                    # We are now in delving deck view, so button should show option to go to library
                    self.toggle_button.update_text("SHOW CARD LIBRARY")
                
                # Reposition cards for the new view
                self._position_cards()
                return
            
            # Handle click events based on current view
            if not self.show_library:
                # Delving deck view - check if a card was clicked
                for card in self.delving_deck_cards:
                    if card.rect.collidepoint(mouse_pos):
                        self.dragging_card = card
                        self.drag_offset = (
                            card.rect.x - mouse_pos[0],
                            card.rect.y - mouse_pos[1]
                        )
                        break
            else:
                # Library view - no dragging, but we check for hovering
                # This is handled in MOUSEMOTION event
                pass
        
        elif event.type == MOUSEBUTTONUP and event.button == 1:  # Left button release
            # Stop dragging any card
            self.dragging_card = None
        
        elif event.type == MOUSEMOTION:
            # Move card being dragged
            if self.dragging_card:
                self.dragging_card.update_position((
                    mouse_pos[0] + self.drag_offset[0],
                    mouse_pos[1] + self.drag_offset[1]
                ))
            
            # Update button hover states
            self.back_button.check_hover(mouse_pos)
            self.toggle_button.check_hover(mouse_pos)
            
            # Update hover states based on current view
            if not self.show_library:
                # Delving deck view
                self.hovered_item = None
                for card in self.delving_deck_cards:
                    # Only check the rectangle collision, don't use card's hover check method
                    # which would trigger split button visuals
                    card.is_hovered = card.rect.collidepoint(mouse_pos)
                    
                    # Also disable hover selection property which controls the split button display
                    card.hover_selection = None
                    
                    if card.is_hovered:
                        # Create a more complete hover item that includes all needed properties
                        self.hovered_item = {
                            "type": "card", 
                            "card": card,
                            "suit": card.suit,
                            "value": card.value,
                            "owned": True,
                            "position": card.rect.topleft,
                            "rarity": "common" if card.value < 11 else "rare"
                        }
            else:
                # Library view - check for hovering over catalog items
                self.hovered_item = None
                for item in self.card_catalog:
                    # Skip headers
                    if item.get("type") == "header":
                        continue
                    
                    # Calculate item rectangle - use catalog card size if small flag is set
                    position = item.get("position")
                    if item.get("small", False):
                        item_rect = pygame.Rect(
                            position[0], position[1],
                            self.catalog_card_width, self.catalog_card_height
                        )
                    else:
                        item_rect = pygame.Rect(
                            position[0], position[1],
                            CARD_WIDTH, CARD_HEIGHT
                        )
                    
                    # Check if mouse is hovering over this item
                    if item_rect.collidepoint(mouse_pos):
                        # If it's a card and owned, update hover state
                        if item.get("type") == "card" and item.get("owned") and item.get("card"):
                            # Update card's hover state
                            item["card"].is_hovered = True
                            # Disable hover selection property
                            item["card"].hover_selection = None
                            # Set as current hovered item
                            self.hovered_item = item
                        elif item.get("type") == "card" and not item.get("owned"):
                            # Hovering over unowned card slot
                            self.hovered_item = item
                        elif item.get("type") == "unknown":
                            # Hovering over placeholder
                            self.hovered_item = item
                    elif item.get("type") == "card" and item.get("owned") and item.get("card"):
                        # Reset hover state for non-hovered cards
                        item["card"].is_hovered = False
    
    def update(self, delta_time):
        # Update card animations
        if not self.show_library:
            # Delving deck view - update all cards with full animations
            for card in self.delving_deck_cards:
                card.update(delta_time)
                
                if card.is_flipping:
                    card.update_flip(delta_time)
        else:
            # Library view - only update hover effects for owned cards in the catalog
            # but disable idle floating animation
            for item in self.card_catalog:
                if item.get("type") == "card" and item.get("owned") and item.get("card"):
                    # Store original idle settings
                    original_idle_float_amount = item["card"].idle_float_amount
                    original_idle_float_speed = item["card"].idle_float_speed
                    
                    # Disable idle floating by setting amount to 0
                    item["card"].idle_float_amount = 0
                    item["card"].idle_float_speed = 0
                    
                    # Update only hover effects, not idle animations
                    item["card"].update(delta_time)
                    
                    # Restore original idle settings after update
                    item["card"].idle_float_amount = original_idle_float_amount
                    item["card"].idle_float_speed = original_idle_float_speed
                    
                    if item["card"].is_flipping:
                        item["card"].update_flip(delta_time)
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw floor
        floor_x = (SCREEN_WIDTH - self.floor.get_width()) // 2
        floor_y = (SCREEN_HEIGHT - self.floor.get_height()) // 2
        surface.blit(self.floor, (floor_x, floor_y))
        
        # Draw main panel
        self.main_panel.draw(surface)
        
        # Draw title based on current view
        title_text = "DELVING DECK" if not self.show_library else "CARD LIBRARY"
        title_render = self.title_font.render(title_text, True, WHITE)
        title_rect = title_render.get_rect(centerx=SCREEN_WIDTH//2, top=self.main_panel.rect.top + 20)
        surface.blit(title_render, title_rect)
        
        # Draw subtitle with info about the current view
        if not self.show_library:
            subtitle = f"Your current deck ({len(self.delving_deck_cards)}/10 cards)"
            subtitle_render = self.header_font.render(subtitle, True, WHITE)
            subtitle_rect = subtitle_render.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 10)
            surface.blit(subtitle_render, subtitle_rect)
        else:
            # For library view, place the card count in top right corner
            # Calculate total collectible cards by counting all types except headers and unknowns
            total_collectible = len([i for i in self.card_catalog if i.get("type") == "card" or i.get("type") == "unknown"])
            collection_text = f"{len(self.card_library)}/{total_collectible}"
            collection_render = self.body_font.render(f"Cards: {collection_text}", True, WHITE)
            collection_rect = collection_render.get_rect(topright=(self.main_panel.rect.right - 20, self.main_panel.rect.top + 20))
            surface.blit(collection_render, collection_rect)
        
        # Draw cards based on current view
        if not self.show_library:
            # Draw delving deck cards
            # Draw non-hovered cards first
            for card in self.delving_deck_cards:
                if not card.is_hovered and card != self.dragging_card:
                    card.draw(surface)
            
            # Then draw hovered card to ensure it appears on top
            if self.hovered_item and self.hovered_item.get("type") == "card" and self.hovered_item.get("card") != self.dragging_card:
                self.hovered_item["card"].draw(surface)
            
            # Draw dragged card last (on top of everything)
            if self.dragging_card:
                self.dragging_card.draw(surface)
        else:
            # Draw library catalog items
            for item in self.card_catalog:
                if item["type"] == "header":
                    # Draw section header
                    header_text = self.body_font.render(item["title"], True, self.rarity_colors[item["rarity"]])
                    header_rect = header_text.get_rect(center=item["position"])
                    surface.blit(header_text, header_rect)
                elif item["type"] == "card":
                    position = item["position"]
                    
                    # Draw card border based on rarity - use catalog card size with thinner borders
                    border_rect = pygame.Rect(
                        position[0] - 1, position[1] - 1,
                        self.catalog_card_width + 2, self.catalog_card_height + 2
                    )
                    pygame.draw.rect(surface, self.rarity_colors[item["rarity"]], border_rect, 1, border_radius=4)
                    
                    if item["owned"]:
                        # If the card is owned, we'll draw the card object itself later
                        # to handle hover effects properly
                        if item.get("card"):
                            # Need to draw the card at the smaller catalog size
                            # First check if card isn't being hovered or dragged (those are drawn separately)
                            if not item.get("card").is_hovered and item.get("card") != self.dragging_card:
                                # Draw the card at the catalog size - scale it down from the original
                                # Store original properties
                                original_texture = item["card"].texture
                                original_rect = item["card"].rect
                                
                                # Calculate scale factor
                                scale_factor = self.catalog_card_width / CARD_WIDTH
                                
                                # Create scaled version of the texture
                                scaled_texture = pygame.transform.scale(
                                    original_texture, 
                                    (self.catalog_card_width, self.catalog_card_height)
                                )
                                
                                # Temporarily update card's rect and texture for drawing at smaller size
                                item["card"].rect = pygame.Rect(
                                    position[0], 
                                    position[1], 
                                    self.catalog_card_width, 
                                    self.catalog_card_height
                                )
                                item["card"].texture = scaled_texture
                                item["card"].width = self.catalog_card_width
                                item["card"].height = self.catalog_card_height
                                
                                # Disable idle animation in catalog view
                                original_idle_float_amount = item["card"].idle_float_amount
                                original_idle_offset = item["card"].idle_float_offset
                                item["card"].idle_float_amount = 0
                                item["card"].idle_float_offset = 0
                                
                                # Draw the card at its catalog size
                                item["card"].draw(surface)
                                
                                # Draw count overlay if card count > 1
                                if hasattr(item["card"], 'count') and item["card"].count > 1:
                                    # Position in bottom left corner of card
                                    count_x = position[0] + 10
                                    count_y = position[1] + self.catalog_card_height - 9
                                    
                                    # Draw a small curved box background for count
                                    count_width = 22  # Width of box
                                    count_height = 18  # Height of box
                                    
                                    # Create rounded rect for count badge
                                    count_rect = pygame.Rect(
                                        count_x - count_width//2, 
                                        count_y - count_height//2,
                                        count_width, 
                                        count_height
                                    )
                                    
                                    # Draw grey background with rounded corners
                                    pygame.draw.rect(
                                        surface, 
                                        (60, 60, 60),  # Dark grey background
                                        count_rect,
                                        0,  # Filled
                                        5  # Border radius
                                    )
                                    pygame.draw.rect(
                                        surface, 
                                        (100, 100, 100),  # Light grey border
                                        count_rect,
                                        1,  # Border width
                                        5  # Border radius
                                    )
                                    
                                    # Draw count number
                                    small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)
                                    count_text = small_font.render(f"{item['card'].count}", True, WHITE)
                                    count_text_rect = count_text.get_rect(center=(count_x, count_y))
                                    surface.blit(count_text, count_text_rect)
                                
                                # Restore idle animation settings
                                item["card"].idle_float_amount = original_idle_float_amount
                                item["card"].idle_float_offset = original_idle_offset
                                
                                # Restore original properties
                                item["card"].texture = original_texture
                                item["card"].rect = original_rect
                                item["card"].width = CARD_WIDTH
                                item["card"].height = CARD_HEIGHT
                    else:
                        # Draw placeholder for unowned card - with catalog size
                        card_rect = pygame.Rect(
                            position[0], position[1],
                            self.catalog_card_width, self.catalog_card_height
                        )
                        
                        # Draw greyed out card back
                        placeholder_surface = pygame.Surface((self.catalog_card_width, self.catalog_card_height), pygame.SRCALPHA)
                        placeholder_surface.fill((70, 70, 70, 220))  # Grey semi-transparent
                        
                        # Add some subtle card marking
                        suit = item["suit"]
                        suit_symbol = "♥" if suit == "hearts" else "♦" if suit == "diamonds" else "?"
                        
                        # Draw suit in center of card - smaller font for catalog view
                        small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
                        suit_text = small_font.render(suit_symbol, True, (120, 120, 120))
                        suit_rect = suit_text.get_rect(center=(self.catalog_card_width//2, self.catalog_card_height//2))
                        placeholder_surface.blit(suit_text, suit_rect)
                        
                        # Draw the placeholder
                        surface.blit(placeholder_surface, card_rect)
                elif item["type"] == "unknown":
                    position = item["position"]
                    
                    # Draw card border based on rarity - use catalog card size with thinner borders
                    border_rect = pygame.Rect(
                        position[0] - 1, position[1] - 1,
                        self.catalog_card_width + 2, self.catalog_card_height + 2
                    )
                    pygame.draw.rect(surface, self.rarity_colors[item["rarity"]], border_rect, 1, border_radius=4)
                    
                    # Draw placeholder for unknown card - with catalog size
                    card_rect = pygame.Rect(
                        position[0], position[1],
                        self.catalog_card_width, self.catalog_card_height
                    )
                    
                    # Draw question mark placeholder
                    placeholder_surface = pygame.Surface((self.catalog_card_width, self.catalog_card_height), pygame.SRCALPHA)
                    placeholder_surface.fill((50, 50, 50, 200))  # Dark grey 
                    
                    # Draw ? in center of card - smaller font for catalog view
                    small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
                    question_text = small_font.render("?", True, (150, 150, 150))
                    question_rect = question_text.get_rect(center=(self.catalog_card_width//2, self.catalog_card_height//2))
                    placeholder_surface.blit(question_text, question_rect)
                    
                    # Draw the placeholder
                    surface.blit(placeholder_surface, card_rect)
            
            # Draw hovered card on top if it's owned
            if self.hovered_item and self.hovered_item.get("type") == "card" and self.hovered_item.get("owned") and self.hovered_item.get("card"):
                # Draw the card at catalog size with subtle hover effect
                position = self.hovered_item.get("position")
                
                # Draw a subtle highlight border - thinner for smaller cards
                border_rect = pygame.Rect(
                    position[0] - 1, position[1] - 1,
                    self.catalog_card_width + 2, self.catalog_card_height + 2
                )
                # Use a slightly dimmer version of the rarity color for a more subtle effect
                rarity_color = self.rarity_colors[self.hovered_item["rarity"]]
                hover_color = (int(rarity_color[0] * 0.8), int(rarity_color[1] * 0.8), int(rarity_color[2] * 0.8))
                pygame.draw.rect(surface, hover_color, border_rect, 1, border_radius=4)
                
                # Store original properties
                original_texture = self.hovered_item["card"].texture
                original_rect = self.hovered_item["card"].rect
                
                # Calculate scale factor
                scale_factor = self.catalog_card_width / CARD_WIDTH
                
                # Create scaled version of the texture
                scaled_texture = pygame.transform.scale(
                    original_texture, 
                    (self.catalog_card_width, self.catalog_card_height)
                )
                
                # Temporarily update card's properties for drawing at smaller size
                self.hovered_item["card"].rect = pygame.Rect(
                    position[0], 
                    position[1], 
                    self.catalog_card_width, 
                    self.catalog_card_height
                )
                self.hovered_item["card"].texture = scaled_texture
                self.hovered_item["card"].width = self.catalog_card_width
                self.hovered_item["card"].height = self.catalog_card_height
                
                # Mark this as a hovered card for proper drawing
                self.hovered_item["card"].is_hovered = True
                
                # Disable idle animation in catalog view
                original_idle_float_amount = self.hovered_item["card"].idle_float_amount
                original_idle_offset = self.hovered_item["card"].idle_float_offset
                self.hovered_item["card"].idle_float_amount = 0
                self.hovered_item["card"].idle_float_offset = 0
                
                # For hovered cards in library view, scale them up significantly (80% of original)
                # to make them clearly visible
                enlarged_width = int(CARD_WIDTH * 0.8)
                enlarged_height = int(CARD_HEIGHT * 0.8)
                
                # Create enlarged version of the texture
                enlarged_texture = pygame.transform.scale(
                    original_texture, 
                    (enlarged_width, enlarged_height)
                )
                
                # Calculate centered position for enlarged card
                enlarged_x = position[0] - (enlarged_width - self.catalog_card_width) // 2
                enlarged_y = position[1] - (enlarged_height - self.catalog_card_height) // 2
                
                # Update card's rect and texture for drawing at enlarged size
                self.hovered_item["card"].rect = pygame.Rect(
                    enlarged_x, 
                    enlarged_y, 
                    enlarged_width, 
                    enlarged_height
                )
                self.hovered_item["card"].texture = enlarged_texture
                self.hovered_item["card"].width = enlarged_width
                self.hovered_item["card"].height = enlarged_height
                
                # Draw the card at its enlarged size
                self.hovered_item["card"].draw(surface)
                
                # Draw count overlay if card count > 1
                if hasattr(self.hovered_item["card"], 'count') and self.hovered_item["card"].count > 1:
                    # Position in bottom left corner of card
                    count_x = enlarged_x + 10
                    count_y = enlarged_y + enlarged_height - 22
                    
                    # Draw a larger curved box background for count (proportional to enlarged card)
                    count_width = 30  # Width of box
                    count_height = 24  # Height of box
                    
                    # Create rounded rect for count badge
                    count_rect = pygame.Rect(
                        count_x - count_width//2, 
                        count_y - count_height//2,
                        count_width, 
                        count_height
                    )
                    
                    # Draw grey background with rounded corners
                    pygame.draw.rect(
                        surface, 
                        (60, 60, 60),  # Dark grey background
                        count_rect,
                        0,  # Filled
                        8  # Border radius
                    )
                    pygame.draw.rect(
                        surface, 
                        (100, 100, 100),  # Light grey border
                        count_rect,
                        2,  # Border width
                        8  # Border radius
                    )
                    
                    # Draw count number
                    small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
                    count_text = small_font.render(f"{self.hovered_item['card'].count}", True, WHITE)
                    count_text_rect = count_text.get_rect(center=(count_x, count_y))
                    surface.blit(count_text, count_text_rect)
                
                # Restore idle animation settings
                self.hovered_item["card"].idle_float_amount = original_idle_float_amount
                self.hovered_item["card"].idle_float_offset = original_idle_offset
                
                # Restore original properties
                self.hovered_item["card"].texture = original_texture
                self.hovered_item["card"].rect = original_rect
                self.hovered_item["card"].width = CARD_WIDTH
                self.hovered_item["card"].height = CARD_HEIGHT
        
        # Draw card info for hovered item
        if self.hovered_item:
            if (self.hovered_item.get("type") == "card" and self.hovered_item.get("owned") and 
                self.hovered_item.get("card")):
                # For owned cards, show detailed info
                self._draw_card_info(surface, self.hovered_item["card"])
            elif ((self.hovered_item.get("type") == "card" and not self.hovered_item.get("owned")) or
                  self.hovered_item.get("type") == "unknown"):
                # For unowned cards or placeholders, show mystery info
                self._draw_mystery_info(surface, self.hovered_item)
        
        # Draw buttons
        self.back_button.draw(surface)
        self.toggle_button.draw(surface)
    
    def _draw_card_info(self, surface, card):
        """Draw detailed card info for an owned card"""
        # Determine if we need to display count
        has_count = hasattr(card, 'count') and card.count > 1
        
        # Calculate text heights
        header_height = self.header_font.get_height()
        body_height = self.body_font.get_height()
        
        # Calculate info box dimensions
        info_width = 300
        
        # Calculate height based on number of text lines plus padding
        # Top padding (10px) + header + (spacing + body) * N + bottom padding (10px)
        if has_count:
            # 4 lines: name, type, damage/heal, count
            info_height = 10 + header_height + 5 + (body_height + 5) * 3 + 5
        else:
            # 3 lines: name, type, damage/heal
            info_height = 10 + header_height + 5 + (body_height + 5) * 2 + 5
        
        # Get the card position and dimensions
        card_center_x = card.rect.centerx
        card_top = card.rect.top
        card_bottom = card.rect.bottom
        card_left = card.rect.left
        card_right = card.rect.right
        
        # Check if this is a catalog card (smaller size)
        is_catalog_card = hasattr(card, 'is_catalog_card') and card.is_catalog_card
        
        # Always use a consistent and simple positioning strategy for all card views
        # Start with the right side position (most readable position)
        info_x = card_right + 10
        info_y = card_top
        
        # If it would go off-screen to the right, position left of card
        if info_x + info_width > self.main_panel.rect.right - 10:
            info_x = card_left - info_width - 10
            
        # If it's still off-screen (very wide card or panel edge), 
        # position below or above the card instead
        if info_x < self.main_panel.rect.left + 10:
            # Position below or above based on available space
            if card_top + card.rect.height + info_height + 10 <= self.main_panel.rect.bottom - 10:
                # Position below
                info_x = card_center_x - (info_width // 2)
                info_y = card_bottom + 10
            else:
                # Position above
                info_x = card_center_x - (info_width // 2)
                info_y = card_top - info_height - 10
            
        # Final check - ensure it stays within vertical bounds
        if info_y + info_height > self.main_panel.rect.bottom - 10:
            info_y = self.main_panel.rect.bottom - info_height - 10
        if info_y < self.main_panel.rect.top + 10:
            info_y = self.main_panel.rect.top + 10
        
        # Final safety check - ensure panel stays within bounds
        info_x = max(self.main_panel.rect.left + 10, min(info_x, self.main_panel.rect.right - info_width - 10))
        info_y = max(self.main_panel.rect.top + 10, min(info_y, self.main_panel.rect.bottom - info_height - 10))
        
        # Create and draw the info panel
        info_panel = Panel(
            (info_width, info_height),
            (info_x, info_y),
            colour=(60, 50, 40),
            alpha=220,
            border_radius=8,
            dungeon_style=True
        )
        info_panel.draw(surface)
        
        # Start vertical position with top padding
        current_y = info_y + 10  # 10px top padding
        
        if card.type == "weapon" or card.suit == "diamonds":  # Check by both type and suit
            # Card name - use card name property if available
            card_name = card.name if hasattr(card, 'name') and card.name else f"Weapon {card.value}"
            name_text = self.header_font.render(card_name, True, WHITE)
            name_rect = name_text.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(name_text, name_rect)
            
            # Update current_y for next line (add header height + 5px spacing)
            current_y = name_rect.bottom + 5
            
            # Determine weapon type based on value if not already set
            weapon_type = None
            if hasattr(card, 'weapon_type') and card.weapon_type:
                weapon_type = card.weapon_type
            else:
                # Fallback to determine type based on card value
                from roguelike_constants import WEAPON_MAPPINGS
                if card.value in [2, 3]:
                    weapon_type = "arrow"
                elif card.value in [11, 13]:  # Longbow and Crossbow are ranged
                    weapon_type = "ranged"
                else:
                    weapon_type = "melee"
            
            # Weapon type text
            type_text = f"Weapon - "
            if weapon_type == "ranged":
                type_text += "Ranged"
            elif weapon_type == "melee":
                type_text += "Melee"
            elif weapon_type == "arrow":
                type_text += "Arrow (Ammo)"
                    
            type_render = self.body_font.render(type_text, True, GOLD_COLOR)
            type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(type_render, type_rect)
            
            # Update current_y for next line
            current_y = type_rect.bottom + 5
            
            # Damage text
            damage_text = f"Damage: {card.value}"
            damage_render = self.body_font.render(damage_text, True, WHITE)
            damage_rect = damage_render.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(damage_render, damage_rect)
            
            # Update current_y for next line
            current_y = damage_rect.bottom + 5
            
            # Add count line if multiple copies exist
            if has_count:
                count_text = f"Owned: {card.count}"
                count_render = self.body_font.render(count_text, True, GOLD_COLOR)
                count_rect = count_render.get_rect(centerx=info_x + info_width//2, top=current_y)
                surface.blit(count_render, count_rect)
            
        elif card.type == "potion" or card.suit == "hearts":  # Check by both type and suit
            # Card name - use card name property if available
            card_name = card.name if hasattr(card, 'name') and card.name else f"Potion {card.value}"
            name_text = self.header_font.render(card_name, True, WHITE)
            name_rect = name_text.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(name_text, name_rect)
            
            # Update current_y for next line (add header height + 5px spacing)
            current_y = name_rect.bottom + 5
            
            # Potion type text
            type_text = "Potion - Healing"
            type_render = self.body_font.render(type_text, True, GOLD_COLOR)
            type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(type_render, type_rect)
            
            # Update current_y for next line
            current_y = type_rect.bottom + 5
            
            # Healing effect text
            heal_text = f"Restores {card.value} health"
            heal_render = self.body_font.render(heal_text, True, WHITE)
            heal_rect = heal_render.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(heal_render, heal_rect)
            
            # Update current_y for next line
            current_y = heal_rect.bottom + 5
            
            # Add count line if multiple copies exist
            if has_count:
                count_text = f"Owned: {card.count}"
                count_render = self.body_font.render(count_text, True, GOLD_COLOR)
                count_rect = count_render.get_rect(centerx=info_x + info_width//2, top=current_y)
                surface.blit(count_render, count_rect)
    
    def _draw_mystery_info(self, surface, item):
        """Draw mystery info for an unowned card or placeholder"""
        # Skip if no item
        if not item:
            return
            
        # Check for required properties
        if "position" not in item:
            return
            
        # Determine if we have rarity info
        has_rarity = "rarity" in item
        
        # Calculate text heights
        header_height = self.header_font.get_height()
        body_height = self.body_font.get_height()
        
        # Calculate info box dimensions
        info_width = 200  # Slightly smaller info panel
        
        # Calculate height based on number of text lines plus padding
        # Top padding (10px) + header + (spacing + body) * N + bottom padding (10px)
        if has_rarity:
            # 3 lines: name, type, rarity
            info_height = 10 + header_height + 5 + (body_height + 5) * 2 + 5
        else:
            # 2 lines: name, type
            info_height = 10 + header_height + 5 + (body_height + 5) + 5
        
        # Get the item position - adjust for catalog card size if needed
        position = item["position"]
        
        # Set up positioning based on card size
        if item.get("small", False):
            item_width = self.catalog_card_width
            item_height = self.catalog_card_height
            item_center_x = position[0] + item_width // 2
            item_top = position[1]
            item_bottom = position[1] + item_height
        else:
            item_width = CARD_WIDTH
            item_height = CARD_HEIGHT
            item_center_x = position[0] + item_width // 2
            item_top = position[1]
            item_bottom = position[1] + item_height
            
        # Use consistent positioning strategy for all views (same as _draw_card_info)
        # Start with the right side position (most readable position)
        info_x = position[0] + item_width + 10
        info_y = position[1]
        
        # If it would go off-screen to the right, position left of card
        if info_x + info_width > self.main_panel.rect.right - 10:
            info_x = position[0] - info_width - 10
            
        # If it's still off-screen (very wide card or panel edge), 
        # position below or above the card instead
        if info_x < self.main_panel.rect.left + 10:
            # Position below or above based on available space
            if item_top + item_height + info_height + 10 <= self.main_panel.rect.bottom - 10:
                # Position below
                info_x = item_center_x - (info_width // 2)
                info_y = item_bottom + 10
            else:
                # Position above
                info_x = item_center_x - (info_width // 2)
                info_y = item_top - info_height - 10
            
        # Final check - ensure it stays within vertical bounds
        if info_y + info_height > self.main_panel.rect.bottom - 10:
            info_y = self.main_panel.rect.bottom - info_height - 10
        if info_y < self.main_panel.rect.top + 10:
            info_y = self.main_panel.rect.top + 10
        
        # Final safety check - ensure panel stays within bounds
        info_x = max(self.main_panel.rect.left + 10, min(info_x, self.main_panel.rect.right - info_width - 10))
        info_y = max(self.main_panel.rect.top + 10, min(info_y, self.main_panel.rect.bottom - info_height - 10))
        
        # Create and draw the info panel
        info_panel = Panel(
            (info_width, info_height),
            (info_x, info_y),
            colour=(40, 40, 45),
            alpha=200,
            border_radius=8,
            dungeon_style=True
        )
        info_panel.draw(surface)
        
        # Determine the item type for all cards and placeholders
        type_hint = "Unknown"
        
        # For actual card slots, determine type based on suit and value
        if item.get("type") == "card":
            if item.get("suit") == "hearts":
                type_hint = "Potion"
            elif item.get("suit") == "diamonds":
                # Special case for diamonds 2-3, which are arrows
                if item.get("value") == 2 or item.get("value") == 3:
                    type_hint = "Arrow"
                else:
                    type_hint = "Weapon"
            elif item.get("suit") == "spades" or item.get("suit") == "clubs":
                type_hint = "Monster"
        
        # For epic and relic placeholders, make a reasonable guess based on section
        elif item.get("type") == "placeholder" or item.get("type") == "unknown":
            # If it's in the epic or relic section, show a more specific type hint
            rarity = item.get("rarity", "")
            if rarity == "epic":
                # Distribute types evenly for epic cards
                # Use the card's position to deterministically assign a type
                # This ensures the same card always shows the same type
                pos = item.get("position", (0, 0))
                idx = (pos[0] * 31 + pos[1] * 17) % 4  # Simple hash for consistency
                if idx == 0:
                    type_hint = "Weapon"
                elif idx == 1:
                    type_hint = "Potion"
                elif idx == 2:
                    type_hint = "Spell"
                else:
                    type_hint = "Artifact"
            elif rarity == "relic":
                # For relic cards, they're special items
                type_hint = "Artifact"
        
        # Start vertical position with top padding
        current_y = info_y + 10  # 10px top padding
        
        # Draw mystery card name (???)
        mystery_text = self.header_font.render("???", True, WHITE)
        mystery_rect = mystery_text.get_rect(centerx=info_x + info_width//2, top=current_y)
        surface.blit(mystery_text, mystery_rect)
        
        # Update current_y for next line
        current_y = mystery_rect.bottom + 5
        
        # Show type info for ALL unknown cards
        type_render = self.body_font.render(f"Type: {type_hint}", True, (180, 180, 180))
        type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=current_y)
        surface.blit(type_render, type_rect)
        
        # Update current_y for next line
        current_y = type_rect.bottom + 5
        
        # Show rarity text if available
        if has_rarity:
            rarity_render = self.body_font.render(f"{item['rarity'].capitalize()}", True, self.rarity_colors[item["rarity"]])
            rarity_rect = rarity_render.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(rarity_render, rarity_rect)
