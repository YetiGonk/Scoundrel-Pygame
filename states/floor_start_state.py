""" Floor start state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from utils.resource_loader import ResourceLoader

class FloorStartState(GameState):
    """The floor starting screen where players select items/spells."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        
        # Available selections
        self.available_items = []
        self.available_spells = []
        self.picks_remaining = 0
        
        # UI elements
        self.panels = {}
        self.buttons = {}
        self.item_buttons = []
        self.spell_buttons = []
        self.continue_button = None
    
    def enter(self):
        # Load fonts
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
        
        # Get available selections
        self.generate_selections()
        
        # Create UI elements
        self.create_ui()
    
    def generate_selections(self):
        """Generate the available items and spells to choose from."""
        from roguelike_constants import FLOOR_START_SELECTION
        
        # Get items
        item_manager = self.game_manager.item_manager
        self.available_items = item_manager.get_floor_start_selection()
        
        # Get spells
        spell_manager = self.game_manager.spell_manager
        self.available_spells = spell_manager.get_floor_start_selection()
        
        # Set number of picks
        self.picks_remaining = FLOOR_START_SELECTION["picks"]
    
    def create_ui(self):
        """Create the UI elements for the floor start state."""
        # Main panel
        self.panels["main"] = Panel(
            (800, 500),
            (SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 250),
            WHITE
        )
        
        # Items panel
        self.panels["items"] = Panel(
            (350, 400),
            (self.panels["main"].rect.left + 25, self.panels["main"].rect.top + 75)
        )
        
        # Spells panel
        self.panels["spells"] = Panel(
            (350, 400),
            (self.panels["main"].rect.right - 375, self.panels["main"].rect.top + 75)
        )
        
        # Continue button
        continue_rect = pygame.Rect(0, 0, 150, 40)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.bottom = self.panels["main"].rect.bottom - 20
        self.continue_button = Button(continue_rect, "Continue", self.body_font)
        
        # Create item buttons
        self.create_item_buttons()
        
        # Create spell buttons
        self.create_spell_buttons()
    
    def create_item_buttons(self):
        """Create buttons for items."""
        self.item_buttons = []
        
        for i, item in enumerate(self.available_items):
            button_rect = pygame.Rect(
                self.panels["items"].rect.left + 10,
                self.panels["items"].rect.top + 40 + (i * 80),
                330,
                70
            )
            
            self.item_buttons.append({
                "item": item,
                "button": Button(button_rect, item.name, self.normal_font)
            })
    
    def create_spell_buttons(self):
        """Create buttons for spells."""
        self.spell_buttons = []
        
        for i, spell in enumerate(self.available_spells):
            button_rect = pygame.Rect(
                self.panels["spells"].rect.left + 10,
                self.panels["spells"].rect.top + 40 + (i * 80),
                330,
                70
            )
            
            self.spell_buttons.append({
                "spell": spell,
                "button": Button(button_rect, spell.name, self.normal_font)
            })
    
    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            # Check button hover states
            self.continue_button.check_hover(event.pos)
            
            for item_data in self.item_buttons:
                item_data["button"].check_hover(event.pos)
            
            for spell_data in self.spell_buttons:
                spell_data["button"].check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if continue button was clicked
            if self.continue_button.is_clicked(event.pos):
                # Only allow continue if all picks are used or if there are no more options
                if self.picks_remaining <= 0 or (not self.available_items and not self.available_spells):
                    self.game_manager.change_state("playing")
                return
            
            # Check if an item button was clicked and we have picks remaining
            if self.picks_remaining > 0:
                for item_data in self.item_buttons:
                    if item_data["button"].is_clicked(event.pos):
                        self.select_item(item_data["item"])
                        return
                
                # Check if a spell button was clicked
                for spell_data in self.spell_buttons:
                    if spell_data["button"].is_clicked(event.pos):
                        self.select_spell(spell_data["spell"])
                        return
    
    def select_item(self, item):
        """Select an item to add to the player's inventory."""
        if self.game_manager.item_manager.add_player_item(item):
            self.picks_remaining -= 1
            self.available_items.remove(item)
            # Refresh UI
            self.create_item_buttons()
    
    def select_spell(self, spell):
        """Select a spell to add to the player's spellbook."""
        if self.game_manager.spell_manager.add_player_spell(spell):
            self.picks_remaining -= 1
            self.available_spells.remove(spell)
            # Refresh UI
            self.create_spell_buttons()
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
        
        # Draw floor title
        floor_type = self.game_manager.floor_manager.get_current_floor() or "unknown"
        floor_index = self.game_manager.floor_manager.current_floor_index + 1
        title_text = self.header_font.render(f"Floor {floor_index}: {floor_type.capitalize()}", True, BLACK)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 20)
        surface.blit(title_text, title_rect)
        
        # Draw picks remaining
        picks_text = self.body_font.render(f"Picks Remaining: {self.picks_remaining}", True, BLACK)
        picks_rect = picks_text.get_rect(centerx=self.panels["main"].rect.centerx, top=title_rect.bottom + 10)
        surface.blit(picks_text, picks_rect)
        
        # Draw section headings
        items_text = self.body_font.render("Items", True, BLACK)
        items_rect = items_text.get_rect(centerx=self.panels["items"].rect.centerx, top=self.panels["items"].rect.top + 10)
        surface.blit(items_text, items_rect)
        
        spells_text = self.body_font.render("Spells", True, BLACK)
        spells_rect = spells_text.get_rect(centerx=self.panels["spells"].rect.centerx, top=self.panels["spells"].rect.top + 10)
        surface.blit(spells_text, spells_rect)
        
        # Draw continue button
        self.continue_button.draw(surface)
        
        # Draw item buttons and details
        for item_data in self.item_buttons:
            item = item_data["item"]
            button = item_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the rarity and description
            rarity_text = self.normal_font.render(f"Rarity: {item.rarity.capitalize()}", True, BLACK)
            rarity_rect = rarity_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(rarity_text, rarity_rect)
            
            desc_text = self.normal_font.render(item.description[:40] + ("..." if len(item.description) > 40 else ""), True, BLACK)
            desc_rect = desc_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
            surface.blit(desc_text, desc_rect)
        
        # Draw spell buttons and details
        for spell_data in self.spell_buttons:
            spell = spell_data["spell"]
            button = spell_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the rarity and description
            rarity_text = self.normal_font.render(f"Rarity: {spell.rarity.capitalize()}", True, BLACK)
            rarity_rect = rarity_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(rarity_text, rarity_rect)
            
            desc_text = self.normal_font.render(spell.description[:40] + ("..." if len(spell.description) > 40 else ""), True, BLACK)
            desc_rect = desc_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
            surface.blit(desc_text, desc_rect)