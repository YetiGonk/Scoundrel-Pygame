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
        """Update active effects and remove expired ones."""
        current_time = pygame.time.get_ticks()
        
        # Filter out expired effects
        self.active_effects = [effect for effect in self.active_effects if (
            effect['duration'] is None) or  # Permanent effects
            ((current_time - effect['start_time']) < effect['duration'])  # Temporary effects
        ]
    
    def draw(self, surface):
        """Draw the HUD elements."""
        # Draw active effects
        self.draw_active_effects(surface)
        
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
        pygame.draw.rect(surface, GRAY, bg_rect)
        
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
        pygame.draw.rect(surface, health_color, health_rect)
        
        # Draw border
        pygame.draw.rect(surface, BLACK, bg_rect, 2)
        
        # Draw text
        health_text = self.normal_font.render(f"HP: {playing_state.life_points}/{playing_state.max_life}", True, WHITE)
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