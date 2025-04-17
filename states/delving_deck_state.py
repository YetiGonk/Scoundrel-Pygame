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
            "uncommon": (120, 255, 120),      # Green
            "rare": (120, 120, 255),          # Blue
            "exotic": (255, 120, 255)         # Purple
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
        self.toggle_button = Button(
            toggle_button_rect,
            "SHOW CARD LIBRARY",
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
            
            # Convert dictionary format to Card objects
            for card_data in self.game_manager.card_library:
                new_card = Card(card_data["suit"], card_data["value"])
                new_card.face_up = True
                # Disable split button functionality in this state
                new_card.can_add_to_inventory = False
                new_card.can_show_attack_options = False
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
        """Sets up the full card catalog view with owned and placeholder cards"""
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
            
        # Define a smaller card size for catalog view (70% of normal size)
        self.catalog_card_width = int(CARD_WIDTH * 0.7)
        self.catalog_card_height = int(CARD_HEIGHT * 0.7)
        
        # Card grid layout - more compact
        card_spacing_x = 12  # Reduced spacing
        card_spacing_y = 40  # Reduced space between rows but still room for headers
        cards_per_row = 12   # More cards per row
        
        # Calculate start position (centered in the panel)
        total_width = (self.catalog_card_width * cards_per_row) + (card_spacing_x * (cards_per_row - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = self.main_panel.rect.top + 100  # Less space for title
        
        # Position marker
        current_x = start_x
        current_y = start_y
        row_card_count = 0
        
        # Helper function to add a header for a section
        def add_header(title, rarity, y_pos):
            # Add to catalog so we can render it later
            self.card_catalog.append({
                "type": "header",
                "title": title,
                "rarity": rarity,
                "position": (SCREEN_WIDTH // 2, y_pos - 20)  # Less space above header
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
        
        # 1. COMMON CARDS (Hearts & Diamonds 2-10)
        
        # Add common cards header
        add_header("COMMON CARDS", "common", current_y)
        current_y += 15  # Adjust for header space
        
        # Add hearts 2-10
        for value in range(2, 11):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            add_card_slot("hearts", value, "common", position)
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
            
        # Add diamonds 2-10, but skip values 2 and 3 which are arrows
        for value in range(4, 11):  # Start at 4 to avoid duplicate arrow cards
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            add_card_slot("diamonds", value, "common", position)
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
        
        # 2. UNCOMMON CARDS (Arrows + Hearts & Diamonds J-A)
        
        # Start new row for uncommon cards
        current_y += self.catalog_card_height + card_spacing_y + 20  # Less extra space for section
        current_x = start_x
        row_card_count = 0
        
        # Add uncommon cards header
        add_header("UNCOMMON CARDS", "uncommon", current_y)
        current_y += 15  # Adjust for header space
        
        # Add hearts J-A
        for value in range(11, 15):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            add_card_slot("hearts", value, "uncommon", position)
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
            
        # Add diamonds J-A
        for value in range(11, 15):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            add_card_slot("diamonds", value, "uncommon", position)
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1

        # Add 10 uncommon card placeholders
        for i in range(10):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            # Add placeholder
            self.card_catalog.append({
                "type": "unknown",
                "rarity": "uncommon",
                "position": position,
                "small": True  # Flag that this is a catalog item (smaller size)
            })
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
        
        # 3. RARE CARDS (Placeholders)
        
        # Start new row for rare cards
        current_y += self.catalog_card_height + card_spacing_y + 20  # Less extra space for section
        current_x = start_x
        row_card_count = 0
        
        # Add rare cards header
        add_header("RARE CARDS", "rare", current_y)
        current_y += 15  # Adjust for header space
        
        # Add 20 rare card placeholders
        for i in range(20):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            
            # Add placeholder
            self.card_catalog.append({
                "type": "unknown",
                "rarity": "rare",
                "position": position,
                "small": True  # Flag that this is a catalog item (smaller size)
            })
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
            
        # 4. EXOTIC CARDS (Placeholders)
        
        # Start new row for exotic cards
        current_y += self.catalog_card_height + card_spacing_y + 20  # Less extra space for section
        current_x = start_x
        row_card_count = 0
        
        # Add exotic cards header
        add_header("EXOTIC CARDS", "exotic", current_y)
        current_y += 15  # Adjust for header space
        
        # Add 10 exotic card placeholders
        for i in range(10):
            if row_card_count >= cards_per_row:
                # Start new row
                current_y += self.catalog_card_height + card_spacing_y
                current_x = start_x
                row_card_count = 0
            
            position = (current_x, current_y)
            
            # Add placeholder
            self.card_catalog.append({
                "type": "unknown",
                "rarity": "exotic",
                "position": position,
                "small": True  # Flag that this is a catalog item (smaller size)
            })
            
            # Move to next slot
            current_x += self.catalog_card_width + card_spacing_x
            row_card_count += 1
        
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
                
                # Update button text
                if self.show_library:
                    self.toggle_button.text = "SHOW DELVING DECK"
                else:
                    self.toggle_button.text = "SHOW CARD LIBRARY"
                
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
                        self.hovered_item = {"type": "card", "card": card}
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
            # Delving deck view - update all cards
            for card in self.delving_deck_cards:
                card.update(delta_time)
                
                if card.is_flipping:
                    card.update_flip(delta_time)
        else:
            # Library view - only update owned cards in the catalog
            for item in self.card_catalog:
                if item.get("type") == "card" and item.get("owned") and item.get("card"):
                    item["card"].update(delta_time)
                    
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
            collection_text = f"{len(self.card_library)}/{len(self.card_catalog) - len([i for i in self.card_catalog if i.get('type') == 'header' or i.get('type') == 'placeholder'])}"
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
                    header_text = self.header_font.render(item["title"], True, self.rarity_colors[item["rarity"]])
                    header_rect = header_text.get_rect(center=item["position"])
                    surface.blit(header_text, header_rect)
                elif item["type"] == "card":
                    position = item["position"]
                    
                    # Draw card border based on rarity - use catalog card size
                    border_rect = pygame.Rect(
                        position[0] - 2, position[1] - 2,
                        self.catalog_card_width + 4, self.catalog_card_height + 4
                    )
                    pygame.draw.rect(surface, self.rarity_colors[item["rarity"]], border_rect, 2, border_radius=6)
                    
                    if item["owned"]:
                        # If the card is owned, we'll draw the card object itself later
                        # to handle hover effects properly
                        if item.get("card"):
                            # Need to draw the card at the smaller catalog size
                            # First check if card isn't being hovered or dragged (those are drawn separately)
                            if not item.get("card").is_hovered and item.get("card") != self.dragging_card:
                                # Draw the card at the catalog size - scale it down from the original
                                # Store original rect
                                original_rect = item["card"].rect
                                
                                # Calculate scale factor
                                scale_factor = self.catalog_card_width / CARD_WIDTH
                                
                                # Temporarily update card's rect for drawing at smaller size
                                item["card"].rect = pygame.Rect(
                                    position[0], 
                                    position[1], 
                                    self.catalog_card_width, 
                                    self.catalog_card_height
                                )
                                
                                # Create a temporary flag to indicate this is a small catalog card
                                item["card"].is_catalog_card = True
                                item["card"].scale_factor = scale_factor
                                
                                # Draw the card
                                item["card"].draw(surface)
                                
                                # Remove the temporary flag
                                if hasattr(item["card"], 'is_catalog_card'):
                                    delattr(item["card"], 'is_catalog_card')
                                if hasattr(item["card"], 'scale_factor'):
                                    delattr(item["card"], 'scale_factor')
                                
                                # Restore original rect
                                item["card"].rect = original_rect
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
                    
                    # Draw card border based on rarity - use catalog card size
                    border_rect = pygame.Rect(
                        position[0] - 2, position[1] - 2,
                        self.catalog_card_width + 4, self.catalog_card_height + 4
                    )
                    pygame.draw.rect(surface, self.rarity_colors[item["rarity"]], border_rect, 2, border_radius=6)
                    
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
                
                # Draw a subtle highlight border
                border_rect = pygame.Rect(
                    position[0] - 2, position[1] - 2,
                    self.catalog_card_width + 4, self.catalog_card_height + 4
                )
                # Use a slightly dimmer version of the rarity color for a more subtle effect
                rarity_color = self.rarity_colors[self.hovered_item["rarity"]]
                hover_color = (int(rarity_color[0] * 0.8), int(rarity_color[1] * 0.8), int(rarity_color[2] * 0.8))
                pygame.draw.rect(surface, hover_color, border_rect, 2, border_radius=6)
                
                # Store original rect
                original_rect = self.hovered_item["card"].rect
                
                # Calculate scale factor
                scale_factor = self.catalog_card_width / CARD_WIDTH
                
                # Temporarily update card's rect for drawing at smaller size
                self.hovered_item["card"].rect = pygame.Rect(
                    position[0], 
                    position[1], 
                    self.catalog_card_width, 
                    self.catalog_card_height
                )
                
                # Create a temporary flag to indicate this is a small catalog card
                self.hovered_item["card"].is_catalog_card = True
                self.hovered_item["card"].scale_factor = scale_factor
                # Mark this as a hovered catalog card - need both flags for proper drawing
                self.hovered_item["card"].is_hovered = True
                self.hovered_item["card"].is_catalog_card = True
                
                # Draw the card
                self.hovered_item["card"].draw(surface)
                
                # Remove the temporary flags
                if hasattr(self.hovered_item["card"], 'is_catalog_card'):
                    delattr(self.hovered_item["card"], 'is_catalog_card')
                if hasattr(self.hovered_item["card"], 'scale_factor'):
                    delattr(self.hovered_item["card"], 'scale_factor')
                
                # Restore original rect
                self.hovered_item["card"].rect = original_rect
        
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
        # Calculate info box position relative to the hovered card
        info_width = 300
        info_height = 110
        
        # Get the card position and dimensions
        card_center_x = card.rect.centerx
        card_top = card.rect.top
        card_bottom = card.rect.bottom
        card_left = card.rect.left
        card_right = card.rect.right
        
        # Check if this is a catalog card (smaller size)
        is_catalog_card = hasattr(card, 'is_catalog_card') and card.is_catalog_card
        
        # For catalog view, use a simplified positioning strategy
        if self.show_library or is_catalog_card:
            # In library view, always position info to the right of the card
            # This is simpler and more predictable
            info_x = card_right + 5
            info_y = card_top
            
            # But if it would go off-screen to the right, position left of card
            if info_x + info_width > self.main_panel.rect.right - 10:
                info_x = card_left - info_width - 5
            
            # Ensure it stays within vertical bounds
            if info_y + info_height > self.main_panel.rect.bottom - 10:
                info_y = self.main_panel.rect.bottom - info_height - 10
        else:
            # In delving deck view, position based on card location
            panel_middle_y = self.main_panel.rect.top + self.main_panel.rect.height // 2
            
            # In bottom half of screen, show above
            if card_top > panel_middle_y:
                info_y = card_top - info_height - 20
                info_x = card_center_x - (info_width // 2)
            else:
                # In top half of screen, show below
                info_y = card_bottom + 20
                info_x = card_center_x - (info_width // 2)
        
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
        
        # Card name
        name_text = self.header_font.render(card.name, True, WHITE)
        name_rect = name_text.get_rect(centerx=info_x + info_width//2, top=info_y + 10)
        surface.blit(name_text, name_rect)
        
        # Card type and details
        if card.type == "weapon":
            type_text = f"Weapon - "
            if hasattr(card, 'weapon_type') and card.weapon_type:
                if card.weapon_type == "ranged":
                    type_text += "Ranged"
                elif card.weapon_type == "melee":
                    type_text += "Melee"
                elif card.weapon_type == "arrow":
                    type_text += "Arrow (Ammo)"
            
            damage_text = f"Damage: {card.value}"
            
            type_render = self.body_font.render(type_text, True, GOLD_COLOR)
            type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=name_rect.bottom + 10)
            surface.blit(type_render, type_rect)
            
            damage_render = self.body_font.render(damage_text, True, WHITE)
            damage_rect = damage_render.get_rect(centerx=info_x + info_width//2, top=type_rect.bottom + 5)
            surface.blit(damage_render, damage_rect)
            
        elif card.type == "potion":
            type_text = "Potion - Healing"
            heal_text = f"Restores {card.value} health"
            
            type_render = self.body_font.render(type_text, True, GOLD_COLOR)
            type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=name_rect.bottom + 10)
            surface.blit(type_render, type_rect)
            
            heal_render = self.body_font.render(heal_text, True, WHITE)
            heal_rect = heal_render.get_rect(centerx=info_x + info_width//2, top=type_rect.bottom + 5)
            surface.blit(heal_render, heal_rect)
    
    def _draw_mystery_info(self, surface, item):
        """Draw mystery info for an unowned card or placeholder"""
        # Skip if no item
        if not item:
            return
            
        # Check for required properties
        if "position" not in item:
            return
            
        # Calculate info box position relative to the hovered item
        info_width = 200  # Slightly smaller info panel
        info_height = 70
        
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
            
        # For catalog view, use a simplified positioning strategy - fixed offset from card
        if self.show_library:
            # In library view, always position info to the right of the card
            # This is simpler and more predictable
            info_x = position[0] + item_width + 5
            info_y = position[1]
            
            # But if it would go off-screen to the right, position left of card
            if info_x + info_width > self.main_panel.rect.right - 10:
                info_x = position[0] - info_width - 5
            
            # Ensure it stays within vertical bounds
            if info_y + info_height > self.main_panel.rect.bottom - 10:
                info_y = self.main_panel.rect.bottom - info_height - 10
        else:
            # In delving deck view, use more complex positioning
            panel_middle_y = self.main_panel.rect.top + self.main_panel.rect.height // 2
            
            # In bottom half of screen, show above
            if item_top > panel_middle_y:
                info_y = item_top - info_height - 10
                info_x = item_center_x - (info_width // 2)
            else:
                # In top half of screen, show below
                info_y = item_bottom + 10
                info_x = item_center_x - (info_width // 2)
        
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
        
        # Draw mystery text
        if item.get("type") == "card" and not item.get("owned"):
            # For uncollected actual cards, show a hint
            if item.get("suit") == "hearts":
                type_hint = "Potion"
            elif item.get("suit") == "diamonds":
                type_hint = "Weapon" 
            else:
                type_hint = "Unknown"
                
            # Show hint text
            hint_text = self.header_font.render("???", True, WHITE)
            hint_rect = hint_text.get_rect(centerx=info_x + info_width//2, top=info_y + 10)
            surface.blit(hint_text, hint_rect)
            
            # Show type hint
            type_render = self.body_font.render(f"Type: {type_hint}", True, (150, 150, 150))
            type_rect = type_render.get_rect(centerx=info_x + info_width//2, top=hint_rect.bottom + 10)
            surface.blit(type_render, type_rect)
        else:
            # For placeholders, just show question marks
            mystery_text = self.header_font.render("???", True, WHITE)
            mystery_rect = mystery_text.get_rect(centerx=info_x + info_width//2, top=info_y + 10)
            surface.blit(mystery_text, mystery_rect)
            
            # Show rarity text
            rarity_render = self.body_font.render(f"{item['rarity'].capitalize()}", True, self.rarity_colors[item["rarity"]])
            rarity_rect = rarity_render.get_rect(centerx=info_x + info_width//2, top=mystery_rect.bottom + 10)
            surface.blit(rarity_render, rarity_rect)