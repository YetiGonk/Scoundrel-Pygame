""" Card component for the Scoundrel game with enhanced animation support. """
import pygame
import math
import random
from constants import CARD_WIDTH, CARD_HEIGHT, CARD_RED, BLACK, WHITE, DARK_GRAY, GOLD_COLOR, FONTS_PATH
from utils.resource_loader import ResourceLoader
from roguelike_constants import FLOOR_MONSTERS, WEAPON_DAMAGE_TYPES, WEAPON_MAPPINGS

class Card:
    """ Represents a card in the game with support for rotation and scaling. """
    
    @staticmethod
    def _to_roman(num):
        """Convert integer to Roman numeral"""
        if num == 0:
            return ""  # No roman numeral for zero
            
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num

    def _create_blank_card(self, suit):
        """Create a blank card texture with just the suit symbol (for non-valued cards)"""
        import pygame
        from constants import CARD_WIDTH, CARD_HEIGHT, WHITE, BLACK
        
        # Create a blank white card
        texture = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        texture.fill(WHITE)
        
        # Add a border
        pygame.draw.rect(texture, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 1)
        
        # Add the suit symbol
        suit_symbol = ""
        suit_color = BLACK
        if suit == "diamonds":
            suit_symbol = "♦"
            suit_color = (255, 0, 0)  # Red
        elif suit == "hearts":
            suit_symbol = "♥"
            suit_color = (255, 0, 0)  # Red
        elif suit == "spades":
            suit_symbol = "♠"
            suit_color = BLACK
        elif suit == "clubs":
            suit_symbol = "♣"
            suit_color = BLACK
            
        # Create a font object for the suit symbol
        suit_font = pygame.font.SysFont("arial", 40)
        suit_text = suit_font.render(suit_symbol, True, suit_color)
        
        # Draw the suit symbol in the center
        text_rect = suit_text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        texture.blit(suit_text, text_rect)
        
        # Add smaller suit symbols in the corners
        small_font = pygame.font.SysFont("arial", 20)
        small_text = small_font.render(suit_symbol, True, suit_color)
        
        # Top-left corner
        texture.blit(small_text, (5, 5))
        
        # Bottom-right corner (flip the symbol)
        flipped_text = pygame.transform.flip(small_text, True, True)
        texture.blit(flipped_text, (CARD_WIDTH - 25, CARD_HEIGHT - 25))
        
        return texture
    
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
        self.name = None  # Store card name for hover display
        
        # Card subtype properties
        self.weapon_type = None  # "melee" or "ranged" for weapons
        self.damage_type = None  # "piercing", "slashing", or "bludgeoning" for weapons
        self.monster_type = None  # D&D style monster type for monsters
        
        # Set name for potions and weapons using Roman numerals
        if self.type == "potion":
            self.name = f"Potion {self._to_roman(self.value)}"
        elif self.type == "weapon":
            # Weapon type will be set in add_weapon_to_card based on the weapon name
            # Initialize with a generic name that will be overridden later
            self.name = f"Weapon {self._to_roman(self.value)}"
        elif self.type == "monster":
            # Monster name will be set later in add_monster_to_card
            pass
        
        # Animation properties
        self.rotation = 0  # Degrees
        self.scale = 1.0
        
        # Idle hover animation properties
        self.idle_time = 0.0
        self.idle_float_speed = 1
        self.idle_float_amount = 6.0
        self.idle_float_offset = 0.0
        self.idle_phase_offset = 6.28 * random.random()  # Random starting phase (0-2π)
        
        # Hover animation properties
        self.hover_progress = 0.0
        self.hover_speed = 5.0  # How quickly card responds to hover
        self.hover_float_offset = 0.0
        self.hover_scale_target = 1.12  # Target scale when hovered (more pronounced)
        self.hover_lift_amount = 15.0  # How much to lift card when hovered (more pronounced)
        
        # Selection properties (for potions, weapons, and monsters)
        self.can_add_to_inventory = self.type in ["potion", "weapon"]
        self.can_show_attack_options = self.type in ["monster"]
        self.hover_selection = None  # "top" for inventory/weapon, "bottom" for use/bare-handed
        self.inventory_colour = (128, 0, 128, 100)  # Purple with transparency
        self.use_colour = (255, 165, 0, 100)  # Orange with transparency
        self.equip_colour = (0, 255, 0, 100)  # Green with transparency
        self.weapon_attack_colour = (0, 100, 200, 100)  # Blue with transparency (weapon attack)
        self.bare_hands_colour = (200, 50, 50, 100)  # Red with transparency (bare-handed attack)
        self.is_selected = False  # Track if the card has been clicked/selected
        self.icon_size = 50  # Size of the selection icons
        
        # Flags to track state (will be updated by the playing state)
        self.weapon_available = False     # For monsters: is weapon equipped?
        self.inventory_available = True   # For potions/weapons: is there inventory space?
        self.weapon_attack_not_viable = False  # For monsters: is weapon attack not viable based on last defeated monster?
        self.no_arrows = False  # For monsters: is weapon attack not viable due to no arrows?
        
        # Special handling for arrow cards (ranged ammo)
        if self.type == "weapon" and self.value == 0:  # 0 value diamonds is arrow
            self.weapon_type = "arrow"
            self.name = "Arrow"
        
        # Load the card texture - handle non-valued cards (value 0)
        if self.value == 0:
            # Use a special texture for non-valued cards
            # For arrow cards - use diamonds_0 if it exists, otherwise create a custom one
            try:
                texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")
            except:
                # Create a custom card texture for arrows
                # Use a base diamond card as template or create from scratch
                if self.suit == "diamonds":
                    # Try to load a template diamond card
                    try:
                        texture = ResourceLoader.load_image(f"cards/{self.suit}_14.png")  # Use ace of diamonds as template
                    except:
                        # Create a blank card with diamond suit symbol
                        texture = self._create_blank_card("diamonds")
                else:
                    texture = self._create_blank_card(self.suit)
        else:
            # Normal valued card
            texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")
            
        # If this is a monster card (spades or clubs), add monster image and name
        if self.type == "monster" and self.value >= 2 and self.value <= 14:
            texture = self.add_monster_to_card(texture)
        # If this is a weapon card (diamonds), add weapon image
        elif self.type == "weapon" and ((self.value >= 2 and self.value <= 14) or self.value == 0):
            texture = self.add_weapon_to_card(texture)
            
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
        """Add monster image to card surface based on suit, value and floor type"""
        # Get monster data from roguelike_constants
        try:
            monster_data = FLOOR_MONSTERS[self.floor_type][self.suit][self.value]
        except KeyError:
            # No monster defined for this card
            return card_surface
            
        # Store monster name for hover display
        self.name = f"{monster_data["name"]} {self._to_roman(self.value)}"
        
        # Determine monster type based on the name (D&D style types)
        monster_name = monster_data["name"].lower()
        
        # Assign monster type based on monster name keywords
        if any(creature in monster_name for creature in ["goblin", "knight", "soldier", "mage", "king", "merchant", "jester"]):
            self.monster_type = "Humanoid"
        elif any(creature in monster_name for creature in ["skeleton", "ghost", "wraith", "ghoul", "zombie", "lich"]):
            self.monster_type = "Undead"
        elif any(creature in monster_name for creature in ["dragon", "wyrm", "serpent"]):
            self.monster_type = "Dragon"
        elif any(creature in monster_name for creature in ["demon", "devil", "fiend", "shaman"]):
            self.monster_type = "Fiend"
        elif any(creature in monster_name for creature in ["golem", "armour", "sentinel", "totem"]):
            self.monster_type = "Construct"
        elif any(creature in monster_name for creature in ["ooze", "abomination", "medusa", "beholder", "eyes", "squid"]):
            self.monster_type = "Aberration"
        elif any(creature in monster_name for creature in ["elemental", "fire", "lightning"]):
            self.monster_type = "Elemental"
        elif any(creature in monster_name for creature in ["angel", "celestial"]):
            self.monster_type = "Celestial"
        elif any(creature in monster_name for creature in ["snail", "hornet", "crab", "adder", "python", "lizard", "gecko", "snake", "tarantula"]):
            self.monster_type = "Beast"
        elif any(creature in monster_name for creature in ["treant", "vine", "ent"]):
            self.monster_type = "Plant"
        else:
            # Default monster type if none of the above match
            self.monster_type = "Monstrosity"
        
        monster_image_path = monster_data["image"]
        
        # Create a new surface based on the card surface
        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))
                
        # Load, resize, and recolour monster image
        monster_img = ResourceLoader.load_image(monster_image_path, cache=False)
        
        # Scale monster from 32x32 to 96x96
        monster_size = 96
        monster_img = pygame.transform.scale(monster_img, (monster_size, monster_size))
        
        # Recolour the monster using pygame surfaces
        monster_surface = pygame.Surface((monster_size, monster_size), pygame.SRCALPHA)
        for y in range(monster_size):
            for x in range(monster_size):
                colour = monster_img.get_at((x, y))
                # If not transparent (alpha > 0) and not white, apply the suit colour
                if colour.r == 255 and colour.g == 255 and colour.b == 255 and colour.a > 0:
                    monster_surface.set_at((x, y), pygame.Color(0, 0, 0, 255))

        # Calculate center position to place the monster
        monster_pos = ((card_width - monster_size) // 2, (card_height - monster_size) // 2)
        
        # Blit monster onto the card
        new_surface.blit(monster_surface, monster_pos)
        
        return new_surface
        
    def add_weapon_to_card(self, card_surface):
        """Add weapon image to card surface based on value"""
        # Create a new surface based on the card surface
        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))
        
        # Default weapon in case value isn't in mapping
        weapon_name = WEAPON_MAPPINGS.get(self.value, "shortsword")
        
        # Determine weapon type based on the weapon name
        if weapon_name in ["crossbow", "longbow"]:
            self.weapon_type = "ranged"
        elif weapon_name == "arrow":
            self.weapon_type = "arrow"
        else:
            # All other weapons (warhammer, flail, shortsword, etc.) are melee
            self.weapon_type = "melee"
                
        # Set damage type based on weapon name
        self.damage_type = WEAPON_DAMAGE_TYPES.get(weapon_name, "piercing")
        
        # Set the card name based on the weapon
        if self.weapon_type == "arrow":
            self.name = "Arrow"
        else:
            # Convert the name to title case (first letter capitalized)
            weapon_display_name = weapon_name.capitalize()
            # Add Roman numeral suffix based on card value (like monsters and potions)
            self.name = f"{weapon_display_name} {self._to_roman(self.value)}"
        
        # Load weapon image
        weapon_path = f"weapons/{weapon_name}.png"
        try:
            weapon_img = ResourceLoader.load_image(weapon_path)
            
            # Scale weapon to appropriate size for the card
            weapon_size = 96  # Same size as monster images
            weapon_img = pygame.transform.scale(weapon_img, (weapon_size, weapon_size))
            
            # Calculate center position
            weapon_pos = ((card_width - weapon_size) // 2, (card_height - weapon_size) // 2)
            
            # Blit weapon onto the card
            new_surface.blit(weapon_img, weapon_pos)
            
        except Exception as e:
            print(f"Error loading weapon image: {e}")
            # Return original card if image can't be loaded
            return card_surface
            
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
    
    def update(self, delta_time):
        """Update card animations including idle float and hover effects."""
        # Update the idle hover animation
        self.idle_time += delta_time
        
        # For cards in inventory, use reduced floating animation (25% of normal)
        if hasattr(self, 'in_inventory') and self.in_inventory:
            self.idle_float_offset = math.sin(self.idle_time * self.idle_float_speed + self.idle_phase_offset) * (self.idle_float_amount * 0.25)
        else:
            self.idle_float_offset = math.sin(self.idle_time * self.idle_float_speed + self.idle_phase_offset) * self.idle_float_amount
        
        # Update hover animation
        target_hover = 1.0 if self.is_hovered else 0.0
        if abs(self.hover_progress - target_hover) > 0.01:
            # Gradually change hover progress towards target
            if self.hover_progress < target_hover:
                self.hover_progress = min(self.hover_progress + delta_time * self.hover_speed, target_hover)
            else:
                self.hover_progress = max(self.hover_progress - delta_time * self.hover_speed, target_hover)
            
            # Store current center position of the card before scaling
            center_x = self.rect.centerx
            center_y = self.rect.centery
            
            # Update scale based on hover progress
            base_scale = 0.8 if hasattr(self, 'in_inventory') and self.in_inventory else 1.0
            hover_scale_modifier = (self.hover_scale_target - 1.0) * self.hover_progress
            new_scale = base_scale + (base_scale * hover_scale_modifier)
            self.update_scale(new_scale)
            
            # Restore the card's center position after scaling
            self.rect.centerx = center_x
            self.rect.centery = center_y
            
            # For cards in inventory, use reduced hover lift (25% of normal)
            if hasattr(self, 'in_inventory') and self.in_inventory:
                self.hover_float_offset = self.hover_lift_amount * self.hover_progress * 0.25
            else:
                self.hover_float_offset = self.hover_lift_amount * self.hover_progress
    
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
        # Store the center position to maintain it after scaling
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        if abs(scale - 1.0) < 0.01:
            # Reset to original sizes
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
        
        # Update the scale property
        self.scale = scale
        
        # Preserve the center position
        # (Note: We don't directly set this here as the caller might want to handle positioning)
    
    def draw(self, surface):
        # Skip drawing if card isn't visible (for destruction animations)
        if not self.is_visible:
            return
        
        # Calculate total floating offset (idle + hover)
        total_float_offset = self.idle_float_offset + self.hover_float_offset
            
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
                        colour = scaled_shadow.get_at((x, y))
                        grey = (colour[0] + colour[1] + colour[2]) // 3
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
                
                # Calculate center position of the card
                center_x = self.rect.x + self.rect.width / 2
                center_y = self.rect.y + self.rect.height / 2
                
                # Adjust position to keep card centered during scaling and floating
                x_pos = center_x - scaled_width / 2
                y_pos = center_y - self.height / 2 - total_float_offset
                
                surface.blit(scaled_card, (x_pos, y_pos))
        else:
            # Normal drawing (either face up or face down) with rotation and hover support
            current_texture = self.texture if self.face_up else self.face_down_texture
            
            # Calculate the center position for rotated or scaled cards
            # This ensures the card rotates around its center
            center_x = self.rect.x + self.rect.width / 2
            center_y = self.rect.y + self.rect.height / 2
            
            # Calculate the top-left position for drawing, including float offset
            pos_x = center_x - current_texture.get_width() / 2
            pos_y = center_y - current_texture.get_height() / 2 - total_float_offset
            
            # Calculate shadow properties based on float height
            # As the card floats higher, shadow moves further away and gets more transparent
            shadow_alpha = 40 + int(15 * (total_float_offset / (self.idle_float_amount + self.hover_lift_amount)))
            shadow_offset = 4 + int(total_float_offset * 0.7)  # Shadow moves more with higher float
            
            # Scale shadow based on height for perspective effect
            shadow_scale = 1.0 + (total_float_offset * 0.0007)  # Slight scaling for perspective
            shadow_width = int(current_texture.get_width() * shadow_scale)
            shadow_height = int(current_texture.get_height() * shadow_scale)
            
            # Create shadow surface
            shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, shadow_alpha))
            
            # Calculate shadow position (centered under the card)
            shadow_x = center_x - shadow_width / 2 + shadow_offset
            shadow_y = center_y - shadow_height / 2 + shadow_offset
            
            # Draw the shadow
            surface.blit(shadow_surf, (shadow_x, shadow_y))
            
            # Draw the card at the calculated position
            surface.blit(current_texture, (pos_x, pos_y))
            
            # Draw selection overlay for cards when hovered
            # Show split colours for hovered cards
            if self.face_up and self.is_hovered:
                # Create overlay surfaces for top and bottom sections
                overlay_width = current_texture.get_width()
                overlay_height = current_texture.get_height() // 2  # Half height for each section
                
                # For defeated monsters, don't show any action overlay
                is_defeated_monster = False
                
                # First check the is_defeated flag
                if hasattr(self, 'is_defeated') and self.is_defeated:
                    is_defeated_monster = True
                
                # As a fallback, also check if it's in the PlayingState's defeated_monsters list
                if not is_defeated_monster and pygame.display.get_surface():
                    # Only try to access the playing_state if we're running in the game
                    try:
                        # This gets the current PyGame application
                        import sys
                        main_module = sys.modules['__main__']
                        if hasattr(main_module, 'game_manager'):
                            game_manager = main_module.game_manager
                            if hasattr(game_manager, 'current_state'):
                                current_state = game_manager.current_state
                                if hasattr(current_state, 'defeated_monsters'):
                                    # Check if this card is in the defeated_monsters list
                                    if self in current_state.defeated_monsters:
                                        is_defeated_monster = True
                                        # Also set the flag for future checks
                                        self.is_defeated = True
                    except:
                        # If anything goes wrong, just continue
                        pass
                
                # Skip all overlay rendering for defeated monsters
                if is_defeated_monster:
                    pass  # No overlay for defeated monsters
                
                # Check if this is an equipped weapon (show discard only)
                elif hasattr(self, 'is_equipped') and self.is_equipped:
                    # Full overlay with single color for discard
                    full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                    full_overlay.fill((200, 60, 60))  # Bright red color for discard
                    full_overlay.set_alpha(150)  # More opacity
                    surface.blit(full_overlay, (pos_x, pos_y))
                
                # Check if this is an inventory card (show split equip/discard or use/discard)
                elif hasattr(self, 'in_inventory') and self.in_inventory:
                    # Create top overlay
                    top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                    
                    # Create bottom overlay (red for discard)
                    bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                    bottom_overlay.fill((200, 60, 60))  # Bright red color for discard
                    
                    # Choose top color based on card type
                    if self.type == "weapon":
                        top_overlay.fill((60, 180, 60))  # Bright green for equipping
                    elif self.type == "potion":
                        top_overlay.fill((220, 160, 50))  # Bright orange for potion use
                    
                    # Highlight the currently hovered section more intensely
                    top_alpha = 120  # Higher base opacity
                    bottom_alpha = 120  # Higher base opacity
                    if self.hover_selection == "top":
                        top_alpha = 180
                        bottom_alpha = 100
                    elif self.hover_selection == "bottom":
                        top_alpha = 100
                        bottom_alpha = 180
                    
                    top_overlay.set_alpha(top_alpha)
                    bottom_overlay.set_alpha(bottom_alpha)
                    
                    # Draw the overlays
                    surface.blit(top_overlay, (pos_x, pos_y))
                    surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))
                
                # Handle inventory/use overlay for regular room cards (potions and weapons)
                elif self.can_add_to_inventory:
                    if hasattr(self, 'inventory_available') and self.inventory_available:
                        # When inventory has space - show both options
                        # Create top overlay (purple for inventory)
                        top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        top_overlay.fill(self.inventory_colour)
                        
                        # Create bottom overlay (orange for potions use, green for weapon equip)
                        bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        if self.type == "weapon":
                            bottom_overlay.fill(self.equip_colour)  # Green for weapon equipping
                        else:
                            bottom_overlay.fill(self.use_colour)  # Orange for potion use
                        
                        # Highlight the currently hovered section more intensely
                        top_alpha = 100
                        bottom_alpha = 100
                        if self.hover_selection == "top":
                            # Make the top overlay more opaque
                            top_alpha = 150
                            bottom_alpha = 100
                        elif self.hover_selection == "bottom":
                            # Make the top overlay more opaque
                            top_alpha = 100
                            bottom_alpha = 150
                        
                        top_overlay.set_alpha(top_alpha)
                        bottom_overlay.set_alpha(bottom_alpha)
                        
                        # Draw the overlays
                        surface.blit(top_overlay, (pos_x, pos_y))
                        surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))

                    else:
                        # When inventory is full - only show use/equip option
                        # Create full card overlay for use/equip only
                        full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                        
                        # Choose color based on card type
                        if self.type == "weapon":
                            full_overlay.fill(self.equip_colour)  # Green for weapon equipping
                        else:
                            full_overlay.fill(self.use_colour)  # Orange for potion use
                        
                        # Set opacity
                        full_overlay.set_alpha(130)
                        
                        # Draw the overlay
                        surface.blit(full_overlay, (pos_x, pos_y))
                
                # Handle weapon/bare-handed attack overlay for monsters
                elif self.can_show_attack_options:
                    # If we have a weapon equipped and the weapon attack is viable, show both options
                    if self.weapon_available and not self.weapon_attack_not_viable:
                        # Create top overlay (blue for weapon attack)
                        top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        top_overlay.fill(self.weapon_attack_colour)
                        
                        # Create bottom overlay (red for bare-handed attack)
                        bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        bottom_overlay.fill(self.bare_hands_colour)
                        
                        # Highlight the currently hovered section more intensely
                        top_alpha = 100
                        bottom_alpha = 100
                        if self.hover_selection == "top":
                            # Make the top overlay more opaque
                            top_alpha = 150
                            bottom_alpha = 100
                        elif self.hover_selection == "bottom":
                            # Make the bottom overlay more opaque
                            top_alpha = 100
                            bottom_alpha = 150
                        
                        top_overlay.set_alpha(top_alpha)
                        bottom_overlay.set_alpha(bottom_alpha)
                        
                        # Draw the overlays
                        surface.blit(top_overlay, (pos_x, pos_y))
                        surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))
                    else:
                        # No weapon equipped or weapon attack not viable - show only bare hands option on the entire card
                        full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                        full_overlay.fill(self.bare_hands_colour)
                        full_overlay.set_alpha(120)  # Slightly more transparent
                        
                        # Draw the overlay
                        surface.blit(full_overlay, (pos_x, pos_y))

    def draw_hover_text(self, surface):
        """Draw hover action text to the right of the card using the delving deck style"""
        # Check if the card is hovered while in inventory
        card_in_inventory = hasattr(self, 'in_inventory') and self.in_inventory
        # Check if this is a defeated monster
        is_defeated_monster = hasattr(self, 'is_defeated') and self.is_defeated
        
        # For defeated monsters, just show info when hovered
        if is_defeated_monster:
            if not (self.is_hovered and self.face_up):
                return
        # If this is an inventory card
        elif card_in_inventory:
            # Only show hover info for inventory cards when hovered and face up
            if not (self.is_hovered and self.face_up):
                return
        else:
            # For non-inventory cards, use standard checks
            show_for_inventory = self.face_up and self.can_add_to_inventory and self.is_hovered and self.hover_selection
            show_for_monster = self.face_up and self.can_show_attack_options and self.is_hovered and self.hover_selection
            
            # Return if conditions not met
            if not (show_for_inventory or show_for_monster):
                return
        
        # Import necessary classes
        from ui.panel import Panel
        from constants import GOLD_COLOR
        
        # Load fonts matching the delving deck state
        header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 32)  # Larger font for card name
        body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)    # Medium font for details
        
        # Set info box dimensions - exact match to delving deck
        info_width = 300
        
        # Calculate height based on content (we'll adjust after rendering text)
        header_height = header_font.get_height()
        body_height = body_font.get_height()
        
        # Get card position
        card_center_x = self.rect.centerx
        card_top = self.rect.top
        card_bottom = self.rect.bottom
        card_left = self.rect.left
        card_right = self.rect.right
        
        # Calculate the total float offset for positioning
        total_float_offset = 0
        if hasattr(self, 'idle_float_offset') and hasattr(self, 'hover_float_offset'):
            total_float_offset = self.idle_float_offset + self.hover_float_offset
        
        # Start with the right side position (most readable)
        info_x = card_right + 10
        info_y = card_top - total_float_offset
        
        # Calculate lines of text to show
        info_lines = []
        
        # First determine what type of card this is and prepare appropriate info
        if self.type == "weapon":
            # Start with the card name
            card_name = self.name if hasattr(self, 'name') and self.name else f"Weapon {self.value}"
            
            # Determine weapon type based on value if not already set
            weapon_type = None
            if hasattr(self, 'weapon_type') and self.weapon_type:
                weapon_type = self.weapon_type
            else:
                # Fallback to determine type based on card value
                if self.value in [2, 3]:
                    weapon_type = "arrow"
                elif self.value in [11, 13]:  # Longbow and Crossbow are ranged
                    weapon_type = "ranged"
                else:
                    weapon_type = "melee"
            
            # Weapon type text
            type_text = f"Weapon - "
            if weapon_type == "ranged":
                type_text += "Ranged"
            elif weapon_type == "melee":
                type_text += "Melee"
            elif weapon_type == "arrow":
                type_text += "Arrow (Ammo)"
            
            # Damage text
            damage_text = f"Damage: {self.value}"
            
            # Add action text based on card location and selection
            action_text = ""
            action_color = GOLD_COLOR  # Default color
            
            # Check if this is an inventory card
            if hasattr(self, 'in_inventory') and self.in_inventory:
                if self.hover_selection == "top":
                    if self.type == "weapon":
                        action_text = "EQUIP"
                        action_color = (120, 255, 120)  # Bright green
                    elif self.type == "potion":
                        action_text = "USE"
                        action_color = (255, 220, 100)  # Bright gold/yellow
                elif self.hover_selection == "bottom":
                    action_text = "DISCARD"
                    action_color = (255, 120, 120)  # Bright red
                else:
                    # When no hover selection (just hovering on card)
                    if self.type == "weapon":
                        action_text = "EQUIP or DISCARD"
                    elif self.type == "potion":
                        action_text = "USE or DISCARD"
            # Check if this is an equipped weapon
            elif hasattr(self, 'is_equipped') and self.is_equipped:
                action_text = "DISCARD"
                action_color = (255, 120, 120)  # Bright red
            # Standard room card
            else:
                if self.hover_selection == "top":
                    action_text = "INVENTORY"
                    action_color = (120, 120, 255)  # Bright blue
                elif self.hover_selection == "bottom":
                    if self.type == "weapon":
                        action_text = "EQUIP"
                        action_color = (120, 255, 120)  # Bright green
                    elif self.type == "potion":
                        action_text = "USE"
                        action_color = (255, 220, 100)  # Bright gold/yellow
            
            # Create complete lines list
            info_lines = [
                {"text": card_name, "font": header_font, "color": WHITE},
                {"text": type_text, "font": body_font, "color": GOLD_COLOR},
                {"text": damage_text, "font": body_font, "color": WHITE}
            ]
            
            # Add action text if present
            if action_text:
                info_lines.append({"text": action_text, "font": body_font, "color": action_color})
                
        elif self.type == "potion":
            # Start with the card name
            card_name = self.name if hasattr(self, 'name') and self.name else f"Potion {self.value}"
            
            # Potion type text
            type_text = "Potion - Healing"
            
            # Healing effect text
            heal_text = f"Restores {self.value} health"
            
            # Add action text based on card location and selection
            action_text = ""
            action_color = GOLD_COLOR  # Default color
            
            # Check if this is an inventory card
            if hasattr(self, 'in_inventory') and self.in_inventory:
                if self.hover_selection == "top":
                    action_text = "USE"
                    action_color = (255, 220, 100)  # Bright gold/yellow
                elif self.hover_selection == "bottom":
                    action_text = "DISCARD"
                    action_color = (255, 120, 120)  # Bright red
                else:
                    # When no hover selection (just hovering on card)
                    action_text = "USE or DISCARD"
            # Standard room card
            else:
                if self.hover_selection == "top":
                    action_text = "INVENTORY"
                    action_color = (120, 120, 255)  # Bright blue
                elif self.hover_selection == "bottom":
                    action_text = "USE"
                    action_color = (255, 220, 100)  # Bright gold/yellow
            
            # Create complete lines list
            info_lines = [
                {"text": card_name, "font": header_font, "color": WHITE},
                {"text": type_text, "font": body_font, "color": GOLD_COLOR},
                {"text": heal_text, "font": body_font, "color": WHITE}
            ]
            
            # Add action text if present
            if action_text:
                info_lines.append({"text": action_text, "font": body_font, "color": action_color})
                
        elif self.type == "monster":
            # Start with the monster name
            monster_name = self.name if hasattr(self, 'name') and self.name else f"Monster {self.value}"
            
            # Monster type text
            type_text = f"{self.monster_type} - Value {self.value}" if hasattr(self, 'monster_type') and self.monster_type else f"Monster - Value {self.value}"
            
            # Add action/warning text based on weapon state and selection
            action_text = ""
            warning_text = ""
            action_color = GOLD_COLOR
            defeated_text = ""
            
            # Check if this is a defeated monster - also check if it's in the defeated_monsters list
            is_defeated_monster = False
            
            # First check the is_defeated flag
            if hasattr(self, 'is_defeated') and self.is_defeated:
                is_defeated_monster = True
            
            # As a fallback, also check if it's in the PlayingState's defeated_monsters list
            if not is_defeated_monster and pygame.display.get_surface():
                # Only try to access the playing_state if we're running in the game
                try:
                    # This gets the current PyGame application
                    import sys
                    main_module = sys.modules['__main__']
                    if hasattr(main_module, 'game_manager'):
                        game_manager = main_module.game_manager
                        if hasattr(game_manager, 'current_state'):
                            current_state = game_manager.current_state
                            if hasattr(current_state, 'defeated_monsters'):
                                # Check if this card is in the defeated_monsters list
                                if self in current_state.defeated_monsters:
                                    is_defeated_monster = True
                                    # Also set the flag for future checks
                                    self.is_defeated = True
                except:
                    # If anything goes wrong, just continue
                    pass
            
            if is_defeated_monster:
                # For defeated monsters, add a "DEFEATED" text instead of actions
                defeated_text = "DEFEATED"
            else:
                # Only show action options for monsters that aren't defeated
                if self.weapon_available and not self.weapon_attack_not_viable:
                    if self.hover_selection == "top":
                        action_text = "WEAPON ATTACK"
                        action_color = (120, 170, 255)  # Bright blue
                    elif self.hover_selection == "bottom":
                        action_text = "BARE HANDS"
                        action_color = (255, 120, 120)  # Bright red
                elif self.weapon_available and self.weapon_attack_not_viable:
                    if self.no_arrows:
                        warning_text = "NO ARROWS AVAILABLE"
                    else:
                        warning_text = "TOO POWERFUL FOR WEAPON"
                    action_text = "BARE HANDS ONLY"
                    action_color = (255, 120, 120)  # Bright red
                else:
                    action_text = "BARE HANDS ONLY"
                    action_color = (255, 120, 120)  # Bright red
            
            # Create complete lines list
            info_lines = [
                {"text": monster_name, "font": header_font, "color": WHITE},
                {"text": type_text, "font": body_font, "color": GOLD_COLOR}
            ]
            
            # Add "DEFEATED" text for defeated monsters
            if defeated_text:
                info_lines.append({"text": defeated_text, "font": body_font, "color": (150, 150, 150)})  # Grey color
            
            # Add warning text if present
            elif warning_text:
                info_lines.append({"text": warning_text, "font": body_font, "color": (255, 100, 100)})
                
            # Add action text if present
            elif action_text:
                info_lines.append({"text": action_text, "font": body_font, "color": action_color})
        
        # Calculate total height needed for all lines with spacing
        total_text_height = 0
        line_spacing = 5
        for line in info_lines:
            total_text_height += line["font"].get_height() + line_spacing
        
        # Calculate info panel height
        info_height = 10 + total_text_height + 5  # 10px padding top, 5px padding bottom (matching delving deck)
        
        # Smart positioning logic - match the delving deck state approach
        # If it would go off-screen to the right, position left of card
        # Try to check against main_panel boundaries if available, otherwise use screen bounds
        main_panel_right = pygame.display.get_surface().get_width() - 10  # Default screen right edge
        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_right = self.main_panel.rect.right - 10
            
        if info_x + info_width > main_panel_right:
            info_x = card_left - info_width - 10
            
        # If it's still off-screen, position above or below the card
        main_panel_left = 10  # Default screen left edge
        main_panel_bottom = pygame.display.get_surface().get_height() - 10  # Default screen bottom
        
        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_left = self.main_panel.rect.left + 10
            main_panel_bottom = self.main_panel.rect.bottom - 10
            
        if info_x < main_panel_left:
            # Position below or above based on available space
            if card_bottom + info_height + 10 <= main_panel_bottom:
                # Position below
                info_x = card_center_x - (info_width // 2)
                info_y = card_bottom + 10
            else:
                # Position above
                info_x = card_center_x - (info_width // 2)
                info_y = card_top - info_height - 10
        
        # Final bounds check - ensure it stays within panel bounds if available
        main_panel_top = 10  # Default screen top edge
        
        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_top = self.main_panel.rect.top + 10
        
        # Final safety check - ensure panel stays within bounds
        info_x = max(main_panel_left, min(info_x, main_panel_right - info_width))
        info_y = max(main_panel_top, min(info_y, main_panel_bottom - info_height))
            
        # Create and draw the info panel
        panel_color = (60, 50, 40)  # Default brown color matching delving deck
        
        # For defeated monsters, use neutral color
        if hasattr(self, 'is_defeated') and self.is_defeated:
            panel_color = (60, 50, 40)  # Default brown color, no special highlight
        # For inventory cards, match panel color with action
        elif hasattr(self, 'in_inventory') and self.in_inventory:
            if self.hover_selection == "top":
                if self.type == "weapon":
                    panel_color = (60, 100, 40)  # Green tint for EQUIP
                elif self.type == "potion": 
                    panel_color = (100, 90, 40)  # Yellow/orange tint for USE
            elif self.hover_selection == "bottom":
                panel_color = (100, 40, 40)  # Red tint for DISCARD
        # For equipped weapons, use discard color
        elif hasattr(self, 'is_equipped') and self.is_equipped:
            panel_color = (100, 40, 40)  # Red tint for DISCARD
        # For room weapon cards
        elif self.type == "weapon" and self.hover_selection:
            if self.hover_selection == "top":
                panel_color = (60, 50, 100)  # Blue tint for INVENTORY
            elif self.hover_selection == "bottom":
                panel_color = (60, 100, 40)  # Green tint for EQUIP
        # For room potion cards
        elif self.type == "potion" and self.hover_selection:
            if self.hover_selection == "top":
                panel_color = (60, 50, 100)  # Blue tint for INVENTORY
            elif self.hover_selection == "bottom":
                panel_color = (100, 90, 40)  # Yellow/orange tint for USE
        # For monster cards
        elif self.type == "monster":
            if self.weapon_attack_not_viable:
                panel_color = (100, 40, 40)  # Red tint for warnings
            elif self.hover_selection == "top":
                panel_color = (40, 60, 100)  # Blue tint for WEAPON ATTACK
            elif self.hover_selection == "bottom":
                panel_color = (100, 40, 40)  # Red tint for BARE HANDS
            
        info_panel = Panel(
            (info_width, info_height),
            (info_x, info_y),
            colour=panel_color,
            alpha=220,
            border_radius=8,
            dungeon_style=True
        )
        info_panel.draw(surface)
        
        # Draw all lines of text
        current_y = info_y + 10  # Start with top padding
        for line in info_lines:
            text_surface = line["font"].render(line["text"], True, line["color"])
            text_rect = text_surface.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(text_surface, text_rect)
            current_y = text_rect.bottom + line_spacing
    
    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        previous_selection = self.hover_selection
        
        # Reset hover selection
        self.hover_selection = None
        
        # Card is already verified to be under cursor and the closest one
        # So we just set is_hovered to True
        self.is_hovered = True
        
        # Determine which part of the card is being hovered (top or bottom)
        if self.is_hovered and self.face_up:
            # Calculate the mid-point of the card height
            card_midpoint_y = self.rect.y + self.rect.height / 2
            
            # For defeated monsters, don't set any hover selection
            is_defeated_monster = False
            
            # Check the is_defeated flag
            if hasattr(self, 'is_defeated') and self.is_defeated:
                is_defeated_monster = True
            
            # As a fallback, also check if it's in the PlayingState's defeated_monsters list
            if not is_defeated_monster and pygame.display.get_surface():
                try:
                    import sys
                    main_module = sys.modules['__main__']
                    if hasattr(main_module, 'game_manager'):
                        game_manager = main_module.game_manager
                        if hasattr(game_manager, 'current_state'):
                            current_state = game_manager.current_state
                            if hasattr(current_state, 'defeated_monsters'):
                                if self in current_state.defeated_monsters:
                                    is_defeated_monster = True
                                    self.is_defeated = True
                except:
                    pass
            
            if is_defeated_monster:
                # No hover selection for defeated monsters (ensures no split colors)
                self.hover_selection = None
            
            # For equipped weapons (only have discard option)
            elif hasattr(self, 'is_equipped') and self.is_equipped:
                # No split for equipped weapons, just a single action
                self.hover_selection = "bottom"  # Discard
            
            # For inventory cards
            elif hasattr(self, 'in_inventory') and self.in_inventory:
                # Show split options for inventory cards: use/equip or discard
                if mouse_pos[1] < card_midpoint_y:
                    self.hover_selection = "top"  # Use or equip
                else:
                    self.hover_selection = "bottom"  # Discard
            
            # For regular room cards
            elif self.can_add_to_inventory:
                # For potions and weapons
                if hasattr(self, 'inventory_available') and self.inventory_available:
                    # When inventory has space, show both options
                    if mouse_pos[1] < card_midpoint_y:
                        self.hover_selection = "top"  # Inventory (purple)
                    else:
                        self.hover_selection = "bottom"  # Use (orange)
                else:
                    # When inventory is full, always use "bottom" (use/equip)
                    self.hover_selection = "bottom"  # Always use/equip
            elif self.can_show_attack_options:
                # For monsters
                if self.weapon_available and not self.weapon_attack_not_viable:
                    # When weapon is available and viable, show both options
                    if mouse_pos[1] < card_midpoint_y:
                        self.hover_selection = "top"  # Weapon attack (blue)
                    else:
                        self.hover_selection = "bottom"  # Bare hands (red)
                else:
                    # When no weapon is available or weapon attack not viable, always use "bottom" (bare hands)
                    self.hover_selection = "bottom"  # Always bare hands
            
        # Return true if either the hover state or the selection changed
        return previous_hover != self.is_hovered or previous_selection != self.hover_selection