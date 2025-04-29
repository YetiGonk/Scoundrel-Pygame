""" 
Title State for the Scoundrel game with atmospheric dungeon aesthetic.
"""
import pygame
import random
import math
from pygame.locals import *

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, DARK_GRAY,
    PANEL_BORDER_RADIUS, PANEL_ALPHA, PANEL_BORDER_WIDTH,
    GOLD_COLOR, GOLD_BORDER
)
from states.game_state import GameState
from ui.panel import Panel
from ui.button import Button
from utils.resource_loader import ResourceLoader

class TitleState(GameState):
    """The atmospheric title screen state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        # Fonts
        self.title_font = None
        self.subtitle_font = None
        self.body_font = None
        
        # Visual elements
        self.background = None
        self.floor = None
        self.title_panel = None
        self.start_button = None
        self.rules_button = None
        
        # Animation elements
        self.particles = []
        self.torch_lights = []
        self.title_glow = 0
        self.title_glow_dir = 1
        
        # Cards for visual effect
        self.cards = []
        self.card_images = {}
        
        # Easter egg - tagline cycling with weighted selection
        self.title_clicks = 0
        self.last_click_count = 0
        self.last_tagline_index = -1  # Start with no previous tagline
        self.seen_taglines = set()  # Keep track of which taglines have been seen
    
    def enter(self):
        # Make sure floor manager is initialised
        if not self.game_manager.floor_manager.floors:
            self.game_manager.floor_manager.initialise_run()
            
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 72)
        self.subtitle_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load a random floor image for visual variety
        from constants import FLOOR_WIDTH, FLOOR_HEIGHT
        from roguelike_constants import FLOOR_TYPES
        import random
        
        # Select a random floor type for the title screen
        random_floor_type = random.choice(FLOOR_TYPES)
        floor_image = f"floors/{random_floor_type}_floor.png"
        
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        # Create title panel
        panel_width = 800
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        self.title_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 30),  # Dark stone colour
            alpha=230,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=(120, 100, 80)  # Gold-ish border
        )
        
        # Create buttons with dungeon styling
        button_width = 300
        button_height = 60
        button_spacing = 10
        buttons_y = panel_y + panel_height - button_height*4 - button_spacing*3 - 25
        
        # Start button (top)
        start_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y,
            button_width, 
            button_height
        )
        self.start_button = Button(
            start_button_rect,
            "START ADVENTURE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(80, 40, 40),  # Dark red
            border_colour=(150, 70, 70)  # Brighter red border
        )
        
        
        # Delving deck button (below start)
        delving_deck_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing),
            button_width, 
            button_height
        )
        self.delving_deck_button = Button(
            delving_deck_rect,
            "DELVING DECK",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 80, 40),  # Dark green
            border_colour=(120, 160, 80)  # Brighter green border
        )
        
        # Rules button (below delving deck)
        rules_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing) * 2,
            button_width, 
            button_height
        )
        self.rules_button = Button(
            rules_button_rect,
            "GAME RULES",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 60, 80),  # Dark blue
            border_colour=(80, 120, 160)  # Brighter blue border
        )
        
        # Initialise torch lights
        self._create_torch_lights()
        
        # Initialise animated cards
        self._load_card_images()
        self._create_animated_cards()
    
    def _create_torch_lights(self):
        """Create torch light effects around the title screen"""
        self.torch_lights = []
        
        # Add torches along the sides
        for y_pos in [0.3, 0.7]:
            # Left torch
            self.torch_lights.append({
                'x': SCREEN_WIDTH * 0.15,
                'y': SCREEN_HEIGHT * y_pos,
                'radius': 100,
                'flicker': 0,
                'flicker_speed': random.uniform(0.1, 0.2),
                'colour': (255, 150, 50)  # Orange-ish
            })
            
            # Right torch
            self.torch_lights.append({
                'x': SCREEN_WIDTH * 0.85,
                'y': SCREEN_HEIGHT * y_pos,
                'radius': 100,
                'flicker': random.uniform(0, 2 * math.pi),
                'flicker_speed': random.uniform(0.1, 0.2),
                'colour': (255, 150, 50)
            })
    
    def _load_card_images(self):
        """Load a selection of card images for visual effect"""
        self.card_images = {}
        
        # Load a small selection of spades (monsters)
        for value in [10, 11, 13]:
            key = f"spades_{value}"
            self.card_images[key] = ResourceLoader.load_image(f"cards/spades_{value}.png")
        
        # Load a small selection of diamonds (weapons)
        for value in [5, 9, 12]:
            key = f"diamonds_{value}"
            self.card_images[key] = ResourceLoader.load_image(f"cards/diamonds_{value}.png")
        
        # Load a small selection of hearts (potions)
        for value in [4, 7, 14]:
            key = f"hearts_{value}"
            self.card_images[key] = ResourceLoader.load_image(f"cards/hearts_{value}.png")
        
        # Load the card back
        self.card_images["card_back"] = ResourceLoader.load_image("cards/card_back.png")
    
    def _create_animated_cards(self, num_cards=8):
        """Create animated cards that float around the title screen
        
        Args:
            num_cards: Number of cards to create. Default is 8 for initial creation.
                       When called later to add single cards, this is not specified.
        """
        # Clear existing cards only on first initialization
        if len(self.cards) == 0:
            self.cards = []
            card_count = num_cards
        else:
            # Just add a single card when called during updates
            card_count = 1
        
        for _ in range(card_count):
            card_keys = list(self.card_images.keys())
            card_key = random.choice(card_keys[:-1])  # Don't select card_back from initial cards
            
            # Parameters for movement
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.2, 0.5)
            
            # Starting position (off-screen)
            if random.random() < 0.5:
                # Start from outside the left/right edges
                x = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                y = random.uniform(100, SCREEN_HEIGHT - 100)
            else:
                # Start from outside the top/bottom edges
                x = random.uniform(100, SCREEN_WIDTH - 100)
                y = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100
            
            # Card data
            self.cards.append({
                'image': self.card_images[card_key],
                'x': x,
                'y': y,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-0.5, 0.5),
                'scale': random.uniform(0.7, 1.0),  # Increased scale from 0.5-0.8 to 0.7-1.0
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'shown': False,  # Initially face down
                'flip_progress': 0,  # 0 = back, 1 = front
                'flip_speed': random.uniform(0.02, 0.04),
                'flip_direction': 1,  # 1 = flipping to front, -1 = flipping to back
                'front_image': self.card_images[card_key],
                'back_image': self.card_images["card_back"],
                'dragging': False,  # Whether card is being dragged
                'drag_offset_x': 0,  # Offset from drag point to card center
                'drag_offset_y': 0,
                'z_index': random.random(),  # For layering when dragging
                'hover': False    # Whether mouse is hovering over card
            })
    
    def _add_particle(self, x, y, colour=(255, 215, 0)):
        """Add a particle effect at the specified position"""
        self.particles.append({
            'x': x,
            'y': y,
            'colour': colour,
            'size': random.uniform(1, 3),
            'life': 1.0,  # Full life
            'decay': random.uniform(0.005, 0.02),
            'dx': random.uniform(-0.7, 0.7),
            'dy': random.uniform(-0.7, 0.7)
        })
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check for card dragging first
            card_clicked = False
            
            # Sort cards by z-index to handle topmost cards first
            sorted_cards = sorted(self.cards, key=lambda card: card['z_index'], reverse=True)
            
            for card in sorted_cards:
                # Calculate card rect for collision detection
                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )
                
                # Expand collision area slightly to make it easier to grab
                expanded_rect = card_rect.inflate(20, 20)
                
                if expanded_rect.collidepoint(mouse_pos):
                    # This card was clicked - start dragging
                    card['dragging'] = True
                    card['drag_offset_x'] = card['x'] - mouse_pos[0]
                    card['drag_offset_y'] = card['y'] - mouse_pos[1]
                    
                    # Move this card to the top (highest z-index)
                    card['z_index'] = max([c['z_index'] for c in self.cards]) + 0.1
                    
                    # If card is face down, flip it when clicked
                    if not card['shown']:
                        card['flip_direction'] = 1
                    
                    card_clicked = True
                    break  # Only drag one card at a time
            
            # Only process button clicks if no card was clicked
            if not card_clicked:
                # Check for button clicks
                if self.start_button.is_clicked(mouse_pos):
                    # Initialise a new roguelike run
                    self.game_manager.start_new_run()
                    
                    # Go directly to playing state, skipping rules screen
                    self.game_manager.change_state("playing")
                    
                    # Set the rules as seen for any future logic that might need it
                    if not hasattr(self.game_manager, 'has_shown_rules'):
                        self.game_manager.has_shown_rules = True
                elif self.delving_deck_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("delving_deck")
                elif self.rules_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("rules")
                    
                # Check if title area was clicked (for easter egg)
                # Make the clickable area larger to cover title, subtitle and tagline
                title_rect = pygame.Rect(
                    (SCREEN_WIDTH - 600) // 2,  # Wider
                    self.title_panel.rect.top + 40,  # Slightly higher
                    600,  # Wider clickable area
                    150   # Taller to include subtitle and tagline
                )
                if title_rect.collidepoint(mouse_pos):
                    self.title_clicks += 1
                    
                    # Add particles around click area
                    for _ in range(10):
                        self._add_particle(mouse_pos[0], mouse_pos[1], (255, 200, 50))
        
        elif event.type == MOUSEBUTTONUP and event.button == 1:  # Left button release
            # Stop dragging all cards
            for card in self.cards:
                if card['dragging']:
                    card['dragging'] = False
                    
                    # Add a small random movement after releasing
                    speed_factor = 0.2
                    card['dx'] = random.uniform(-0.5, 0.5) * speed_factor
                    card['dy'] = random.uniform(-0.5, 0.5) * speed_factor
        
        elif event.type == MOUSEMOTION:
            # Move cards that are being dragged
            for card in self.cards:
                if card['dragging']:
                    card['x'] = mouse_pos[0] + card['drag_offset_x']
                    card['y'] = mouse_pos[1] + card['drag_offset_y']
                    
                    # Disable natural movement while dragging
                    card['dx'] = 0
                    card['dy'] = 0
            
            # Update card hover states
            for card in self.cards:
                # Calculate card rect
                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )
                
                # Expanded rect for easier interaction
                expanded_rect = card_rect.inflate(20, 20)
                card['hover'] = expanded_rect.collidepoint(mouse_pos)
        
        # Update button hover states - only if no card is under the cursor
        card_under_cursor = any(card['hover'] for card in self.cards)
        if not card_under_cursor:
            self.start_button.check_hover(mouse_pos)
            self.delving_deck_button.check_hover(mouse_pos)
            self.rules_button.check_hover(mouse_pos)
        else:
            # Force non-hover state for buttons when a card is under cursor
            self.start_button.hovered = False
            self.delving_deck_button.hovered = False
            self.rules_button.hovered = False
    
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
    
    def _update_torch_lights(self, delta_time):
        """Update the torch light effects"""
        for torch in self.torch_lights:
            torch['flicker'] += torch['flicker_speed']
            
            # Add occasional particles
            if random.random() < 0.1:
                ember_x = torch['x'] + random.uniform(-5, 5)
                ember_y = torch['y'] + random.uniform(-5, 5)
                ember_colour = (
                    min(255, torch['colour'][0] + random.randint(-20, 20)),
                    min(255, torch['colour'][1] + random.randint(-30, 10)),
                    min(255, torch['colour'][2] + random.randint(-20, 10))
                )
                self._add_particle(ember_x, ember_y, ember_colour)
    
    def _update_cards(self, delta_time):
        """Update the animated cards"""
        # Movement and rotation
        for card in self.cards:
            # Skip movement updates for cards being dragged
            if card['dragging']:
                continue
                
            # Move the card
            card['x'] += card['dx']
            card['y'] += card['dy']
            
            # Rotate the card (slower rotation if hovering)
            if card['hover']:
                card['rotation'] += card['rot_speed'] * 0.3
            else:
                card['rotation'] += card['rot_speed']
            
            # Flip animation
            if card['flip_progress'] < 1 and card['flip_direction'] > 0:
                card['flip_progress'] += card['flip_speed']
                if card['flip_progress'] >= 1:
                    card['flip_progress'] = 1
                    card['shown'] = True
            elif card['flip_progress'] > 0 and card['flip_direction'] < 0:
                card['flip_progress'] -= card['flip_speed']
                if card['flip_progress'] <= 0:
                    card['flip_progress'] = 0
                    card['shown'] = False
            
            # Reset if off-screen (only if not being dragged)
            if (card['x'] < -150 or card['x'] > SCREEN_WIDTH + 150 or
                card['y'] < -150 or card['y'] > SCREEN_HEIGHT + 150):
                
                # Reposition to a random edge
                if random.random() < 0.5:
                    # Start from outside the left/right edges
                    card['x'] = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                    card['y'] = random.uniform(100, SCREEN_HEIGHT - 100)
                else:
                    # Start from outside the top/bottom edges
                    card['x'] = random.uniform(100, SCREEN_WIDTH - 100)
                    card['y'] = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100
                
                # Reset card to back face
                card['shown'] = False
                card['flip_progress'] = 0
                
                # New random direction
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 0.5)
                card['dx'] = math.cos(angle) * speed
                card['dy'] = math.sin(angle) * speed
                
                # New random rotation
                card['rot_speed'] = random.uniform(-0.5, 0.5)
                
                # Random new card face
                card_keys = list(self.card_images.keys())
                card_key = random.choice(card_keys[:-1])  # Don't select card_back
                card['front_image'] = self.card_images[card_key]
            
            # Start flipping if entering visible area and not already flipping
            if (100 < card['x'] < SCREEN_WIDTH - 100 and
                100 < card['y'] < SCREEN_HEIGHT - 100 and
                not card['shown'] and card['flip_progress'] == 0):
                card['flip_direction'] = 1
        
        # Randomly add new cards if we have fewer than the initial amount
        if len(self.cards) < 8 and random.random() < 0.01:  # Changed from 5 to 8 to match increased card count
            self._create_animated_cards()
    
    def update(self, delta_time):
        # Update title glow effect
        glow_speed = 0.5
        self.title_glow += glow_speed * self.title_glow_dir * delta_time
        if self.title_glow >= 1.0:
            self.title_glow = 1.0
            self.title_glow_dir = -1
        elif self.title_glow <= 0.0:
            self.title_glow = 0.0
            self.title_glow_dir = 1
        
        # Update particles
        self._update_particles(delta_time)
        
        # Update torch lights
        self._update_torch_lights(delta_time)
        
        # Update animated cards
        self._update_cards(delta_time)
        
        # Add occasional ambient particles
        if random.random() < 0.05:
            x = random.uniform(self.title_panel.rect.left + 50, self.title_panel.rect.right - 50)
            y = random.uniform(self.title_panel.rect.top + 50, self.title_panel.rect.bottom - 50)
            self._add_particle(x, y)
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw torch light effects (glow behind everything)
        for torch in self.torch_lights:
            # Create a surface for the glow
            glow_size = int(torch['radius'] * 2 * (1 + 0.1 * math.sin(torch['flicker'])))
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Draw gradient glow
            for r in range(glow_size//2, 0, -1):
                alpha = max(0, int(90 * r / (glow_size//2) * (0.8 + 0.2 * math.sin(torch['flicker']))))
                pygame.draw.circle(
                    glow_surface, 
                    (*torch['colour'], alpha), 
                    (glow_size//2, glow_size//2), 
                    r
                )
            
            # Position and draw the glow
            glow_rect = glow_surface.get_rect(center=(torch['x'], torch['y']))
            surface.blit(glow_surface, glow_rect)
        
        # Draw floor
        floor_x = (SCREEN_WIDTH - self.floor.get_width()) // 2
        floor_y = (SCREEN_HEIGHT - self.floor.get_height()) // 2
        surface.blit(self.floor, (floor_x, floor_y))
        
        # Draw animated cards (behind the panel)
        # Sort cards by z-index for proper layering
        sorted_cards = sorted(self.cards, key=lambda card: card['z_index'])
        
        for card in sorted_cards:
            # Calculate width for flip animation (to give 3D effect)
            flip_width = int(card['image'].get_width() * card['scale'] * abs(math.cos(card['flip_progress'] * math.pi)))
            if flip_width < 1:
                flip_width = 1  # Prevent zero width
            
            # Create a surface for the card
            card_height = int(card['image'].get_height() * card['scale'])
            card_surface = pygame.Surface((flip_width, card_height), pygame.SRCALPHA)
            
            # Choose the correct image based on flip progress
            if card['flip_progress'] < 0.5:
                # Back of card still showing
                image = pygame.transform.scale(
                    card['back_image'], 
                    (flip_width, card_height)
                )
            else:
                # Front of card showing
                image = pygame.transform.scale(
                    card['front_image'], 
                    (flip_width, card_height)
                )
            
            # Blit the image onto the card surface
            card_surface.blit(image, (0, 0))
            
            # Draw highlight effect if card is being hovered or dragged
            if card['hover'] or card['dragging']:
                # Create a highlight border
                highlight_rect = pygame.Rect(0, 0, flip_width, card_height)
                pygame.draw.rect(
                    card_surface, 
                    (255, 215, 0) if card['dragging'] else (180, 180, 255),  # Gold if dragging, blue if hovering
                    highlight_rect, 
                    width=3,
                    border_radius=3
                )
                
                # Add some particles if dragging
                if card['dragging'] and random.random() < 0.05:
                    self._add_particle(card['x'] + random.uniform(-20, 20), 
                        card['y'] + random.uniform(-30, 30), 
                        (255, 215, 0))
            
            # Rotate the card
            rotated_card = pygame.transform.rotate(card_surface, card['rotation'])
            
            # Position and draw the card
            card_rect = rotated_card.get_rect(center=(card['x'], card['y']))
            surface.blit(rotated_card, card_rect)
        
        # Draw the title panel
        self.title_panel.draw(surface)
        
        # Draw title with glow effect
        glow_intensity = int(40 + 30 * self.title_glow)
        glow_colour = (255, 200, 50, glow_intensity)  # Gold with varying alpha
        
        title_text = self.title_font.render("SCOUNDREL", True, WHITE)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.title_panel.rect.top + 50)
        
        # Create glow surface
        glow_size = 15
        glow_surface = pygame.Surface((title_text.get_width() + glow_size*2, title_text.get_height() + glow_size*2), pygame.SRCALPHA)
        
        # Draw radial gradient
        for r in range(glow_size, 0, -1):
            alpha = int(glow_colour[3] * r / glow_size)
            pygame.draw.rect(
                glow_surface, 
                (*glow_colour[:3], alpha), 
                pygame.Rect(glow_size-r, glow_size-r, title_text.get_width()+r*2, title_text.get_height()+r*2),
                border_radius=10
            )
        
        # Apply glow and text
        glow_rect = glow_surface.get_rect(center=title_rect.center)
        surface.blit(glow_surface, glow_rect)
        surface.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.subtitle_font.render("The 52-Card Dungeon Crawler", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 40)
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw tagline/description (random when clicked)
        taglines = [
            "Navigate with cunning, defeat with paper cuts", # first tagline shown
            "In darkened halls where cards may fall...",
            "Fortune favours the card counters",
            "Excitement!",
            "It's just a flesh wound!",
            "One more room couldn't hurt...",
            "What's in the cards for you, adventurer?",
            "Rooms of whimsy and peril!",
            "Dungeons and dragons and cards and counting!",
            "Kill it with a fire card!",
            "Crossbows are useless without bolts!",
            "Better lucky than good, better prepared than lucky",
            "Don't give up! You can always draw another card!",
            "[Insert sponsor here]",
            "The dungeon is a cruel mistress",
            "Insanity is expecting a different result from the same card",
            "Exodia!!!",
            "Read the rules if you're a chump!",
            "The real scoundrel was the friends we made along the way!",
            "r/scoundrelthegame",
            "Some treasures are worth the papercuts...",
            "52 card pickup!",
            "Another day, another dungeon...",
            "Shuffle up and deal with it!",
            "Card games are a gamble, but this is a dungeon!",
            "Flipping you off is a card game term!",
            "Original concept by Kurt Bieg and Zach Gage!",
            "You are not allowed a calculator on this exam",
            "Scoundrel this, scoundrel that",
            "Trust in the heart of the cards...",
            "When in doubt, run away!",
            "If only I were a scoundrel...",
            "This dungeon is definitely not up to code",
            "Terms and conditions apply to all card effects",
            "Don't bring a card to a sword fight!",
            "You fell for the classic blunder!",
            "You can't cheat death, but you can shuffle the deck",
            "A wise scoundrel knows when to hold 'em and when to fold 'em",
            "I believe in you... sort of",
            "I feel like we are connecting on a deeper level through these title screen taglines...",
            "PyGame is a cruel mistress",
            "Scoundrel, shmoundrel!",
            "Roguelike or roguelite? You decide!",
            "Scoundrel 2: Electric Boogaloo",
            "Sconedrel: Argue about how to pronounce it.",
            "SCOUNDRELLLLL!",
            "The sequel will be a dating sim."
        ]
        
        # Choose random tagline with weighted selection favoring unseen taglines
        if not hasattr(self, 'last_tagline_index'):
            self.last_tagline_index = -1
            
        # If tagline was just clicked, choose a new random one
        if self.title_clicks > 0 and hasattr(self, 'last_click_count') and self.title_clicks > self.last_click_count:
            # Get indices of all taglines that are not the last one shown
            available_indices = [i for i in range(len(taglines)) if i != self.last_tagline_index]
            
            # Reset seen taglines if all have been seen
            if len(self.seen_taglines) >= len(taglines) - 1:  # -1 because we don't count the current tagline
                self.seen_taglines = {self.last_tagline_index}  # Keep only the current one as seen
            
            # Split available indices into seen and unseen
            unseen_indices = [i for i in available_indices if i not in self.seen_taglines]
            seen_indices = [i for i in available_indices if i in self.seen_taglines]
            
            # Choose with weighted probability: 
            # 80% chance to pick from unseen if available, 20% chance for seen ones
            if unseen_indices and (not seen_indices or random.random() < 0.8):
                self.last_tagline_index = random.choice(unseen_indices)
            else:
                self.last_tagline_index = random.choice(seen_indices or available_indices)
            
            # Add the chosen tagline to seen list
            self.seen_taglines.add(self.last_tagline_index)
            
        # Store current click count for next comparison
        self.last_click_count = self.title_clicks
            
        # Use a default starting tagline if not clicked yet
        if self.title_clicks == 0:
            # Start with a welcoming tagline
            tagline = taglines[0]
        else:
            tagline = taglines[self.last_tagline_index]
        
        # Determine if the tagline needs to be split into multiple lines
        max_width = 550  # Maximum width for a tagline before wrapping
        
        # Render the tagline to check its width
        test_text = self.body_font.render(tagline, True, (200, 200, 200))
        
        # If the tagline is too long, split it into two lines
        if test_text.get_width() > max_width:
            # Find a good breaking point near the middle
            words = tagline.split()
            total_words = len(words)
            middle_point = total_words // 2
            
            # Try to find a natural breaking point around the middle
            # Start from middle and look for spaces before and after
            break_point = middle_point
            
            # First line with words up to the break point
            line1 = " ".join(words[:break_point])
            # Second line with words after the break point
            line2 = " ".join(words[break_point:])
            
            # Render both lines
            line1_text = self.body_font.render(line1, True, (200, 200, 200))
            line2_text = self.body_font.render(line2, True, (200, 200, 200))
            
            # Position and draw both lines
            line1_rect = line1_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 40)
            line2_rect = line2_text.get_rect(centerx=SCREEN_WIDTH//2, top=line1_rect.bottom + 5)
            
            surface.blit(line1_text, line1_rect)
            surface.blit(line2_text, line2_rect)
        else:
            # Single line rendering for shorter taglines
            tagline_text = self.body_font.render(tagline, True, (200, 200, 200))
            tagline_rect = tagline_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 25)
            surface.blit(tagline_text, tagline_rect)
        
        # Draw buttons
        self.start_button.draw(surface)
        self.delving_deck_button.draw(surface)
        self.rules_button.draw(surface)
        
        # Draw particle effects (on top of everything)
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            particle_colour = (*particle['colour'], alpha)
            pygame.draw.circle(
                surface, 
                particle_colour, 
                (int(particle['x']), int(particle['y'])), 
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )