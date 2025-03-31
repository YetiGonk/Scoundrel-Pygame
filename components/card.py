""" Card component for the Scoundrel game with enhanced animation support. """
import pygame
import math
from constants import CARD_WIDTH, CARD_HEIGHT, CARD_RED, BLACK, FONTS_PATH
from utils.resource_loader import ResourceLoader
from roguelike_constants import FLOOR_MONSTERS

class Card:
    """ Represents a card in the game with support for rotation and scaling. """
    
    def __init__(self, suit, value, floor_type="dungeon"):
        self.suit = suit
        self.value = value
        self.type = self.determine_type()
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.is_hovered = False
        # Basic properties
        self.is_flipping = False
        self.face_up = False
        self.z_index = 0
        self.is_visible = True  # Controls card visibility for effects
        self.floor_type = floor_type
        
        # Animation properties
        self.rotation = 0  # Degrees
        self.scale = 1.0
        
        # Load the card texture
        if self.value > 14:
            texture = ResourceLoader.load_image(
                f"cards/joker_{"black" if self.suit in ("clubs", "spades") else "red"}_{self.value}.png"
            )
        else:
            texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")
            
        # If this is a monster card (spades or clubs), add monster image and name
        if self.type == "monster" and self.value >= 2 and self.value <= 17:
            texture = self.add_monster_to_card(texture)
            
        self.texture = pygame.transform.scale(texture, (self.width, self.height))
        self.original_texture = self.texture
        
        # Load face down texture
        self.face_down_texture = pygame.transform.scale(
            ResourceLoader.load_image("cards/card_back.png"), 
            (self.width, self.height)
        )
        self.original_face_down_texture = self.face_down_texture
        
        # Flip animation properties
        self.flip_progress = 0.0  # 0.0 to 1.0
        self.is_flipping = False
        self.face_up = False
        self.lift_height = 20  # How high the card lifts during flip
        self.original_y = 0  # Original y position for reference
    
    def add_monster_to_card(self, card_surface):
        """Add monster image and name to card surface based on suit, value and floor type"""
        # Get monster data from roguelike_constants
        try:
            monster_data = FLOOR_MONSTERS[self.floor_type][self.suit][self.value]
        except KeyError:
            # No monster defined for this card
            return card_surface
            
        monster_name = monster_data["name"].upper()
        monster_image_path = monster_data["image"]
        
        # Create a new surface based on the card surface
        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))
                
        # Load, resize, and recolor monster image
        monster_img = ResourceLoader.load_image(monster_image_path, cache=False)
        
        # Scale monster from 32x32 to 96x96
        monster_size = 96
        monster_img = pygame.transform.scale(monster_img, (monster_size, monster_size))
        
        # Recolor the monster using pygame surfaces
        monster_surface = pygame.Surface((monster_size, monster_size), pygame.SRCALPHA)
        for y in range(monster_size):
            for x in range(monster_size):
                color = monster_img.get_at((x, y))
                # If not transparent (alpha > 0) and not white, apply the suit color
                if color.r == 255 and color.g == 255 and color.b == 255 and color.a > 0:
                    monster_surface.set_at((x, y), pygame.Color(0, 0, 0, 255))

        # Calculate center position to place the monster
        monster_pos = ((card_width - monster_size) // 2, (card_height - monster_size) // 2)
        
        # Blit monster onto the card
        new_surface.blit(monster_surface, monster_pos)
        
        # Load font for monster name
        font_size = 16
        try:
            font = pygame.font.Font(FONTS_PATH + "/Pixel Times.ttf", font_size)
        except:
            # Fallback to default font if custom font not found
            font = pygame.font.SysFont(None, font_size)
        
        text_surface = None
        text_rect = None
        
        # Render monster name
        if len(monster_name) > 10 and " " in monster_name:
            # Split monster name to fit within the card width
            monster_name = monster_name.split(" ")
            for i, word in enumerate(monster_name):
                text_surface = font.render(word, True, BLACK)
                text_rect = text_surface.get_rect(center=(card_width // 2, monster_pos[1] + monster_size + 10 + i * 20))
        else:
            text_surface = font.render(monster_name, True, BLACK)
            text_rect = text_surface.get_rect(center=(card_width // 2, monster_pos[1] + monster_size + 10))
        
        # Blit name onto the card
        new_surface.blit(text_surface, text_rect)
        
        return new_surface
    
    def determine_type(self):
        if self.suit in ["spades", "clubs"]:
            return "monster"
        elif self.suit == "diamonds":
            return "weapon"
        elif self.suit == "hearts":
            return "potion"
        return "unknown"
    
    def update_position(self, pos):
        self.rect.topleft = (int(pos[0]), int(pos[1]))
        if not self.is_flipping:
            self.original_y = int(pos[1])
    
    def start_flip(self):
        self.is_flipping = True
        self.flip_progress = 0.0
        self.original_y = self.rect.y
    
    def update_flip(self, delta_time):
        if self.is_flipping:
            # Progress the flip animation
            flip_speed = 2  # Speed multiplier
            self.flip_progress += delta_time * flip_speed
            
            if self.flip_progress >= 1.0:
                # Finished flipping
                self.flip_progress = 1.0
                self.is_flipping = False
                self.face_up = True
                self.rect.y = self.original_y  # Reset y position
            else:
                # Calculate the y position (lifting effect)
                if self.flip_progress < 0.5:
                    # First half: lift up
                    lift_amount = self.lift_height * (self.flip_progress * 2)
                else:
                    # Second half: come back down
                    lift_amount = self.lift_height * (1 - (self.flip_progress - 0.5) * 2)
                
                # Update y position for lift effect
                self.rect.y = self.original_y - lift_amount
    
    def rotate(self, angle):
        """Rotate the card textures"""
        self.rotation = angle
        
        # Only rotate if angle is not close to 0
        if abs(angle) > 0.1:
            # Rotate both textures
            self.texture = pygame.transform.rotate(self.original_texture, angle)
            self.face_down_texture = pygame.transform.rotate(self.original_face_down_texture, angle)
            
            # Update rect size for rotated texture
            self.rect.width = self.texture.get_width()
            self.rect.height = self.texture.get_height()
        else:
            # Reset to original textures
            self.texture = self.original_texture.copy()
            self.face_down_texture = self.original_face_down_texture.copy()
            self.rect.width = self.width
            self.rect.height = self.height
    
    def update_scale(self, scale):
        """Update the card scale"""
        if abs(scale - 1.0) < 0.01:
            # Reset to original size
            self.texture = self.original_texture.copy()
            self.face_down_texture = self.original_face_down_texture.copy()
            self.rect.width = self.width  
            self.rect.height = self.height
        else:
            # Scale the textures
            new_width = int(self.width * scale)
            new_height = int(self.height * scale)
            
            if new_width > 0 and new_height > 0:
                self.texture = pygame.transform.scale(self.original_texture, (new_width, new_height))
                self.face_down_texture = pygame.transform.scale(self.original_face_down_texture, (new_width, new_height))
                
                # Update rect size
                self.rect.width = new_width
                self.rect.height = new_height
        
        self.scale = scale
    
    def draw(self, surface):
        # Skip drawing if card isn't visible (for destruction animations)
        if not self.is_visible:
            return
            
        if self.is_flipping:
            # Existing flip animation code
            # Draw shadow as a greyed card behind the main card
            shadow_offset_x = 15  # Horizontal offset
            shadow_offset_y = 15  # Vertical offset
            
            # Calculate the shadow position based on lift height
            if self.flip_progress < 0.5:
                # First half: shadow moves away as card lifts
                shadow_offset_x *= self.flip_progress * 2
                shadow_offset_y = 15  # Keep y offset constant
            else:
                # Second half: shadow moves back as card returns
                shadow_offset_x *= 2 - self.flip_progress * 2
                shadow_offset_y = 15  # Keep y offset constant
            
            # Shadow gets more transparent during highest lift point
            shadow_alpha = 120
            if self.flip_progress < 0.5:
                shadow_alpha = 120 - self.flip_progress * 80
            else:
                shadow_alpha = 80 + (self.flip_progress - 0.5) * 80
            
            # Create a greyed version of the current texture for shadow
            shadow_texture = None
            if self.flip_progress < 0.5:
                shadow_texture = self.face_down_texture.copy()
            else:
                shadow_texture = self.texture.copy()
            
            # Create shadow surface with transparency
            shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Calculate card width based on flip progress (same as main card)
            scaled_width = self.width
            if self.flip_progress < 0.5:
                # First half of flip: card gets narrower
                scaled_width = self.width * (1 - self.flip_progress * 2)
            else:
                # Second half of flip: card gets wider
                scaled_width = self.width * ((self.flip_progress - 0.5) * 2)
            
            # Only draw shadow if the card has some width
            if scaled_width > 1:
                # Scale the shadow texture
                scaled_shadow = pygame.transform.scale(shadow_texture, (int(scaled_width), self.height))
                
                # Convert scaled texture to greyscale and with transparency
                for x in range(scaled_shadow.get_width()):
                    for y in range(scaled_shadow.get_height()):
                        color = scaled_shadow.get_at((x, y))
                        grey = (color[0] + color[1] + color[2]) // 3
                        scaled_shadow.set_at((x, y), (30, 30, 30, shadow_alpha))  # Dark grey with transparency
                
                # Adjust x position to keep shadow centered during scaling
                x_offset = (self.width - scaled_width) / 2
                
                # Draw shadow behind the card
                surface.blit(scaled_shadow, (self.rect.x + x_offset + shadow_offset_x, 
                                            self.rect.y + shadow_offset_y))
            
            # Now draw the main card
            # Calculate card width based on flip progress
            scaled_width = self.width
            if self.flip_progress < 0.5:
                # First half of flip: card gets narrower
                scaled_width = self.width * (1 - self.flip_progress * 2)
            else:
                # Second half of flip: card gets wider
                scaled_width = self.width * ((self.flip_progress - 0.5) * 2)
            
            # Determine which texture to show
            if self.flip_progress < 0.5:
                # First half: face down
                texture = self.face_down_texture
            else:
                # Second half: face up
                texture = self.texture
            
            # Only draw if the card has some width
            if scaled_width > 1:
                # Scale the texture to the current width
                scaled_card = pygame.transform.scale(texture, (int(scaled_width), self.height))
                
                # Adjust x position to keep card centered during scaling
                x_offset = (self.width - scaled_width) / 2
                surface.blit(scaled_card, (self.rect.x + x_offset, self.rect.y))
        else:
            # Normal drawing (either face up or face down) with rotation support
            current_texture = self.texture if self.face_up else self.face_down_texture
            
            # Calculate the center position for rotated or scaled cards
            # This ensures the card rotates around its center
            center_x = self.rect.x + self.rect.width / 2
            center_y = self.rect.y + self.rect.height / 2
            
            # Calculate the top-left position for drawing
            pos_x = center_x - current_texture.get_width() / 2
            pos_y = center_y - current_texture.get_height() / 2
            
            # Draw the card at the calculated position
            surface.blit(current_texture, (pos_x, pos_y))

    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        
        # Adjust for rotation if needed
        if abs(self.rotation) > 0.1 or abs(self.scale - 1.0) > 0.01:
            # For rotated/scaled cards, use distance-based collision detection
            center_x = self.rect.x + self.rect.width / 2
            center_y = self.rect.y + self.rect.height / 2
            
            # Calculate distance from mouse to card center
            dx = mouse_pos[0] - center_x
            dy = mouse_pos[1] - center_y
            
            # Get effective radius (half of diagonal)
            radius = math.sqrt((self.width * self.scale / 2) ** 2 + (self.height * self.scale / 2) ** 2)
            
            # Check if mouse is within the radius
            distance = math.sqrt(dx * dx + dy * dy)
            self.is_hovered = distance <= radius
        else:
            # For normal cards, use rect collision
            self.is_hovered = self.rect.collidepoint(mouse_pos)
            
        return previous_hover != self.is_hovered