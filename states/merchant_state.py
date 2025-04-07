""" Merchant state for the Scoundrel game. """
import pygame
import random
import math
from pygame.locals import *

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY
from roguelike_constants import MERCHANT_INVENTORY
from states.game_state import GameState
from ui.button import Button
from ui.panel import Panel
from ui.hud import HUD
from ui.status_ui import StatusUI
from utils.resource_loader import ResourceLoader
from utils.animation import Animation, EasingFunctions


class MerchantCharacter:
    """Represents the merchant character with idle animation."""
    
    def __init__(self, position, scale=10):
        # Load merchant sprite
        self.sprite = ResourceLoader.load_image("monsters/hooded_merchant.png")
        self.sprite_width = self.sprite.get_width()
        self.sprite_height = self.sprite.get_height()
        
        # Flip the sprite horizontally
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        
        # Define sprite features with correct positions from the flipped sprite
        # For flipped sprite, x coordinates are mirrored from right edge
        self.lantern_rect = pygame.Rect(self.sprite_width - 4 - 5, 20, 5, 6)  # Mirror lantern position
        self.left_eye_rect = pygame.Rect(self.sprite_width - 18 - 2, 9, 2, 1)  # Mirror right eye to left
        self.right_eye_rect = pygame.Rect(self.sprite_width - 14 - 2, 9, 2, 1)  # Mirror left eye to right
        
        # Scale up the sprite
        self.scale = scale
        self.scaled_width = int(self.sprite_width * scale)
        self.scaled_height = int(self.sprite_height * scale)
        self.sprite = pygame.transform.scale(self.sprite, (self.scaled_width, self.scaled_height))
        
        # Position (centered)
        self.position = position
        self.rect = self.sprite.get_rect()
        self.rect.center = (position[0] + self.scaled_width//2, position[1] - self.scaled_height//2)
        
        # Animation properties
        self.bob_offset = 0.0
        self.bob_speed = 2.0
        self.bob_height = 5.0
        self.time_passed = random.random() * 10  # Start at random phase
        
        # Breathing effect
        self.breath_scale = 1.0
        self.breath_speed = 1.5
        self.breath_amount = 0.03  # 3% size variation
        
        # Occasional blinking
        self.blink_timer = 0
        self.blink_interval = random.uniform(3.0, 8.0)  # Random time between blinks
        self.is_blinking = False
        self.blink_duration = 0.15  # How long a blink lasts
        
        # Lantern flame animation
        self.flame_intensity = 1.0
        self.flame_speed = 8.0
        
        # Add some particles for effect
        self.particles = []
        self.spawn_particle_timer = 0
        self.spawn_particle_interval = 0.8
        
    def update(self, delta_time):
        # Update time for animations
        self.time_passed += delta_time
        
        # Bob up and down
        self.bob_offset = math.sin(self.time_passed * self.bob_speed) * self.bob_height
        
        # Breathing effect
        self.breath_scale = 1.0 + math.sin(self.time_passed * self.breath_speed) * self.breath_amount
        
        # Flame intensity for lantern
        self.flame_intensity = 1.0 + 0.3 * math.sin(self.time_passed * self.flame_speed)
        
        # Blink occasionally
        if not self.is_blinking:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.is_blinking = True
                self.blink_timer = 0
                self.blink_interval = random.uniform(3.0, 8.0)  # Set next blink interval
        else:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_duration:
                self.is_blinking = False
                self.blink_timer = 0
                
        # Spawn particles from the lantern
        self.spawn_particle_timer += delta_time
        if self.spawn_particle_timer >= self.spawn_particle_interval:
            self.spawn_particle_timer = 0
            
            # Calculate lantern position in screen coordinates
            lantern_x = self.position[0] + self.lantern_rect.x * self.scale
            lantern_y = self.position[1] + self.lantern_rect.y * self.scale
            
            # Add a new particle from the lantern
            self.particles.append({
                'x': lantern_x + random.randint(0, int(self.lantern_rect.width * self.scale)),
                'y': lantern_y + random.randint(0, int(self.lantern_rect.height * self.scale // 2)),
                'size': random.randint(2, 6),
                'speed': random.uniform(13, 20),
                'life': 0,
                'max_life': random.uniform(3.0, 9.0),
                'color': (255, 215, random.randint(0, 100), 200)  # Gold-ish with alpha
            })
                
        # Update particles
        updated_particles = []
        for particle in self.particles:
            particle['life'] += delta_time
            if particle['life'] < particle['max_life']:
                # Move particle upward
                particle['y'] -= particle['speed'] * delta_time
                updated_particles.append(particle)
        self.particles = updated_particles
        
    def draw(self, surface):
        # Calculate the center of the sprite
        center_x = self.position[0] + self.scaled_width // 2
        center_y = self.position[1] + self.scaled_height // 2
        
        # Draw particles behind the merchant
        for particle in self.particles:
            # Calculate alpha based on life
            alpha = 255 * (1 - particle['life'] / particle['max_life'])
            color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
            
            # Create a temporary surface for the particle with alpha
            particle_surf = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (particle['size'], particle['size']), particle['size'])
            
            # Draw the particle
            surface.blit(particle_surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Apply breathing effect (centered scaling)
        if self.breath_scale != 1.0:
            # Calculate new dimensions
            breath_width = int(self.scaled_width * self.breath_scale)
            breath_height = int(self.scaled_height * self.breath_scale)
            
            # Create scaled sprite
            animated_sprite = pygame.transform.scale(self.sprite, (breath_width, breath_height))
            
            # Calculate position to keep centered
            x_pos = center_x - breath_width // 2
            y_pos = center_y - breath_height // 2 + self.bob_offset
        else:
            # No scaling needed
            animated_sprite = self.sprite
            x_pos = center_x - self.scaled_width // 2
            y_pos = center_y - self.scaled_height // 2 + self.bob_offset
        
        # Draw the merchant
        surface.blit(animated_sprite, (x_pos, y_pos))
        
        # Calculate the current display scale (accounting for breathing)
        current_scale = self.scale * self.breath_scale
        
        # Draw blink effect on eyes if blinking
        if self.is_blinking:
            # Left eye
            left_eye_x = x_pos + self.left_eye_rect.x * current_scale
            left_eye_y = y_pos + self.left_eye_rect.y * current_scale
            left_eye_width = self.left_eye_rect.width * current_scale
            left_eye_height = self.left_eye_rect.height * current_scale
            
            left_eye_rect = pygame.Rect(
                left_eye_x, left_eye_y, 
                left_eye_width, left_eye_height
            )
            
            # Right eye
            right_eye_x = x_pos + self.right_eye_rect.x * current_scale
            right_eye_y = y_pos + self.right_eye_rect.y * current_scale
            right_eye_width = self.right_eye_rect.width * current_scale
            right_eye_height = self.right_eye_rect.height * current_scale
            
            right_eye_rect = pygame.Rect(
                right_eye_x, right_eye_y, 
                right_eye_width, right_eye_height
            )
            
            # Draw eye covers
            pygame.draw.rect(surface, (0, 0, 0), left_eye_rect)
            pygame.draw.rect(surface, (0, 0, 0), right_eye_rect)
        
        # Draw lantern flame glow
        lantern_x = x_pos + self.lantern_rect.x * current_scale
        lantern_y = y_pos + self.lantern_rect.y * current_scale
        lantern_width = self.lantern_rect.width * current_scale
        lantern_height = self.lantern_rect.height * current_scale
        
        # Calculate flame center
        flame_x = lantern_x + lantern_width // 2
        flame_y = lantern_y + lantern_height // 3
        
        # Draw flame glow (multiple circles with decreasing opacity)
        flame_sizes = [5, 3, 2]
        flame_colors = [
            (255, 200, 50, 30),  # outer glow
            (255, 220, 80, 60),  # middle glow
            (255, 240, 120, 120)  # inner glow
        ]
        
        for i, size in enumerate(flame_sizes):
            # Scale flame intensity
            current_size = size * self.flame_intensity
            
            # Create a surface with alpha for the glow
            glow_surf = pygame.Surface((int(current_size*2), int(current_size*2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, flame_colors[i], (int(current_size), int(current_size)), int(current_size))
            
            # Draw at the lantern position
            surface.blit(glow_surf, (flame_x - current_size, flame_y - current_size))


class MerchantState(GameState):
    """The merchant screen state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        self.shade = None
        
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
        
        # Status displays
        self.hud = None
        self.status_ui = None
        
        # Merchant character
        self.merchant = None
    
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

        # Load shade
        self.shade = Panel((SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0), colour=DARK_GRAY, alpha=100, border_radius=0)

        # Generate inventory
        self.generate_inventory()
        
        # Create UI elements
        self.create_ui()
        
        # Initialize StatusUI with custom position
        self.status_ui = StatusUI(self.game_manager)
        self.status_ui.update_fonts(self.header_font, self.normal_font)
        # Adjust StatusUI position to be on the left side and not covered by main panel
        self.status_ui.panel_rect = pygame.Rect(
            80, 50,  # Move to left side
            320, 70  # Make it a bit smaller
        )
        
        # Load gold icon
        self.gold_icon = ResourceLoader.load_image("ui/gold.png")
        
        # Create the merchant character in the bottom left corner
        merchant_pos = (85, SCREEN_HEIGHT - 405)  # Position is the bottom-left anchor
        self.merchant = MerchantCharacter(merchant_pos)
        
        # Preserve the playing state's equipped weapon and defeated monsters
        playing_state = self.game_manager.states["playing"]
        # Store them in the game_manager to be restored when returning to playing state
        self.game_manager.equipped_weapon = playing_state.equipped_weapon
        self.game_manager.defeated_monsters = playing_state.defeated_monsters.copy()
    
    def generate_inventory(self):
        """Generate the merchant's inventory."""
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()
        
        # Get items, spells, and cards for sale
        from roguelike_constants import MERCHANT_INVENTORY
        
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
            (720, 530),
            (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 265),
            colour=DARK_GRAY
        )
        
        # Items panel
        self.panels["items"] = Panel(
            (200, 430),
            (self.panels["main"].rect.left + 30, self.panels["main"].rect.top + 75),
            colour=GRAY
        )
        
        # Spells panel
        self.panels["spells"] = Panel(
            (200, 430),
            (self.panels["main"].rect.left + 260, self.panels["main"].rect.top + 75),
            colour=GRAY
        )
        
        # Cards panel
        self.panels["cards"] = Panel(
            (200, 430),
            (self.panels["main"].rect.left + 490, self.panels["main"].rect.top + 75),
            colour=GRAY
        )
        
        # Continue button
        continue_rect = pygame.Rect(0, 0, 150, 40)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.top = self.panels["main"].rect.bottom - 15
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
                # Don't increment the room counter for merchant rooms
                # The current_room still points to the room before the merchant
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
            
    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""
        # Get player life points from playing_state
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return
            
        # Health display parameters
        health_display_x = 90
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
        health_text = self.body_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)
        surface.blit(health_text, health_text_rect)
        
    def draw_gold_display(self, surface):
        """Draw gold display showing current gold amount."""
        # Gold display parameters - placed right of health display

        gold_display_x = 290
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
    
    def update(self, delta_time):
        # Update merchant character animation
        if self.merchant:
            self.merchant.update(delta_time)
    
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
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
            
        # Draw merchant character
        if self.merchant:
            self.merchant.draw(surface)
        
        # Draw merchant title
        floor_type = self.game_manager.floor_manager.get_current_floor() or "unknown"
        title_text = self.header_font.render(f"{floor_type.capitalize()} Merchant", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 20)
        surface.blit(title_text, title_rect)
        
        # Draw section headings
        items_text = self.body_font.render("Items", True, WHITE)
        items_rect = items_text.get_rect(centerx=self.panels["items"].rect.centerx, top=self.panels["items"].rect.top + 10)
        surface.blit(items_text, items_rect)
        
        spells_text = self.body_font.render("Spells", True, WHITE)
        spells_rect = spells_text.get_rect(centerx=self.panels["spells"].rect.centerx, top=self.panels["spells"].rect.top + 10)
        surface.blit(spells_text, spells_rect)
        
        cards_text = self.body_font.render("Cards", True, WHITE)
        cards_rect = cards_text.get_rect(centerx=self.panels["cards"].rect.centerx, top=self.panels["cards"].rect.top + 10)
        surface.blit(cards_text, cards_rect)
        
        # Draw continue button
        self.continue_button.draw(surface)
        
        # Draw item buttons and prices
        for item_data in self.item_buttons:
            item = item_data["item"]
            button = item_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price and durability
            price_text = self.normal_font.render(f"Price: {item.price}", True, WHITE)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)
            
            if item.durability > 0:
                durability_text = self.normal_font.render(f"Uses: {item.durability}", True, WHITE)
                durability_rect = durability_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
                surface.blit(durability_text, durability_rect)
        
        # Draw spell buttons and prices
        for spell_data in self.spell_buttons:
            spell = spell_data["spell"]
            button = spell_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price and memory
            price_text = self.normal_font.render(f"Price: {spell.price}", True, WHITE)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)
            
            memory_text = self.normal_font.render(f"Memory: {spell.memory_points}", True, WHITE)
            memory_rect = memory_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 45)
            surface.blit(memory_text, memory_rect)
        
        # Draw card buttons and prices
        for card_data in self.card_buttons:
            card = card_data["card"]
            button = card_data["button"]
            
            # Draw the button
            button.draw(surface)
            
            # Draw the price
            price_text = self.normal_font.render(f"Price: {card.get('price', 0)}", True, WHITE)
            price_rect = price_text.get_rect(left=button.rect.left + 10, top=button.rect.top + 25)
            surface.blit(price_text, price_rect)