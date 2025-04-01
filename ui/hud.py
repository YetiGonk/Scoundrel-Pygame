"""
HUD component for displaying active effects and item/spell information
"""
import pygame
from constants import WHITE, BLACK, GRAY, BLUE, GREEN, RED, SCREEN_WIDTH, SCREEN_HEIGHT

class HUD:
    """Heads-up display for showing active effects and status."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.normal_font = pygame.font.SysFont(None, 20)
        self.small_font = pygame.font.SysFont(None, 16)
        
        # Active effects (damage shield, etc.)
        self.active_effects = []
        
        # Effect icon positions
        self.effect_icon_size = 40
        self.effect_spacing = 10
        self.effect_start_pos = (SCREEN_WIDTH//2 - 100, 20)
        
        # Resource tracking for animations
        self.last_gold_amount = game_manager.player_gold
        self.gold_change_time = 0
        self.gold_change_amount = 0
    
    def update_fonts(self, normal_font, small_font=None):
        """Update fonts if they are loaded after initialization."""
        self.normal_font = normal_font
        if small_font:
            self.small_font = small_font
    
    def add_effect(self, effect_type, duration=None, value=None):
        """Add a new active effect to display."""
        self.active_effects.append({
            'type': effect_type,
            'duration': duration,  # None for permanent effects
            'value': value,
            'start_time': pygame.time.get_ticks()
        })
    
    def update(self):
        """Update active effects and resource animations."""
        current_time = pygame.time.get_ticks()
        
        # Filter out expired effects
        self.active_effects = [effect for effect in self.active_effects if (
            effect['duration'] is None) or  # Permanent effects
            ((current_time - effect['start_time']) < effect['duration'])  # Temporary effects
        ]
        
        # Check for gold changes
        current_gold = self.game_manager.player_gold
        if current_gold != self.last_gold_amount:
            self.gold_change_amount = current_gold - self.last_gold_amount
            self.gold_change_time = current_time
            # Add a gold effect if player gained gold
            if self.gold_change_amount > 0:
                self.add_effect('gold', 2000, self.gold_change_amount)
            self.last_gold_amount = current_gold
    
    def draw(self, surface):
        """Draw the HUD elements."""
        # Draw active effects
        self.draw_active_effects(surface)
        
        # Draw gold indicator
        self.draw_gold_indicator(surface)
        
        # Draw health indicator
        self.draw_health_indicator(surface)
        
        # Draw damage shield if active
        if hasattr(self.game_manager.states["playing"], 'damage_shield') and self.game_manager.states["playing"].damage_shield > 0:
            self.draw_damage_shield(surface)
    
    def draw_active_effects(self, surface):
        """Draw icons for active effects."""
        for i, effect in enumerate(self.active_effects):
            # Calculate position
            x = self.effect_start_pos[0] + i * (self.effect_icon_size + self.effect_spacing)
            y = self.effect_start_pos[1]
            
            # Draw effect icon
            effect_rect = pygame.Rect(x, y, self.effect_icon_size, self.effect_icon_size)
            
            # Choose color based on effect type
            effect_color = BLUE  # Default
            if effect['type'] == 'shield':
                effect_color = BLUE
            elif effect['type'] == 'healing':
                effect_color = GREEN
            elif effect['type'] == 'damage':
                effect_color = RED
            elif effect['type'] == 'gold':
                effect_color = (255, 215, 0)  # Gold
            
            # Draw effect icon
            pygame.draw.rect(surface, effect_color, effect_rect)
            pygame.draw.rect(surface, BLACK, effect_rect, 2)
            
            # Draw value if available
            if effect['value'] is not None:
                value_text = self.normal_font.render(str(effect['value']), True, WHITE)
                value_rect = value_text.get_rect(center=effect_rect.center)
                surface.blit(value_text, value_rect)
            
            # Draw duration if available
            if effect['duration'] is not None:
                remaining = effect['duration'] - (pygame.time.get_ticks() - effect['start_time'])
                remaining_text = self.small_font.render(f"{remaining//1000}s", True, WHITE)
                remaining_rect = remaining_text.get_rect(midbottom=effect_rect.midbottom)
                surface.blit(remaining_text, remaining_rect)
    
    def draw_gold_indicator(self, surface):
        """Draw gold indicator above the health bar."""
        # Health bar parameters - we'll position relative to these
        bar_width = 200
        bar_height = 20
        health_x = 20
        health_y = SCREEN_HEIGHT - 30
        
        # Gold indicator parameters
        gold_bar_width = 120
        gold_bar_height = 20
        x = health_x
        y = health_y - gold_bar_height - 10  # Position above health bar
        
        # Draw background 
        bg_rect = pygame.Rect(x, y, gold_bar_width, gold_bar_height)
        pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)
        
        # Draw gold bar - always full, just for visual consistency
        gold_color = (255, 215, 0)  # Gold color
        gold_rect = pygame.Rect(x, y, gold_bar_width, gold_bar_height)
        pygame.draw.rect(surface, gold_color, gold_rect, border_radius=5)
        
        # Draw border
        pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)
        
        # Draw gold coin icon inside the bar on the left
        coin_radius = 8
        coin_x = x + 15
        coin_y = y + gold_bar_height // 2
        pygame.draw.circle(surface, (255, 223, 0), (coin_x, coin_y), coin_radius)  # Brighter gold for the coin
        pygame.draw.circle(surface, (184, 134, 11), (coin_x, coin_y), coin_radius, 2)  # Darker gold border
        
        # Draw gold value with black text
        gold_text = self.normal_font.render(f"{self.game_manager.player_gold}", True, BLACK)
        gold_text_rect = gold_text.get_rect(center=bg_rect.center, x=coin_x + coin_radius + 10)
        surface.blit(gold_text, gold_text_rect)
        
        # Show gold change animation if recent
        current_time = pygame.time.get_ticks()
        if current_time - self.gold_change_time < 2000 and self.gold_change_amount != 0:
            # Determine animation properties
            alpha = 255 - int(255 * (current_time - self.gold_change_time) / 2000)  # Fade out
            y_offset = int(15 * (current_time - self.gold_change_time) / 2000)  # Float up
            
            # Create change text with appropriate color
            change_prefix = "+" if self.gold_change_amount > 0 else ""
            change_color = (50, 205, 50) if self.gold_change_amount > 0 else (220, 20, 60)
            
            # Create a text surface
            change_text = self.normal_font.render(f"{change_prefix}{self.gold_change_amount}", True, change_color)
            
            # Create a surface with per-pixel alpha
            text_surface = pygame.Surface(change_text.get_size(), pygame.SRCALPHA)
            
            # Blit the text onto the surface
            text_surface.blit(change_text, (0, 0))
            
            # Set the alpha for the entire surface
            text_surface.set_alpha(alpha)
            
            # Position and draw the text
            change_rect = text_surface.get_rect(center=(x + bar_width - 30, y - y_offset - 10))
            surface.blit(text_surface, change_rect)
    
    def draw_health_indicator(self, surface):
        """Draw a health bar indicator."""
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return
        
        # Health bar parameters
        bar_width = 200
        bar_height = 20
        x = 20
        y = SCREEN_HEIGHT - 30
        
        # Draw background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)
        
        # Calculate health percentage
        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int(bar_width * health_percent)
        
        # Choose color based on health percentage
        if health_percent > 0.7:
            health_color = GREEN
        elif health_percent > 0.3:
            health_color = (255, 165, 0)  # Orange
        else:
            health_color = RED
        
        # Draw health bar
        health_rect = pygame.Rect(x, y, health_width, bar_height)
        pygame.draw.rect(surface, health_color, health_rect, border_radius=5)
        
        # Draw border
        pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)
        
        # Draw health value
        health_text = self.normal_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bg_rect.center)
        surface.blit(health_text, health_text_rect)
    
    def draw_damage_shield(self, surface):
        """Draw a damage shield indicator."""
        playing_state = self.game_manager.states["playing"]
        if playing_state.damage_shield <= 0:
            return
        
        # Shield parameters
        shield_radius = 150
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw shield effect
        shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, (0, 100, 255, 50), (center_x, center_y), shield_radius)
        pygame.draw.circle(shield_surface, (0, 100, 255, 100), (center_x, center_y), shield_radius, 5)
        surface.blit(shield_surface, (0, 0))
        
        # Draw shield value
        shield_text = self.normal_font.render(f"Shield: {playing_state.damage_shield}", True, BLUE)
        shield_text_rect = shield_text.get_rect(center=(center_x, center_y - shield_radius - 20))
        surface.blit(shield_text, shield_text_rect)