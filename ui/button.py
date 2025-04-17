"""
Button UI component for the Scoundrel game with optional dungeon styling.
"""
import pygame
from constants import (
    LIGHT_GRAY, BLACK, WHITE,
    BUTTON_PANEL_COLOR, BUTTON_BORDER_WIDTH, BUTTON_BORDER_RADIUS, 
    BUTTON_ALPHA, BUTTON_GLOW_SIZE, BUTTON_HOVER_GLOW_WHITE, 
    BUTTON_HOVER_GLOW_DARK, BUTTON_HOVER_LIGHTEN, BUTTON_ROUND_CORNER
)

class Button:    
    def __init__(self, rect, text, font, text_colour=BLACK, bg_colour=LIGHT_GRAY, border_colour=BLACK, 
                dungeon_style=False, panel_colour=None, border_width=None, callback=None):
        # Use constants for defaults
        if panel_colour is None:
            panel_colour = BUTTON_PANEL_COLOR
        if border_width is None:
            border_width = BUTTON_BORDER_WIDTH
        self.rect = rect
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.bg_colour = bg_colour
        self.border_colour = border_colour
        self.is_hovered = False
        self.dungeon_style = dungeon_style
        self.panel_colour = panel_colour
        self.border_width = border_width
        self.panel = None
        self.callback = callback
        
        # Pre-render the text
        self.text_surface = font.render(text, True, text_colour)
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
                colour=self.panel_colour,
                alpha=BUTTON_ALPHA,
                border_radius=BUTTON_BORDER_RADIUS,
                dungeon_style=True,
                border_width=self.border_width,
                border_colour=self.border_colour
            )
        except ImportError:
            # Fallback if Panel isn't available
            self.dungeon_style = False
            
    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update visual appearance when hover state changes
        if previous_hover != self.is_hovered and self.dungeon_style and self.panel:
            if self.is_hovered:
                # Make border lighter when hovered
                lighter_border = self._lighten_colour(self.border_colour, BUTTON_HOVER_LIGHTEN)
                self.panel.update_style(True, self.border_width, lighter_border)
            else:
                # Reset to original border
                self.panel.update_style(True, self.border_width, self.border_colour)
                
        return previous_hover != self.is_hovered
    
    def _lighten_colour(self, colour, factor=BUTTON_HOVER_LIGHTEN):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))
    
    def is_clicked(self, mouse_pos):
        is_clicked = self.rect.collidepoint(mouse_pos)
        if is_clicked and self.callback:
            self.callback()
        return is_clicked
    
    def draw(self, surface):
        if self.dungeon_style and self.panel:
            # Draw the styled panel
            self.panel.draw(surface)
            
            # Draw the text with glow for emphasis
            if self.is_hovered:
                # Add glow effect on hover
                glow_size = BUTTON_GLOW_SIZE
                glow_surface = pygame.Surface(
                    (self.text_surface.get_width() + glow_size*2, 
                     self.text_surface.get_height() + glow_size*2), 
                    pygame.SRCALPHA
                )
                
                # Create glow colour based on text colour
                if self.text_colour == WHITE or sum(self.text_colour) > 400:  # Light text
                    glow_colour = BUTTON_HOVER_GLOW_WHITE
                else:  # Dark text
                    glow_colour = BUTTON_HOVER_GLOW_DARK
                    
                # Draw radial gradient
                pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
                glow_rect = glow_surface.get_rect(center=self.text_rect.center)
                surface.blit(glow_surface, glow_rect)
            
            # Draw the text
            surface.blit(self.text_surface, self.text_rect)
        else:
            # Draw traditional button background with rounded corners
            pygame.draw.rect(surface, self.bg_colour, self.rect, border_radius=BUTTON_ROUND_CORNER)
            
            # Draw button border with rounded corners
            pygame.draw.rect(surface, self.border_colour, self.rect, 2, border_radius=BUTTON_ROUND_CORNER)
            
            # Draw button text
            surface.blit(self.text_surface, self.text_rect)