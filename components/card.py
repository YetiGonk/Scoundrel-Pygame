""" Card component for the Scoundrel game with enhanced animation support. """
import pygame
import math
import random
from constants import CARD_WIDTH, CARD_HEIGHT, CARD_RED, BLACK, WHITE, DARK_GRAY, FONTS_PATH
from utils.resource_loader import ResourceLoader
from roguelike_constants import FLOOR_MONSTERS, WEAPON_DAMAGE_TYPES, WEAPON_MAPPINGS

class Card:
    """ Represents a card in the game with support for rotation and scaling. """
    
    @staticmethod
    def _to_roman(num):
        """Convert integer to Roman numeral"""
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
        
        # Special handling for arrow cards (ranged ammo)
        if self.type == "weapon" and self.value == 2:  # 2 of Diamonds is an arrow
            self.weapon_type = "arrow"
            self.name = "Arrow"
        
        # Load the card texture
        texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")
            
        # If this is a monster card (spades or clubs), add monster image and name
        if self.type == "monster" and self.value >= 2 and self.value <= 14:
            texture = self.add_monster_to_card(texture)
        # If this is a weapon card (diamonds), add weapon image
        elif self.type == "weapon" and self.value >= 2 and self.value <= 14:
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
            # Only show split colours if the card hasn't been selected yet
            if self.face_up and self.is_hovered and not self.is_selected:
                # Create overlay surfaces for top and bottom sections
                overlay_width = current_texture.get_width()
                overlay_height = current_texture.get_height() // 2  # Half height for each section
                
                # Handle inventory/use overlay for potions and weapons
                if self.can_add_to_inventory:
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
                            # Make the bottom overlay more opaque
                            top_alpha = 100
                            bottom_alpha = 150
                        
                        top_overlay.set_alpha(top_alpha)
                        bottom_overlay.set_alpha(bottom_alpha)
                        
                        # Draw the overlays
                        surface.blit(top_overlay, (pos_x, pos_y))
                        surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))
                        
                        # Draw icons for inventory and use options
                        font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 14)
                        
                        # 1. Draw inventory bag icon in the top half
                        bag_icon = pygame.transform.scale(ResourceLoader.load_image("ui/inv.png"), (self.icon_size, self.icon_size))
                        bag_icon_x = pos_x + (overlay_width - self.icon_size) // 2
                        bag_icon_y = pos_y + (overlay_height - self.icon_size) // 2
                        surface.blit(bag_icon, (bag_icon_x, bag_icon_y))
                        
                        # 2. Draw hand icon in the bottom half
                        hand_icon = pygame.transform.scale(ResourceLoader.load_image("ui/hand.png"), (self.icon_size, self.icon_size))
                        hand_icon_x = pos_x + (overlay_width - self.icon_size) // 2
                        hand_icon_y = pos_y + overlay_height + (overlay_height - self.icon_size) // 2
                        surface.blit(hand_icon, (hand_icon_x, hand_icon_y))
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
                        
                        # Draw appropriate text centered on card
                        font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 18)
                        action_text = "EQUIP" if self.type == "weapon" else "USE"
                        text = font.render(action_text, True, WHITE)
                        text_x = pos_x + (overlay_width - text.get_width()) // 2
                        text_y = pos_y + overlay_height - text.get_height() // 2
                        surface.blit(text, (text_x, text_y))
                        
                        # Draw hand icon centered on card
                        hand_icon = pygame.transform.scale(ResourceLoader.load_image("ui/hand.png"), (self.icon_size, self.icon_size))
                        hand_icon_x = pos_x + (overlay_width - self.icon_size) // 2
                        hand_icon_y = pos_y + overlay_height - self.icon_size - 8
                        surface.blit(hand_icon, (hand_icon_x, hand_icon_y))
                
                # Handle weapon/bare-handed attack overlay for monsters
                elif self.can_show_attack_options:
                    # If we have a weapon equipped, show both options
                    if self.weapon_available:
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
                        # No weapon equipped - show only bare hands option on the entire card
                        full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                        full_overlay.fill(self.bare_hands_colour)
                        full_overlay.set_alpha(120)  # Slightly more transparent
                        
                        # Draw the overlay
                        surface.blit(full_overlay, (pos_x, pos_y))

    def draw_hover_text(self, surface):
        """Draw hover action text to the right of the card"""
        # Don't show the hover text for cards in inventory
        show_for_inventory = self.face_up and self.can_add_to_inventory and self.is_hovered and self.hover_selection
        show_for_monster = self.face_up and self.can_show_attack_options and self.is_hovered and self.hover_selection
        
        if not (show_for_inventory or show_for_monster) or (hasattr(self, 'in_inventory') and self.in_inventory):
            return
            
        font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 14)
        current_texture = self.texture if self.face_up else self.face_down_texture
        overlay_width = current_texture.get_width()
        
        # Calculate base position (will change based on hover area)
        center_x = self.rect.x + self.rect.width / 2
        center_y = self.rect.y + self.rect.height / 2
        pos_x = center_x - current_texture.get_width() / 2
        
        # Calculate the total float offset for proper positioning
        total_float_offset = 0
        if hasattr(self, 'idle_float_offset') and hasattr(self, 'hover_float_offset'):
            total_float_offset = self.idle_float_offset + self.hover_float_offset
        pos_y = center_y - current_texture.get_height() / 2 - total_float_offset
            
        # Draw text and background based on hover selection
        if self.can_add_to_inventory:
            # Handle inventory/use labels for potions and weapons
            if hasattr(self, 'inventory_available') and self.inventory_available:
                # When inventory has space, show both options depending on hover position
                if self.hover_selection == "top":
                    # Show "INVENTORY" text
                    bag_text = font.render("INVENTORY", True, WHITE)
                    
                    # Create background for the text
                    text_bg = pygame.Surface((bag_text.get_width() + 10, bag_text.get_height() + 6), pygame.SRCALPHA)
                    text_bg.fill((0, 0, 0, 220))  # More opaque black background to stand out
                    
                    # Position text to the right of the card
                    text_bg_x = pos_x + overlay_width + 5
                    text_bg_y = pos_y + (self.height // 4) - (text_bg.get_height() // 2)
                    
                    # Draw background and text
                    surface.blit(text_bg, (text_bg_x, text_bg_y))
                    surface.blit(bag_text, (text_bg_x + 5, text_bg_y + 3))
    
                elif self.hover_selection == "bottom":
                    # Show appropriate action text
                    action_text = "EQUIP" if self.type == "weapon" else "USE"
                    hand_text = font.render(action_text, True, WHITE)
                    
                    # Create background for the text
                    text_bg = pygame.Surface((hand_text.get_width() + 10, hand_text.get_height() + 6), pygame.SRCALPHA)
                    if self.type == "weapon":
                        text_bg.fill((0, 120, 0, 220))  # Green background for equipping
                    else:
                        text_bg.fill((0, 0, 0, 220))  # More opaque black background
                    
                    # Position text to the right of the card
                    text_bg_x = pos_x + overlay_width + 5
                    text_bg_y = pos_y + (self.height * 3 // 4) - (text_bg.get_height() // 2)
                    
                    # Draw background and text
                    surface.blit(text_bg, (text_bg_x, text_bg_y))
                    surface.blit(hand_text, (text_bg_x + 5, text_bg_y + 3))
            else:
                # When inventory is full, show only use/equip option
                action_text = "EQUIP" if self.type == "weapon" else "USE"
                hand_text = font.render(action_text, True, WHITE)
                
                # Create background for the text
                text_bg = pygame.Surface((hand_text.get_width() + 10, hand_text.get_height() + 6), pygame.SRCALPHA)
                if self.type == "weapon":
                    text_bg.fill((0, 120, 0, 220))  # Green background for equipping
                else:
                    text_bg.fill((0, 0, 0, 220))  # More opaque black background
                
                # Position text to the right of the card
                text_bg_x = pos_x + overlay_width + 5
                text_bg_y = pos_y + (self.height // 2) - (text_bg.get_height() // 2)  # Center vertically
                
                # Draw background and text
                surface.blit(text_bg, (text_bg_x, text_bg_y))
                surface.blit(hand_text, (text_bg_x + 5, text_bg_y + 3))
                
        elif self.can_show_attack_options:
            # Handle attack option labels for monsters
            if self.weapon_available:
                # With weapon available, show both options
                if self.hover_selection == "top":
                    # Show "WEAPON ATTACK" text
                    weapon_text = font.render("WEAPON ATTACK", True, WHITE)
                    
                    # Create background for the text
                    text_bg = pygame.Surface((weapon_text.get_width() + 10, weapon_text.get_height() + 6), pygame.SRCALPHA)
                    text_bg.fill((0, 0, 0, 220))  # More opaque black background
                    
                    # Position text to the right of the card
                    text_bg_x = pos_x + overlay_width + 5
                    text_bg_y = pos_y + (self.height // 4) - (text_bg.get_height() // 2)
                    
                    # Draw background and text
                    surface.blit(text_bg, (text_bg_x, text_bg_y))
                    surface.blit(weapon_text, (text_bg_x + 5, text_bg_y + 3))
                    
                elif self.hover_selection == "bottom":
                    # Show "BARE HANDS" text
                    bare_text = font.render("BARE HANDS", True, WHITE)
                    
                    # Create background for the text with warning
                    text_bg = pygame.Surface((bare_text.get_width() + 10, bare_text.get_height() + 6), pygame.SRCALPHA)
                    text_bg.fill((160, 0, 0, 220))  # Red background for warning
                    
                    # Position text to the right of the card
                    text_bg_x = pos_x + overlay_width + 5
                    text_bg_y = pos_y + (self.height * 3 // 4) - (text_bg.get_height() // 2)
                    
                    # Draw background and text
                    surface.blit(text_bg, (text_bg_x, text_bg_y))
                    surface.blit(bare_text, (text_bg_x + 5, text_bg_y + 3))
            else:
                # No weapon available - show only bare hands option
                bare_text = font.render("BARE HANDS ONLY", True, WHITE)
                
                # Create background for the text with warning
                text_bg = pygame.Surface((bare_text.get_width() + 10, bare_text.get_height() + 6), pygame.SRCALPHA)
                text_bg.fill((160, 0, 0, 220))  # Red background for warning
                
                # Position text to the right of the card (centered vertically)
                text_bg_x = pos_x + overlay_width + 5
                text_bg_y = pos_y + (self.height // 2) - (text_bg.get_height() // 2)
                
                # Draw background and text
                surface.blit(text_bg, (text_bg_x, text_bg_y))
                surface.blit(bare_text, (text_bg_x + 5, text_bg_y + 3))
    
    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        previous_selection = self.hover_selection
        
        # Reset hover selection
        self.hover_selection = None
        
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
        
        # Determine which part of the card is being hovered (top or bottom)
        if self.is_hovered and self.face_up:
            # Calculate the mid-point of the card height
            card_midpoint_y = self.rect.y + self.rect.height / 2
            
            # Check if mouse is in top or bottom half
            if self.can_add_to_inventory:
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
                if self.weapon_available:
                    # When weapon is available, show both options
                    if mouse_pos[1] < card_midpoint_y:
                        self.hover_selection = "top"  # Weapon attack (blue)
                    else:
                        self.hover_selection = "bottom"  # Bare hands (red)
                else:
                    # When no weapon is available, always use "bottom" (bare hands)
                    self.hover_selection = "bottom"  # Always bare hands
            
        # Return true if either the hover state or the selection changed
        return previous_hover != self.is_hovered or previous_selection != self.hover_selection