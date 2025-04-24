"""UI Renderer for drawing game elements in the Scoundrel game."""
import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT
from constants import WHITE, BLACK, GRAY, DARK_GRAY, LIGHT_GRAY, GOLD_COLOR, FONTS_PATH
from utils.resource_loader import ResourceLoader


class UIRenderer:
    """Handles rendering of UI elements and game objects."""
    
    def __init__(self, playing_state):
        """Initialize with a reference to the playing state."""
        self.playing_state = playing_state
    
    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""
        # Health display parameters
        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y
        health_bar_width = 160
        health_bar_height = 40
        
        # Create or update health panel with dungeon style
        if not hasattr(self, 'health_panel'):
            panel_rect = pygame.Rect(
                health_display_x - 10, 
                health_display_y - health_bar_height - 20,
                health_bar_width + 20,
                health_bar_height + 20
            )
            
            # Create the panel with a dark wooden appearance for the health bar container
            from ui.panel import Panel
            self.health_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),  # Very dark brown
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)  # Medium brown border
            )
        
        # Draw the styled health panel
        self.health_panel.draw(surface)
        
        # Draw health bar background with stone texture for a dungeon feel
        bar_bg_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            health_bar_height
        )
        
        # Create stone texture for background
        stone_bg = pygame.Surface((bar_bg_rect.width, bar_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(stone_bg, (50, 50, 55), pygame.Rect(0, 0, bar_bg_rect.width, bar_bg_rect.height), border_radius=5)
        
        # Add noise to the stone
        for x in range(0, bar_bg_rect.width, 3):
            for y in range(0, bar_bg_rect.height, 3):
                # Random stone texture
                noise = random.randint(0, 25)
                stone_colour = (50 + noise, 50 + noise, 55 + noise, 255)
                pygame.draw.rect(stone_bg, stone_colour, (x, y, 3, 3))
        
        # Draw the stone background
        surface.blit(stone_bg, bar_bg_rect.topleft)
        
        # Calculate health percentage
        health_percent = self.playing_state.life_points / self.playing_state.max_life
        health_width = int(health_bar_width * health_percent)
        
        # Choose colour based on health percentage with a more magical/fantasy glow
        if health_percent > 0.7:
            health_colour = (50, 220, 100)  # Vibrant green with magical tint
            glow_colour = (100, 255, 150, 40)  # Green glow
        elif health_percent > 0.3:
            health_colour = (255, 155, 20)  # Warmer orange
            glow_colour = (255, 180, 50, 40)  # Orange glow
        else:
            health_colour = (255, 30, 30)  # Bright red
            glow_colour = (255, 70, 70, 40)  # Red glow
        
        # Draw health bar with inner glow effect
        if health_width > 0:
            health_rect = pygame.Rect(
                health_display_x,
                health_display_y - health_bar_height - 10,
                health_width,
                health_bar_height
            )
            
            # Main health bar
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)
            
            # Create a glow effect
            glow_surf = pygame.Surface((health_width, health_bar_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_colour, pygame.Rect(0, 0, health_width, health_bar_height), border_radius=5)
            
            # Apply the glow
            surface.blit(glow_surf, health_rect.topleft)
        
        # Add a subtle inner shadow at the top for depth
        shadow_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            8
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        surface.blit(shadow_surface, shadow_rect)
        
        # Add highlights at the bottom for 3D effect
        if health_width > 0:
            highlight_rect = pygame.Rect(
                health_display_x,
                health_display_y - 18,
                health_width,
                8
            )
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_surface.fill((255, 255, 255, 60))
            surface.blit(highlight_surface, highlight_rect)
        
        # Draw health text with a subtle glow for better readability
        health_text = self.playing_state.body_font.render(f"{self.playing_state.life_points}/{self.playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)
        
        # Draw a subtle glow behind the text
        glow_surf = pygame.Surface((health_text.get_width() + 10, health_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 255, 255, 30), glow_surf.get_rect())
        glow_rect = glow_surf.get_rect(center=health_text_rect.center)
        
        # Draw the glow and text
        surface.blit(glow_surf, glow_rect)
        surface.blit(health_text, health_text_rect)
    
    def draw_gold_display(self, surface):
        """Draw gold display showing current gold amount."""
        # Gold display parameters - placed ABOVE health display
        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y
        gold_display_x = health_display_x
        gold_display_y = health_display_y - 130  # Position above health display
        
        # Load the gold coin image
        gold_icon = ResourceLoader.load_image("ui/gold.png")
        
        # Get icon dimensions
        icon_width = gold_icon.get_width()
        icon_height = gold_icon.get_height()
        
        # Render gold amount to calculate panel size
        gold_text = self.playing_state.body_font.render(f"{self.playing_state.game_manager.player_gold}", True, (255, 223, 0))
        
        # Create gold panel with treasure chest appearance
        if not hasattr(self, 'gold_panel'):
            # Calculate panel size based on icon and text
            panel_width = icon_width + gold_text.get_width() + 80
            panel_height = max(icon_height, gold_text.get_height()) + 20
            
            from ui.panel import Panel
            # Create a special panel with gold/treasure colours
            self.gold_panel = Panel(
                (panel_width, panel_height),
                (gold_display_x - 10, gold_display_y - 10),
                colour=(60, 40, 20),  # Dark wood/treasure chest colour
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(150, 120, 40)  # Gold-coloured border
            )
            
            # Store the position for the icon
            self.gold_icon_pos = (gold_display_x, gold_display_y)
        
        # Draw the panel
        self.gold_panel.draw(surface)
        
        # Draw gold particles focused on the gold icon for a treasure feel
        if not hasattr(self, 'gold_particles'):
            self.gold_particles = []
            
            # Calculate boundaries for the gold icon area
            icon_left = self.gold_icon_pos[0]
            icon_right = self.gold_icon_pos[0] + icon_width
            icon_top = self.gold_icon_pos[1]
            icon_bottom = self.gold_icon_pos[1] + icon_height
            
            # Add more particles for a better effect
            for _ in range(7):  # Increased from 5 to 7
                self.gold_particles.append({
                    # Restrict x-range to the gold icon area, plus a small margin
                    'x': random.randint(icon_left, icon_right),
                    'y': random.randint(icon_top, icon_bottom),
                    'size': random.randint(1, 2),  # Smaller particles (was 1-3)
                    'alpha': random.randint(100, 200),
                    'speed': random.uniform(0.1, 0.3)
                })
        
        # Update and draw gold particles
        for particle in self.gold_particles:
            # Subtle movement
            particle['y'] -= particle['speed']
            particle['alpha'] -= 1
            
            # Calculate icon boundaries (in case icon_pos changes)
            icon_left = self.gold_icon_pos[0]
            icon_right = self.gold_icon_pos[0] + icon_width
            icon_top = self.gold_icon_pos[1]
            icon_bottom = self.gold_icon_pos[1] + icon_height
            
            # Reset particles that fade out or move off-screen
            if particle['alpha'] < 50 or particle['y'] < icon_top:
                # Reset position to within the gold icon area
                particle['x'] = random.randint(icon_left, icon_right)
                particle['y'] = random.randint(icon_bottom - 5, icon_bottom)  # Start from bottom of icon
                particle['alpha'] = random.randint(150, 200)
            
            # Draw the particle
            pygame.draw.circle(
                surface, 
                (255, 215, 0, particle['alpha']),  # Gold colour
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
        
        # Draw the gold coin icon
        surface.blit(gold_icon, self.gold_icon_pos)
        
        # Draw gold amount with gold-coloured text
        gold_text = self.playing_state.body_font.render(f"{self.playing_state.game_manager.player_gold}", True, (255, 223, 0))  # Gold text
        gold_text_rect = gold_text.get_rect(
            right=health_display_x + icon_width + 65,
            centery=self.gold_icon_pos[1] + icon_height//2
        )
        
        # Add dark outline to make gold text readable (subtle glow effect)
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x == 0 and offset_y == 0:
                    continue  # Skip the center position
                # Add darker outline
                gold_outline = self.playing_state.body_font.render(
                    f"{self.playing_state.game_manager.player_gold}", 
                    True, 
                    (100, 70, 0)
                )
                surface.blit(
                    gold_outline, 
                    (gold_text_rect.x + offset_x, gold_text_rect.y + offset_y)
                )
        
        # Draw the gold text on top
        surface.blit(gold_text, gold_text_rect)
    
    def _draw_card_shadow(self, surface, card):
        """Draw shadow effect for a card"""
        shadow_alpha = 60
        shadow_width = 4
        shadow_rect = card.rect.inflate(shadow_width * 2, shadow_width * 2)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=3)
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
