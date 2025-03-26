""" Merchant state for the Scoundrel game. """
import pygame
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from utils.resource_loader import ResourceLoader

class MerchantState(GameState):
    """The merchant screen state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        
        # Inventory
        self.items_for_sale = []
        self.spells_for_sale = []
        self.cards_for_sale = []
        
        # UI elements
        self.panels = {}
        self.buttons = {}
        self.item_buttons = []
        self.spell_buttons = []
        self.card_buttons = []
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
        
        # Generate inventory
        self.generate_inventory()
        
        # Create UI elements
        self.create_ui()
    
    def generate_inventory(self):
        """Generate the merchant's inventory."""
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()
        
        # Get items, spells, and cards for sale
        from constants import MERCHANT_INVENTORY
        
        # Get items for sale
        item_manager = self.game_manager.item_manager
        rarity_weights = self.get_rarity_weights_for_floor(floor_manager.current_floor_index)
        self.items_for_sale = item_manager.get_random_items(
            MERCHANT_INVENTORY["items"], 
            rarity_weights
        )
        
        # Get spells for sale
        spell_manager = self.game_manager.spell_manager
        self.spells_for_sale = spell_manager.get_random_spells(
            MERCHANT_INVENTORY["spells"],
            rarity_weights
        )
        
        # TODO: Implement special cards for sale
        self.cards_for_sale = []
    
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
        """Create the UI elements for the merchant state."""
        # Main panel
        self.panels["main"] = Panel(
            (800, 500),
            (SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 250),
            WHITE
        )
        
        # Items panel
        self.panels["items"] = Panel(
            (250, 400),
            (self.panels["main"].rect.left + 25, self.panels["main"].rect.top + 75)
        )
        
        # Spells panel
        self.panels["spells"] = Panel(
            (250, 400),
            (self.panels["main"].rect.left + 300, self.panels["main"].rect.top + 75)
        )
        
        # Cards panel
        self.panels["cards"] = Panel(
            (200, 400),
            (self.panels["main"].rect.left + 575, self.panels["main"].rect.top + 75)
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
        
        # Create card buttons
        self.create_card_buttons()
    
    def create_item_buttons(self):
        """Create buttons for items."""
        self.item_buttons = []
        
        for i, item in enumerate(self.items_for_sale):
            button_rect = pygame.Rect(
                self.panels["items"].rect.left + 10,
                self.panels["items"].rect.top + 40 + (i * 80),
                230,
                70
            )
            
            self.item_buttons.append({
                "item": item,
                "button": Button(button_rect, item.name, self.normal_font)
            })
    
    def create_spell_buttons(self):
        """Create buttons for spells."""
        self.spell_buttons = []
        
        for i, spell in enumerate(self.spells_for_sale):
            button_rect = pygame.Rect(
                self.panels["spells"].rect.left + 10,
                self.panels["spells"].rect.top + 40 + (i * 80),
                230,
                70
            )
            
            self.spell_buttons.append({
                "spell": spell,
                "button": Button(button_rect, spell.name, self.normal_font)
            })
    
    def create_card_buttons(self):
        """Create buttons for cards."""
        self.card_buttons = []
        
        for i, card in enumerate(self.cards_for_sale):
            button_rect = pygame.Rect(
                self.panels["cards"].rect.left + 10,
                self.panels["cards"].rect.top + 40 + (i * 80),
                180,
                70
            )
            
            self.card_buttons.append({
                "card": card,
                "button": Button(button_rect, f"Card: {card.get('name', 'Unknown')}", self.normal_font)
            })
    
    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            # Check button hover states
            self.continue_button.check_hover(event.pos)
            
            for item_data in self.item_buttons:
                item_data["button"].check_hover(event.pos)
            
            for spell_data in self.spell_buttons:
                spell_data["button"].check_hover(event.pos)
            
            for card_data in self.card_buttons:
                card_data["button"].check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if continue button was clicked
            if self.continue_button.is_clicked(event.pos):
                self.game_manager.change_state("playing")
                return
            
            # Check if an item button was clicked
            for item_data in self.item_buttons:
                if item_data["button"].is_clicked(event.pos):
                    self.purchase_item(item_data["item"])
                    return
            
            # Check if a spell button was clicked
            for spell_data in self.spell_buttons:
                if spell_data["button"].is_clicked(event.pos):
                    self.purchase_spell(spell_data["spell"])
                    return
            
            # Check if a card button was clicked
            for card_data in self.card_buttons:
                if card_data["button"].is_clicked(event.pos):
                    self.purchase_card(card_data["card"])
                    return
    
    def purchase_item(self, item):
        """Purchase an item if the player has enough gold."""
        if self.game_manager.player_gold >= item.price:
            if self.game_manager.item_manager.add_player_item(item):
                self.game_manager.player_gold -= item.price
                self.items_for_sale.remove(item)
                # Refresh UI
                self.create_item_buttons()
    
    def purchase_spell(self, spell):
        """Purchase a spell if the player has enough gold."""
        if self.game_manager.player_gold >= spell.price:
            if self.game_manager.spell_manager.add_player_spell(spell):
                self.game_manager.player_gold -= spell.price
                self.spells_for_sale.remove(spell)
                # Refresh UI
                self.create_spell_buttons()
    
    def purchase_card(self, card):
        """Purchase a special card if the player has enough gold."""
        if self.game_manager.player_gold >= card.get("price", 0):
            # TODO: Implement card purchasing
            self.game_manager.player_gold -= card.get("price", 0)
            self.cards_for_sale.remove(card)
            # Refresh UI
            self.create_card_buttons()
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(title_text, title_rect)
        
        # Draw section headings
        items_text = self.body_font.render("Items", True, BLACK)
        items_rect = items_text.get_rect(centerx=self.panels["items"].rect.centerx, top=self.panels["items"].rect.top + 10)
        surface.blit(items_text, items_rect)
        
        spells_text = self.body_font.render("Spells", True, BLACK)
        spells_rect = spells_text.get_rect(centerx=self.panels["spells"].rect.centerx, top=self.panels["spells"].rect.top + 10)
        surface.blit(spells_text, spells_rect)
        
        cards_text = self.body_font.render("Cards", True, BLACK)
        cards_rect = cards_text.get_rect(centerx=self.panels["cards"].rect.centerx, top=self.panels["cards"].rect.top + 10)
        surface.blit(cards_text, cards_rect)
        
        # Draw player gold
        gold_text = self.body_font.render(f"Gold: {self.game_manager.player_gold}", True, BLACK)
        gold_rect = gold_text.get_rect(left=self.panels["main"].rect.left + 20, bottom=self.panels["main"].rect.bottom - 20)
        surface.blit(gold_text, gold_rect)
        
        # Draw buttons
        self.continue_button.draw(surface)
        
        # Draw item buttons and prices
        for item_data in self.item_buttons:
            item = item_data["item"]
            button = item_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price and durability
            price_text = self.normal_font.render(f"Price: {item.price}", True, BLACK)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)
            
            if item.durability > 0:
                durability_text = self.normal_font.render(f"Uses: {item.durability}", True, BLACK)
                durability_rect = durability_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
                surface.blit(durability_text, durability_rect)
        
        # Draw spell buttons and prices
        for spell_data in self.spell_buttons:
            spell = spell_data["spell"]
            button = spell_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price and memory
            price_text = self.normal_font.render(f"Price: {spell.price}", True, BLACK)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)
            
            memory_text = self.normal_font.render(f"Memory: {spell.memory_points}", True, BLACK)
            memory_rect = memory_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
            surface.blit(memory_text, memory_rect)
        
        # Draw card buttons and prices
        for card_data in self.card_buttons:
            card = card_data["card"]
            button = card_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price
            price_text = self.normal_font.render(f"Price: {card.get('price', 0)}", True, BLACK)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)
            surface.blit(self.background, (0, 0))
            surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
        
        # Draw merchant title
        floor_type = self.game_manager.floor_manager.get_current_floor() or "unknown"
        title_text = self.header_font.render(f"{floor_type.capitalize()} Merchant", True, BLACK)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 20)
        surface.blit(title_text, title_rect)