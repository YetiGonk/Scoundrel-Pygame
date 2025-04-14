"""
Button UI component for the Scoundrel game with optional dungeon styling.
"""
import pygame
from constants import LIGHT_GRAY, BLACK, WHITE

class Button:    
    def __init__(self, rect, text, font, text_color=BLACK, bg_color=LIGHT_GRAY, border_color=BLACK, 
                dungeon_style=False, panel_color=(60, 45, 35), border_width=3):
        self.rect = rect
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.is_hovered = False
        self.dungeon_style = dungeon_style
        self.panel_color = panel_color
        self.border_width = border_width
        self.panel = None
        
        # Pre-render the text
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
        # Create styled panel if requested
        if self.dungeon_style:
            self._create_dungeon_panel()
    
    def _create_dungeon_panel(self):
        """Create a dungeon-styled panel for the button"""
        try:
            from ui.panel import Panel
            
            # Create the panel with a stone/wooden appearance
            self.panel = Panel(
                (self.rect.width, self.rect.height),
                (self.rect.left, self.rect.top),
                colour=self.panel_color,
                alpha=250,  # More opaque for buttons
                border_radius=8,
                dungeon_style=True,
                border_width=self.border_width,
                border_color=self.border_color
            )
        except ImportError:
            # Fallback if Panel isn't available
            self.dungeon_style = False
            
    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update visual appearance when hover state changes
        if previous_hover != self.is_hovered and self.dungeon_style and self.panel:
            if self.is_hovered:
                # Make border lighter when hovered
                lighter_border = self._lighten_color(self.border_color, 0.3)
                self.panel.update_style(True, self.border_width, lighter_border)
            else:
                # Reset to original border
                self.panel.update_style(True, self.border_width, self.border_color)
                
        return previous_hover != self.is_hovered
    
    def _lighten_color(self, color, factor=0.3):
        """Create a lighter version of the color"""
        r, g, b = color[0], color[1], color[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        if self.dungeon_style and self.panel:
            # Draw the styled panel
            self.panel.draw(surface)
            
            # Draw the text with glow for emphasis
            if self.is_hovered:
                # Add glow effect on hover
                glow_size = 6
                glow_surface = pygame.Surface(
                    (self.text_surface.get_width() + glow_size*2, 
                     self.text_surface.get_height() + glow_size*2), 
                    pygame.SRCALPHA
                )
                
                # Create glow color based on text color
                if self.text_color == WHITE or sum(self.text_color) > 400:  # Light text
                    glow_color = (255, 255, 255, 30)  # White glow
                else:  # Dark text
                    glow_color = (0, 0, 0, 30)  # Dark glow
                    
                # Draw radial gradient
                pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
                glow_rect = glow_surface.get_rect(center=self.text_rect.center)
                surface.blit(glow_surface, glow_rect)
            
            # Draw the text
            surface.blit(self.text_surface, self.text_rect)
        else:
            # Draw traditional button background with rounded corners
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
            
            # Draw button border with rounded corners
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=5)
            
            # Draw button text
            surface.blit(self.text_surface, self.text_rect)