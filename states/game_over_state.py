"""
Game over state for the Scoundrel game with dungeon-themed styling.
"""
import pygame
import random
from pygame.locals import *

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, RED, LIGHT_GRAY, DARK_GRAY,
    PANEL_BORDER_RADIUS, PANEL_ALPHA, PANEL_BORDER_WIDTH
)
from states.game_state import GameState
from ui.panel import Panel
from ui.button import Button
from utils.resource_loader import ResourceLoader

class GameOverState(GameState):
    """The game over state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None
        
        # Styled buttons
        self.restart_button = None
        self.title_button = None
        
        # Game over panel
        self.game_over_panel = None
        
        # Particle effects
        self.particles = []
        
        # We will use the PlayingState to render the game in the background
        self.playing_state = None
    
    def enter(self):
        # Get the PlayingState instance for rendering
        self.playing_state = self.game_manager.states["playing"]
        
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 48)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        
        # Create game over panel
        panel_width = 580
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel colour based on victory/defeat
        if self.game_manager.game_data["victory"]:
            panel_colour = (40, 60, 40)  # Dark green for victory
            border_colour = (80, 180, 80)  # Brighter green border
        else:
            panel_colour = (60, 30, 30)  # Dark red for defeat
            border_colour = (150, 50, 50)  # Brighter red border
        
        self.game_over_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=panel_colour,
            alpha=240,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=border_colour
        )
        
        # Create buttons - wider and positioned lower
        button_width = 300  # Increased from 250 to 300
        button_height = 50
        button_spacing = 12
        buttons_y = panel_y + panel_height - button_height*2 - button_spacing - 33  # Moved down by 20 pixels
        
        # Restart button
        restart_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y,
            button_width, 
            button_height
        )
        self.restart_button = Button(
            restart_button_rect,
            "NEW ADVENTURE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 80, 40) if self.game_manager.game_data["victory"] else (80, 40, 40),
            border_colour=(80, 150, 80) if self.game_manager.game_data["victory"] else (150, 70, 70)
        )
        
        # Title screen button
        title_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + button_height + button_spacing,
            button_width, 
            button_height
        )
        self.title_button = Button(
            title_button_rect,
            "RETURN TO TITLE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 60, 80),
            border_colour=(100, 100, 160)
        )
        
        # Initialize particles based on victory/defeat
        self._create_particles()
    
    def _create_particles(self):
        """Create particles based on victory/defeat state"""
        self.particles = []
        
        # Number and colour of particles
        if self.game_manager.game_data["victory"]:
            num_particles = 40
            colours = [(120, 255, 120), (180, 255, 180), (220, 255, 220)]  # Green hues
        else:
            num_particles = 20
            colours = [(255, 120, 120), (255, 150, 150)]  # Red hues
        
        # Create particles around the panel
        for _ in range(num_particles):
            # Position around the panel edges
            edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
            
            if edge == 0:  # Top
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.top - 20, self.game_over_panel.rect.top + 20)
            elif edge == 1:  # Right
                x = random.uniform(self.game_over_panel.rect.right - 20, self.game_over_panel.rect.right + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)
            elif edge == 2:  # Bottom
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.bottom - 20, self.game_over_panel.rect.bottom + 20)
            else:  # Left
                x = random.uniform(self.game_over_panel.rect.left - 20, self.game_over_panel.rect.left + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)
            
            # Random colour from the palette
            colour = random.choice(colours)
            
            # Add particle
            self.particles.append({
                'x': x,
                'y': y,
                'colour': colour,
                'size': random.uniform(1.5, 3.5),
                'life': 1.0,  # Full life
                'decay': random.uniform(0.002, 0.005),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5)
            })
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check for button clicks
            if self.restart_button and self.restart_button.is_clicked(event.pos):
                # Reset game data
                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False
                
                # Completely reset the playing state
                from states.playing_state import PlayingState
                self.game_manager.states["playing"] = PlayingState(self.game_manager)
                
                # Make sure we preserve the player's card library between runs
                # The card_library contains all cards the player has collected
                if not hasattr(self.game_manager, 'card_library'):
                    self.game_manager.card_library = []
                
                # Start a new game
                self.game_manager.start_new_run()
            
            # Check for title button click
            elif self.title_button and self.title_button.is_clicked(event.pos):
                # Reset game data
                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False
                
                # Completely reset the playing state
                from states.playing_state import PlayingState
                self.game_manager.states["playing"] = PlayingState(self.game_manager)
                
                # Make sure we preserve the player's card library between runs
                # The card_library contains all cards the player has collected
                if not hasattr(self.game_manager, 'card_library'):
                    self.game_manager.card_library = []
                
                # Go to title screen
                self.game_manager.change_state("title")
        
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        if self.restart_button:
            self.restart_button.check_hover(mouse_pos)
        if self.title_button:
            self.title_button.check_hover(mouse_pos)
    
    def _update_particles(self, delta_time):
        """Update the particle effects"""
        # Update existing particles
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= particle['decay']
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Add new particles occasionally
        if random.random() < 0.1 and len(self.particles) < 60:
            self._create_particles()
    
    def update(self, delta_time):
        """Update game over state"""
        self._update_particles(delta_time)
    
    def draw(self, surface):
        # If playing state isn't available (or we want a cleaner look), draw a new background
        if not self.playing_state:
            # Create a darker background with a random floor type
            from constants import FLOOR_WIDTH, FLOOR_HEIGHT
            from roguelike_constants import FLOOR_TYPES
            import random
            
            # Draw the background
            if not hasattr(self, 'background') or not self.background:
                self.background = ResourceLoader.load_image("bg.png")
                if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
                    self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    
            # Draw background
            surface.blit(self.background, (0, 0))
            
            # Try to draw a random floor for variety
            if not hasattr(self, 'floor') or not self.floor:
                random_floor_type = random.choice(FLOOR_TYPES)
                floor_image = f"floors/{random_floor_type}_floor.png"
                
                try:
                    self.floor = ResourceLoader.load_image(floor_image)
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
                except:
                    # Fallback to the original floor image
                    self.floor = ResourceLoader.load_image("floor.png")
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
                    
            # Draw the floor
            surface.blit(self.floor, ((SCREEN_WIDTH - FLOOR_WIDTH)/2, (SCREEN_HEIGHT - FLOOR_HEIGHT)/2))
            
            # Draw a semi-transparent overlay to dim everything
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Dark with 150 alpha
            surface.blit(overlay, (0, 0))
        else:
            # Draw the game state behind (this assumes PlayingState.draw can work in a "view only" mode)
            self.playing_state.draw(surface)
            
            # Draw a semi-transparent overlay to dim the background
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Dark with 150 alpha
            surface.blit(overlay, (0, 0))
        
        # Draw particle effects behind the panel
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            # Make sure we're creating a proper color tuple with RGB and alpha values
            r, g, b = particle['colour']
            particle_colour = pygame.Color(r, g, b, alpha)
            pygame.draw.circle(
                surface, 
                particle_colour, 
                (int(particle['x']), int(particle['y'])), 
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )
        
        # Draw the game over panel
        self.game_over_panel.draw(surface)
        
        # Draw result title with appropriate styling
        if self.game_manager.game_data["victory"]:
            result_text = self.title_font.render("VICTORY!", True, (180, 255, 180))
            subtitle_text = self.header_font.render("You have conquered the dungeon", True, WHITE)
        else:
            result_text = self.title_font.render("DEFEATED", True, (255, 180, 180))
            subtitle_text = self.header_font.render("Your adventure ends here...", True, WHITE)
        
        # Position and draw titles
        result_rect = result_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.game_over_panel.rect.top + 32)
        surface.blit(result_text, result_rect)
        
        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=result_rect.bottom + 20)
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw game statistics - move up by 10 pixels
        stats_y = subtitle_rect.bottom + 25  # Reduced from 50 to 40
        
        floors_text = self.body_font.render(
            f"Floors Completed: {self.game_manager.floor_manager.current_floor_index}",
            True, WHITE
        )
        floors_rect = floors_text.get_rect(centerx=SCREEN_WIDTH//2, top=stats_y)
        surface.blit(floors_text, floors_rect)
        
        gold_text = self.body_font.render(
            f"Gold Acquired: {self.game_manager.player_gold}",
            True, (255, 230, 150)  # Gold colour
        )
        gold_rect = gold_text.get_rect(centerx=SCREEN_WIDTH//2, top=floors_rect.bottom + 15)
        surface.blit(gold_text, gold_rect)
        
        # Draw buttons
        if self.restart_button:
            self.restart_button.draw(surface)
        
        if self.title_button:
            self.title_button.draw(surface)