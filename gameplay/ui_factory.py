"""UI Factory for creating UI elements in the Scoundrel game."""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
from constants import ITEM_PANEL_POSITION, SPELL_PANEL_POSITION, ITEM_PANEL_WIDTH, ITEM_PANEL_HEIGHT, SPELL_PANEL_WIDTH, SPELL_PANEL_HEIGHT
from constants import WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY
from ui.button import Button
from ui.panel import Panel


class UIFactory:
    """Creates and manages UI elements."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
    
    def create_item_spell_panels(self):
        """Create panels for displaying items and spells."""
        # Dungeon-themed colors
        dark_parchment = (60, 45, 35)  # For panel backgrounds
        wood_border = (95, 65, 35)     # For panel borders
        
        # Item panel (left side)
        item_panel_rect = pygame.Rect(ITEM_PANEL_POSITION, (ITEM_PANEL_WIDTH, ITEM_PANEL_HEIGHT))
        self.playing_state.item_panel = Panel(
            (item_panel_rect.width, item_panel_rect.height),
            (item_panel_rect.left, item_panel_rect.top),
            colour=dark_parchment,
            alpha=210,
            border_radius=8,
            dungeon_style=True,
            border_width=3,
            border_color=wood_border
        )

        # Spell panel (right side) - slightly more blue tint for magical feel
        spell_panel_rect = pygame.Rect(SPELL_PANEL_POSITION, (SPELL_PANEL_WIDTH, SPELL_PANEL_HEIGHT))
        spell_bg_color = (50, 50, 65)  # Slightly blueish for magical theme
        spell_border = (65, 65, 95)    # Slightly blue-tinted border
        self.playing_state.spell_panel = Panel(
            (spell_panel_rect.width, spell_panel_rect.height),
            (spell_panel_rect.left, spell_panel_rect.top),
            colour=spell_bg_color,
            alpha=210,
            border_radius=8,
            dungeon_style=True,
            border_width=3,
            border_color=spell_border
        )

        # Create item and spell buttons
        self.create_item_buttons()
        self.create_spell_buttons()
    
    def create_item_buttons(self):
        """Create buttons for player items."""
        self.playing_state.item_buttons = []
        
        # Create a panel for items
        item_panel_rect = pygame.Rect(20, 20, 160, 200)
        
        # Create buttons for each item
        for i, item in enumerate(self.playing_state.game_manager.item_manager.player_items):
            button_rect = pygame.Rect(
                item_panel_rect.left + 10,
                item_panel_rect.top + 40 + (i * 50),
                140,
                40
            )
            
            self.playing_state.item_buttons.append({
                "item": item,
                "index": i,
                "button": Button(button_rect, item.name, self.playing_state.normal_font)
            })
    
    def create_spell_buttons(self):
        """Create buttons for player spells."""
        self.playing_state.spell_buttons = []
        
        # Create a panel for spells
        spell_panel_rect = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 200)
        
        # Create buttons for each spell
        for i, spell in enumerate(self.playing_state.game_manager.spell_manager.player_spells):
            button_rect = pygame.Rect(
                spell_panel_rect.left + 10,
                spell_panel_rect.top + 40 + (i * 50),
                140,
                40
            )
            
            self.playing_state.spell_buttons.append({
                "spell": spell,
                "index": i,
                "button": Button(button_rect, spell.name, self.playing_state.normal_font)
            })
    
    def create_run_button(self):
        """Create the run button with dungeon styling."""
        # Increase button size to be more prominent
        run_width = 80  # Wider button
        run_height = 40  # Taller button
        
        # Position below status UI and above room
        run_x = SCREEN_WIDTH // 2
        run_y = 150  # Below status UI, above room
        
        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)
        
        # Use the Pixel Times font with dungeon styling
        self.playing_state.run_button = Button(
            run_button_rect, 
            "RUN", 
            self.playing_state.body_font,
            text_color=WHITE,  # White text for better visibility
            dungeon_style=True,  # Enable dungeon styling
            panel_color=(70, 20, 20),  # Dark red for urgency
            border_color=(120, 40, 40)  # Red border for danger/action
        )