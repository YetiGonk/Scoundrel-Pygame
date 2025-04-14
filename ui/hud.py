"""
HUD component for displaying active effects and item/spell information
"""
import pygame
import random
import math
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
        
        # Gold particles for visual effect
        self.gold_particles = []
        self.last_particle_time = 0
        
        # Panel instances for health and gold indicators
        self.health_panel = None
        self.gold_panel = None
    
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
        """Draw icons for active effects with dungeon styling."""
        try:
            from ui.panel import Panel
            using_panels = True
        except ImportError:
            using_panels = False
            
        for i, effect in enumerate(self.active_effects):
            # Calculate position
            x = self.effect_start_pos[0] + i * (self.effect_icon_size + self.effect_spacing)
            y = self.effect_start_pos[1]
            
            # Effect rect
            effect_rect = pygame.Rect(x, y, self.effect_icon_size, self.effect_icon_size)
            
            # Choose color based on effect type
            effect_color = BLUE  # Default
            if effect['type'] == 'shield':
                effect_color = (60, 120, 200)  # Blue
                panel_color = (40, 70, 120)
                border_color = (80, 140, 220)
                icon_symbol = "✦"  # Star/Shield symbol
            elif effect['type'] == 'healing':
                effect_color = (60, 180, 80)  # Green
                panel_color = (40, 100, 50)
                border_color = (70, 190, 90)
                icon_symbol = "+"  # Plus/healing symbol
            elif effect['type'] == 'damage':
                effect_color = (190, 60, 60)  # Red
                panel_color = (100, 40, 40)
                border_color = (200, 70, 70)
                icon_symbol = "⚔"  # Sword symbol
            elif effect['type'] == 'gold':
                effect_color = (220, 180, 50)  # Gold
                panel_color = (100, 80, 30)
                border_color = (230, 190, 60)
                icon_symbol = "⚜"  # Gold symbol
            else:
                effect_color = (100, 100, 160)  # Default blue
                panel_color = (50, 50, 80)
                border_color = (120, 120, 180)
                icon_symbol = "◆"  # Default diamond symbol
            
            # Draw effect icon with panel if available
            if using_panels:
                # Create a dungeon-styled panel for this effect
                effect_panel = Panel(
                    (self.effect_icon_size, self.effect_icon_size),
                    (x, y),
                    colour=panel_color,
                    alpha=230,
                    border_radius=6,
                    dungeon_style=True,
                    border_width=2,
                    border_color=border_color
                )
                effect_panel.draw(surface)
                
                # Calculate time-based pulse effect for active effects
                current_time = pygame.time.get_ticks()
                if effect['duration'] is not None:
                    # Calculate how much time has passed (0.0 to 1.0)
                    elapsed = (current_time - effect['start_time']) / effect['duration']
                    # Create a pulsating effect that gets faster as time runs out
                    pulse_factor = 0.8 + 0.2 * math.sin(elapsed * 10 + current_time / 200)
                else:
                    # For permanent effects, use a slower, subtler pulse
                    pulse_factor = 0.9 + 0.1 * math.sin(current_time / 800)
                
                # Draw a glowing circle as the effect icon
                glow_radius = int(self.effect_icon_size * 0.3 * pulse_factor)
                center_x = x + self.effect_icon_size // 2
                center_y = y + self.effect_icon_size // 2
                
                # Draw outer glow
                for r in range(glow_radius, 0, -1):
                    alpha = max(0, 150 - (glow_radius - r) * 20)
                    pygame.draw.circle(surface, (*effect_color, alpha), 
                                     (center_x, center_y), r)
                                     
                # Draw icon symbol in the center
                symbol_font = pygame.font.SysFont(None, int(self.effect_icon_size * 0.6))
                symbol_text = symbol_font.render(icon_symbol, True, WHITE)
                symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
                surface.blit(symbol_text, symbol_rect)
            else:
                # Fallback to simple rectangles if Panel isn't available
                pygame.draw.rect(surface, effect_color, effect_rect)
                pygame.draw.rect(surface, BLACK, effect_rect, 2)
            
            # Draw value if available
            if effect['value'] is not None:
                value_text = self.normal_font.render(str(effect['value']), True, WHITE)
                value_rect = value_text.get_rect(center=effect_rect.center)
                
                # For panel-style, position below the effect
                if using_panels:
                    value_rect.midtop = (x + self.effect_icon_size // 2, y + self.effect_icon_size + 2)
                
                surface.blit(value_text, value_rect)
            
            # Draw duration if available
            if effect['duration'] is not None:
                remaining = max(0, effect['duration'] - (pygame.time.get_ticks() - effect['start_time']))
                remaining_text = self.small_font.render(f"{remaining//1000}s", True, WHITE)
                
                # Position differently based on whether we have a value displayed
                if effect['value'] is not None and using_panels:
                    # Position below the value
                    remaining_rect = remaining_text.get_rect(
                        midtop=(x + self.effect_icon_size // 2, 
                               y + self.effect_icon_size + value_text.get_height() + 4)
                    )
                else:
                    # Position at the bottom of the effect
                    remaining_rect = remaining_text.get_rect(
                        midbottom=(x + self.effect_icon_size // 2, 
                                  y + self.effect_icon_size + (10 if using_panels else 0))
                    )
                
                # Add urgency visual cues for effects about to expire
                if remaining < 2000:  # Less than 2 seconds left
                    # Use red text for urgency
                    remaining_text = self.small_font.render(f"{remaining//1000}s", True, (255, 100, 100))
                    
                    # Add pulsating effect as time runs out
                    pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 100)
                    scaled_size = int(remaining_text.get_width() * pulse), int(remaining_text.get_height() * pulse)
                    if scaled_size[0] > 0 and scaled_size[1] > 0:  # Ensure valid size
                        pulsed_text = pygame.transform.scale(remaining_text, scaled_size)
                        remaining_rect = pulsed_text.get_rect(center=remaining_rect.center)
                        surface.blit(pulsed_text, remaining_rect)
                    else:
                        surface.blit(remaining_text, remaining_rect)
                else:
                    surface.blit(remaining_text, remaining_rect)
    
    def draw_gold_indicator(self, surface):
        """Draw gold indicator above the health bar with dungeon styling."""
        # Health bar parameters - we'll position relative to these
        bar_width = 200
        bar_height = 24
        health_x = 20
        health_y = SCREEN_HEIGHT - 30
        
        # Gold indicator parameters
        gold_bar_width = 120
        gold_bar_height = 24
        x = health_x
        y = health_y - gold_bar_height - 10  # Position above health bar
        
        # Create panel if it doesn't exist
        if not self.gold_panel:
            try:
                from ui.panel import Panel
                
                # Use a treasure chest color scheme
                self.gold_panel = Panel(
                    (gold_bar_width, gold_bar_height),
                    (x, y),
                    colour=(80, 60, 30),  # Dark wooden color
                    alpha=240,
                    border_radius=8,
                    dungeon_style=True,
                    border_width=2,
                    border_color=(130, 100, 40)  # Lighter wooden border
                )
                
                # Store gold icon position for particle effects
                self.gold_icon_pos = (x + 15, y + gold_bar_height // 2)
                self.gold_icon_size = (16, 16)
            except ImportError:
                # Fallback if Panel isn't available
                self.gold_panel = None
        
        # Draw the panel
        if self.gold_panel:
            self.gold_panel.draw(surface)
            
            # Draw gold coin icon with golden glow
            coin_radius = 8
            coin_x, coin_y = self.gold_icon_pos
            
            # Draw subtle glow behind coin
            glow_radius = coin_radius + 4
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            for r in range(glow_radius, 0, -1):
                alpha = max(0, 60 - (glow_radius - r) * 15)
                pygame.draw.circle(glow_surface, (255, 230, 100, alpha), (glow_radius, glow_radius), r)
            surface.blit(glow_surface, (coin_x - glow_radius, coin_y - glow_radius))
            
            # Draw coin with metallic effect
            pygame.draw.circle(surface, (255, 223, 0), (coin_x, coin_y), coin_radius)  # Gold fill
            pygame.draw.circle(surface, (255, 240, 120), (coin_x - 3, coin_y - 3), coin_radius//2)  # Highlight
            pygame.draw.circle(surface, (184, 134, 11), (coin_x, coin_y), coin_radius, 1)  # Gold border
            
            # Update and draw gold particles
            self._update_gold_particles()
            self._draw_gold_particles(surface)
            
            # Draw gold value with golden text
            gold_text = self.normal_font.render(f"{self.game_manager.player_gold}", True, (255, 230, 150))
            gold_text_rect = gold_text.get_rect(centery=coin_y, x=coin_x + coin_radius + 10)
            surface.blit(gold_text, gold_text_rect)
        else:
            # Fallback to basic rendering if panel isn't available
            bg_rect = pygame.Rect(x, y, gold_bar_width, gold_bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)
            
            # Draw gold bar
            gold_color = (255, 215, 0)  # Gold color
            gold_rect = pygame.Rect(x, y, gold_bar_width, gold_bar_height)
            pygame.draw.rect(surface, gold_color, gold_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)
            
            # Draw coin and text
            coin_radius = 8
            coin_x = x + 15
            coin_y = y + gold_bar_height // 2
            pygame.draw.circle(surface, (255, 223, 0), (coin_x, coin_y), coin_radius)
            pygame.draw.circle(surface, (184, 134, 11), (coin_x, coin_y), coin_radius, 2)
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
            
            # Position and draw the text - account for panel position
            text_x = x + gold_bar_width - 30
            text_y = y - y_offset - 15
            change_rect = text_surface.get_rect(center=(text_x, text_y))
            surface.blit(text_surface, change_rect)
            
            # Spawn gold particles on gain
            if self.gold_change_amount > 0 and current_time - self.gold_change_time < 200:
                self._add_gold_particles(min(5, self.gold_change_amount // 2 + 1))
    
    def _update_gold_particles(self):
        """Update gold particle positions and properties"""
        # Remove dead particles
        self.gold_particles = [p for p in self.gold_particles if p['alpha'] > 0]
        
        # Update remaining particles
        for particle in self.gold_particles:
            # Move particles upward
            particle['y'] -= particle['speed']
            # Fade out gradually
            particle['alpha'] -= random.uniform(0.5, 1.5)
            # Slightly randomize x position for shimmering effect
            particle['x'] += random.uniform(-0.2, 0.2)
    
    def _draw_gold_particles(self, surface):
        """Draw gold particles for a treasure effect"""
        if not self.gold_particles:
            return
            
        for particle in self.gold_particles:
            if particle['alpha'] <= 0:
                continue
                
            # Calculate particle color with alpha
            gold_color = (255, 223, 0, min(255, int(particle['alpha'])))
            
            # Draw the particle
            pygame.draw.circle(
                surface, 
                gold_color, 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
            
            # Add highlight to some particles for sparkle effect
            if random.random() < 0.3:  # 30% chance
                highlight_color = (255, 255, 230, min(200, int(particle['alpha'])))
                pygame.draw.circle(
                    surface, 
                    highlight_color, 
                    (int(particle['x'] - 1), int(particle['y'] - 1)), 
                    max(1, particle['size'] // 2)
                )
    
    def _add_gold_particles(self, count):
        """Add new gold particles near the coin icon"""
        if not hasattr(self, 'gold_icon_pos'):
            return
            
        coin_x, coin_y = self.gold_icon_pos
        coin_width, coin_height = self.gold_icon_size
        
        for _ in range(count):
            # Create particles within/around the coin area
            self.gold_particles.append({
                'x': coin_x + random.uniform(-5, 5),
                'y': coin_y + random.uniform(-5, 5),
                'size': random.uniform(1, 2.5),
                'speed': random.uniform(0.2, 0.6),
                'alpha': random.uniform(180, 255)
            })
    
    def draw_health_indicator(self, surface):
        """Draw a health bar indicator with dungeon styling."""
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return
        
        # Health bar parameters
        bar_width = 200
        bar_height = 24
        x = 20
        y = SCREEN_HEIGHT - 30
        
        # Create panel if it doesn't exist
        if not self.health_panel:
            try:
                from ui.panel import Panel
                
                # Use a blood/potion themed color scheme
                self.health_panel = Panel(
                    (bar_width, bar_height),
                    (x, y),
                    colour=(60, 30, 30),  # Dark red/brown
                    alpha=240,
                    border_radius=8,
                    dungeon_style=True,
                    border_width=2,
                    border_color=(100, 50, 50)  # Lighter red border
                )
            except ImportError:
                # Fallback if Panel isn't available
                self.health_panel = None
        
        # Calculate health percentage
        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int((bar_width - 10) * health_percent)  # Leave margin for styling
        
        # Choose color based on health percentage
        if health_percent > 0.7:
            health_color = (50, 180, 50)  # Green
            glow_color = (70, 220, 70, 40)  # Green glow
        elif health_percent > 0.3:
            health_color = (220, 160, 40)  # Orange
            glow_color = (240, 180, 60, 40)  # Orange glow
        else:
            health_color = (200, 50, 50)  # Red
            glow_color = (240, 90, 90, 40)  # Red glow
            
        # Draw the panel for health bar container
        if self.health_panel:
            self.health_panel.draw(surface)
            
            # Draw health bar with inner glow and margin
            health_rect = pygame.Rect(x + 5, y + 5, health_width, bar_height - 10)
            
            # Draw glow effect for health bar
            glow_surface = pygame.Surface((health_width + 10, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, 
                          (5, 0, health_width, bar_height - 10), border_radius=4)
            surface.blit(glow_surface, (x, y))
            
            # Draw the actual health bar
            pygame.draw.rect(surface, health_color, health_rect, border_radius=4)
            
            # Add highlight to top of health bar for 3D effect
            if health_width > 4:
                highlight_color = self._lighten_color(health_color, 0.3)
                pygame.draw.rect(surface, highlight_color, 
                              (x + 5, y + 5, health_width, 2), border_radius=2)
        else:
            # Fallback to simpler rendering
            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)
            
            health_rect = pygame.Rect(x, y, health_width, bar_height)
            pygame.draw.rect(surface, health_color, health_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)
        
        # Draw health value with appropriate color based on health status
        text_color = WHITE
        health_text = self.normal_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, text_color)
        health_text_rect = health_text.get_rect(center=(x + bar_width//2, y + bar_height//2))
        surface.blit(health_text, health_text_rect)
    
    def _lighten_color(self, color, factor=0.3):
        """Create a lighter version of the color"""
        r, g, b = color[0], color[1], color[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))
    
    def draw_damage_shield(self, surface):
        """Draw a damage shield indicator with magical dungeon styling."""
        playing_state = self.game_manager.states["playing"]
        if playing_state.damage_shield <= 0:
            return
        
        # Shield parameters
        shield_radius = 150
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Create animated time-based effect (pulsating shield)
        time_ms = pygame.time.get_ticks()
        pulse_factor = 0.1 * (1 + 0.15 * math.sin(time_ms / 500))  # Pulsate every 0.5 seconds
        
        # Draw magical shield effect with multiple layers for depth
        shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Inner core with pulsating size
        inner_radius = int(shield_radius * 0.8 * pulse_factor)
        pygame.draw.circle(shield_surface, (50, 120, 230, 20), (center_x, center_y), inner_radius)
        
        # Main shield layer with arcane-like pattern
        pygame.draw.circle(shield_surface, (70, 140, 255, 40), (center_x, center_y), shield_radius)
        
        # Draw a slightly translucent edge for a magical barrier look
        edge_width = max(2, int(5 * pulse_factor))
        pygame.draw.circle(shield_surface, (100, 180, 255, 120), (center_x, center_y), shield_radius, edge_width)
        
        # Add arcane runes or symbols (simplified as dashed lines)
        dash_length = 15
        dash_gap = 10
        num_dashes = 16
        rune_radius = shield_radius - 10
        
        for i in range(num_dashes):
            angle = 2 * math.pi * i / num_dashes
            start_x = center_x + int(rune_radius * math.cos(angle))
            start_y = center_y + int(rune_radius * math.sin(angle))
            end_x = center_x + int((rune_radius - dash_length) * math.cos(angle))
            end_y = center_y + int((rune_radius - dash_length) * math.sin(angle))
            
            # Vary color slightly for visual interest
            rune_alpha = 150 + int(50 * math.sin((time_ms / 200) + i))
            rune_color = (180, 200, 255, rune_alpha)
            
            pygame.draw.line(shield_surface, rune_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Draw shield particles for magical effect (occasional sparks)
        if random.random() < 0.1:  # 10% chance per frame
            spark_angle = random.uniform(0, 2 * math.pi)
            spark_distance = shield_radius * random.uniform(0.9, 1.1)
            spark_x = center_x + int(spark_distance * math.cos(spark_angle))
            spark_y = center_y + int(spark_distance * math.sin(spark_angle))
            
            # Draw a magical spark
            spark_radius = random.randint(2, 4)
            pygame.draw.circle(shield_surface, (220, 240, 255, 200), (spark_x, spark_y), spark_radius)
            
            # Add glow around spark
            glow_radius = spark_radius * 3
            for r in range(glow_radius, 0, -1):
                alpha = max(0, 100 - (glow_radius - r) * 25)
                pygame.draw.circle(shield_surface, (150, 200, 255, alpha), 
                                  (spark_x, spark_y), r)
        
        # Blit the complete shield effect
        surface.blit(shield_surface, (0, 0))
        
        # Create a stylized panel for shield value display
        from ui.panel import Panel
        
        # Shield panel positioning
        panel_width = 120
        panel_height = 30
        panel_x = center_x - panel_width // 2
        panel_y = center_y - shield_radius - 35
        
        shield_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 60, 120),  # Blue/magical color
            alpha=220,
            border_radius=10,
            dungeon_style=True,
            border_width=2,
            border_color=(80, 130, 200)  # Lighter blue border
        )
        shield_panel.draw(surface)
        
        # Draw shield value with magical glow
        shield_text = self.normal_font.render(f"Shield: {playing_state.damage_shield}", True, (180, 220, 255))
        
        # Create glow behind text
        glow_surface = pygame.Surface((shield_text.get_width() + 10, shield_text.get_height() + 10), pygame.SRCALPHA)
        glow_color = (100, 150, 255, 50)
        pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
        
        # Position and draw
        shield_text_rect = shield_text.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height//2))
        glow_rect = glow_surface.get_rect(center=shield_text_rect.center)
        
        surface.blit(glow_surface, glow_rect)
        surface.blit(shield_text, shield_text_rect)