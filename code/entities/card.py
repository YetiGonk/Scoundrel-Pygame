import math
import pygame
from pygame.locals import *
import random

from config import *

from core.resource_loader import ResourceLoader

from ui.panel import Panel

class Card:
    """ Represents a card in the game with support for rotation and scaling. """

    @staticmethod
    def _to_roman(num):
        """Convert integer to Roman numeral"""
        if num == 0:
            return ""

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

        texture = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        texture.fill(WHITE)

        pygame.draw.rect(texture, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 1)

        suit_symbol = ""
        suit_colour = BLACK
        if suit == "diamonds":
            suit_symbol = "♦"
            suit_colour = (255, 0, 0)
        elif suit == "hearts":
            suit_symbol = "♥"
            suit_colour = (255, 0, 0)
        elif suit == "spades":
            suit_symbol = "♠"
            suit_colour = BLACK
        elif suit == "clubs":
            suit_symbol = "♣"
            suit_colour = BLACK

        suit_font = pygame.font.SysFont("arial", 40)
        suit_text = suit_font.render(suit_symbol, True, suit_colour)

        text_rect = suit_text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        texture.blit(suit_text, text_rect)

        small_font = pygame.font.SysFont("arial", 20)
        small_text = small_font.render(suit_symbol, True, suit_colour)

        texture.blit(small_text, (5, 5))

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

        self.is_flipping = False
        self.face_up = False
        self.z_index = 0
        self.is_visible = True
        self.floor_type = floor_type
        self.name = None

        self.damage_type = None
        self.weapon_difficulty = None
        self.monster_type = None

        self.sprite_file_path = None if self.suit in ("diamonds", "hearts") else self.determine_monster_sprite_path()

        if self.type == "potion":
            self.name = f"Potion {self._to_roman(self.value)}"
        elif self.type == "weapon":

            self.name = f"Weapon {self._to_roman(self.value)}"
        elif self.type == "monster":

            pass

        self.rotation = 0
        self.scale = 1.0

        self.idle_time = 0.0
        self.idle_float_speed = 1
        self.idle_float_amount = 6.0
        self.idle_float_offset = 0.0
        self.idle_phase_offset = 6.28 * random.random()

        self.hover_progress = 0.0
        self.hover_speed = 5.0
        self.hover_float_offset = 0.0
        self.hover_scale_target = 1.12
        self.hover_lift_amount = 15.0

        self.can_add_to_inventory = self.type in ["potion", "weapon"]
        self.can_show_attack_options = self.type in ["monster"]
        self.hover_selection = None
        self.inventory_colour = (128, 0, 128, 100)
        self.use_colour = (255, 165, 0, 100)
        self.equip_colour = (0, 255, 0, 100)
        self.weapon_attack_colour = (0, 100, 200, 100)
        self.bare_hands_colour = (200, 50, 50, 100)
        self.is_selected = False
        self.icon_size = 50

        self.weapon_available = False
        self.inventory_available = True
        self.weapon_attack_not_viable = False

        if self.value == 0:
            try:
                texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")
            except:
                if self.suit == "diamonds":
                    try:
                        texture = ResourceLoader.load_image(f"cards/{self.suit}_14.png")
                    except:
                        texture = self._create_blank_card("diamonds")
                else:
                    texture = self._create_blank_card(self.suit)
        else:
            texture = ResourceLoader.load_image(f"cards/{self.suit}_{self.value}.png")

        if self.type == "monster" and (self.value >= 2 and self.value <= 14):
            texture = self.add_monster_to_card(texture)
        elif self.type == "weapon" and (self.value >= 2 and self.value <= 14):
            texture = self.add_weapon_to_card(texture)
        elif self.type == "potion" and (self.value >= 2 and self.value <= 14):
            texture = self.add_potion_to_card(texture)

        self.texture = pygame.transform.scale(texture, (self.width, self.height))
        self.original_texture = self.texture

        self.face_down_texture = pygame.transform.scale(
            ResourceLoader.load_image("cards/card_back.png"),
            (self.width, self.height)
        )
        self.original_face_down_texture = self.face_down_texture

        self.flip_progress = 0.0
        self.is_flipping = False
        self.face_up = False
        self.lift_height = 20
        self.original_y = 0

    def add_monster_to_card(self, card_surface):
        """Add monster image to card surface based on suit, value and floor type"""
        self.name = f"{self.sprite_file_path.split("/")[-1].split(".")[0].title()} {self._to_roman(self.value)}"
        monster_name = self.name.lower()
        self.monster_type = self.sprite_file_path.split("/")[-2]

        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))

        monster_img = ResourceLoader.load_image(self.sprite_file_path, cache=False)
        monster_size = 96
        monster_img = pygame.transform.scale(monster_img, (monster_size, monster_size))
        monster_surface = pygame.Surface((monster_size, monster_size), pygame.SRCALPHA)
        monster_surface.blit(monster_img, (0, 0))

        monster_pos = ((card_width - monster_size) // 2, (card_height - monster_size) // 2)
        new_surface.blit(monster_surface, monster_pos)

        return new_surface

    def add_weapon_to_card(self, card_surface):
        """Add weapon image to card surface based on value"""
        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))

        self.weapon_difficulty = WEAPON_RANKS[self.value]
        weapon_name = random.choice(WEAPON_RANK_MAP[self.weapon_difficulty])
        self.damage_type = WEAPON_DAMAGE_TYPES[weapon_name]

        weapon_display_name = weapon_name.capitalize()
        self.name = f"{weapon_display_name} {self._to_roman(self.value)}"

        weapon_path = f"weapons/{weapon_name}.png"
        try:
            weapon_img = ResourceLoader.load_image(weapon_path)
            weapon_size = 120
            weapon_img = pygame.transform.scale(weapon_img, (weapon_size, weapon_size))
            weapon_pos = ((card_width - weapon_size) // 2, (card_height - weapon_size) // 2)
            new_surface.blit(weapon_img, weapon_pos)
        except Exception as e:
            return card_surface

        return new_surface

    def add_potion_to_card(self, card_surface):
        """Add potion image to card surface based on value"""
        card_width, card_height = card_surface.get_width(), card_surface.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surface, (0, 0))

        potion_path = f"potions/{random.randint(1,20)}.png"
        try:
            potion_img = ResourceLoader.load_image(potion_path)
            potion_size = 120
            potion_img = pygame.transform.scale(potion_img, (potion_size, potion_size))
            potion_pos = ((card_width - potion_size) // 2, (card_height - potion_size) // 2)
            new_surface.blit(potion_img, potion_pos)
        except Exception as e:
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

    def determine_monster_sprite_path(self):
        difficulty = MONSTER_RANKS[self.value]
        monster_file_path = random.choice(MONSTER_DIFFICULTY_MAP[difficulty])
        return monster_file_path

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

        self.idle_time += delta_time

        if hasattr(self, 'in_inventory') and self.in_inventory:
            self.idle_float_offset = math.sin(self.idle_time * self.idle_float_speed + self.idle_phase_offset) * (self.idle_float_amount * 0.25)
        else:
            self.idle_float_offset = math.sin(self.idle_time * self.idle_float_speed + self.idle_phase_offset) * self.idle_float_amount

        target_hover = 1.0 if self.is_hovered else 0.0
        if abs(self.hover_progress - target_hover) > 0.01:

            if self.hover_progress < target_hover:
                self.hover_progress = min(self.hover_progress + delta_time * self.hover_speed, target_hover)
            else:
                self.hover_progress = max(self.hover_progress - delta_time * self.hover_speed, target_hover)

            center_x = self.rect.centerx
            center_y = self.rect.centery

            base_scale = 1.0
            hover_scale_modifier = (self.hover_scale_target - 1.0) * self.hover_progress
            new_scale = base_scale + (base_scale * hover_scale_modifier)
            self.update_scale(new_scale)

            self.rect.centerx = center_x
            self.rect.centery = center_y

            if hasattr(self, 'in_inventory') and self.in_inventory:
                self.hover_float_offset = self.hover_lift_amount * self.hover_progress * 0.25
            else:
                self.hover_float_offset = self.hover_lift_amount * self.hover_progress

    def update_flip(self, delta_time):
        if self.is_flipping:

            flip_speed = 2
            self.flip_progress += delta_time * flip_speed

            if self.flip_progress >= 1.0:

                self.flip_progress = 1.0
                self.is_flipping = False
                self.face_up = True
                self.rect.y = self.original_y
            else:

                if self.flip_progress < 0.5:

                    lift_amount = self.lift_height * (self.flip_progress * 2)
                else:

                    lift_amount = self.lift_height * (1 - (self.flip_progress - 0.5) * 2)

                self.rect.y = self.original_y - lift_amount

    def rotate(self, angle):
        """Rotate the card textures"""
        self.rotation = angle

        if abs(angle) > 0.1:

            self.texture = pygame.transform.rotate(self.original_texture, angle)
            self.face_down_texture = pygame.transform.rotate(self.original_face_down_texture, angle)

            self.rect.width = self.texture.get_width()
            self.rect.height = self.texture.get_height()
        else:

            self.texture = self.original_texture.copy()
            self.face_down_texture = self.original_face_down_texture.copy()
            self.rect.width = self.width
            self.rect.height = self.height

    def update_scale(self, scale):
        """Update the card scale"""

        center_x = self.rect.centerx
        center_y = self.rect.centery

        if abs(scale - 1.0) < 0.01:

            self.texture = self.original_texture.copy()
            self.face_down_texture = self.original_face_down_texture.copy()
            self.rect.width = self.width
            self.rect.height = self.height
        else:

            new_width = int(self.width * scale)
            new_height = int(self.height * scale)

            if new_width > 0 and new_height > 0:
                self.texture = pygame.transform.scale(self.original_texture, (new_width, new_height))
                self.face_down_texture = pygame.transform.scale(self.original_face_down_texture, (new_width, new_height))

                self.rect.width = new_width
                self.rect.height = new_height

        self.scale = scale

    def draw(self, surface):

        if not self.is_visible:
            return

        total_float_offset = self.idle_float_offset + self.hover_float_offset

        if self.is_flipping:

            shadow_offset_x = 15
            shadow_offset_y = 15

            if self.flip_progress < 0.5:

                shadow_offset_x *= self.flip_progress * 2
                shadow_offset_y = 15
            else:

                shadow_offset_x *= 2 - self.flip_progress * 2
                shadow_offset_y = 15

            shadow_alpha = 120
            if self.flip_progress < 0.5:
                shadow_alpha = 120 - self.flip_progress * 80
            else:
                shadow_alpha = 80 + (self.flip_progress - 0.5) * 80

            shadow_texture = None
            if self.flip_progress < 0.5:
                shadow_texture = self.face_down_texture.copy()
            else:
                shadow_texture = self.texture.copy()

            shadow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            scaled_width = self.width
            if self.flip_progress < 0.5:

                scaled_width = self.width * (1 - self.flip_progress * 2)
            else:

                scaled_width = self.width * ((self.flip_progress - 0.5) * 2)

            if scaled_width > 1:

                scaled_shadow = pygame.transform.scale(shadow_texture, (int(scaled_width), self.height))

                for x in range(scaled_shadow.get_width()):
                    for y in range(scaled_shadow.get_height()):
                        colour = scaled_shadow.get_at((x, y))
                        grey = (colour[0] + colour[1] + colour[2]) // 3
                        scaled_shadow.set_at((x, y), (30, 30, 30, shadow_alpha))

                x_offset = (self.width - scaled_width) / 2

                surface.blit(scaled_shadow, (self.rect.x + x_offset + shadow_offset_x, self.rect.y + shadow_offset_y))

            scaled_width = self.width
            if self.flip_progress < 0.5:

                scaled_width = self.width * (1 - self.flip_progress * 2)
            else:

                scaled_width = self.width * ((self.flip_progress - 0.5) * 2)

            if self.flip_progress < 0.5:

                texture = self.face_down_texture
            else:

                texture = self.texture

            if scaled_width > 1:

                scaled_card = pygame.transform.scale(texture, (int(scaled_width), self.height))

                center_x = self.rect.x + self.rect.width / 2
                center_y = self.rect.y + self.rect.height / 2

                x_pos = center_x - scaled_width / 2
                y_pos = center_y - self.height / 2 - total_float_offset

                surface.blit(scaled_card, (x_pos, y_pos))
        else:

            current_texture = self.texture if self.face_up else self.face_down_texture

            center_x = self.rect.x + self.rect.width / 2
            center_y = self.rect.y + self.rect.height / 2

            pos_x = center_x - current_texture.get_width() / 2
            pos_y = center_y - current_texture.get_height() / 2 - total_float_offset

            shadow_alpha = 40 + int(15 * (total_float_offset / (self.idle_float_amount + self.hover_lift_amount)))
            shadow_offset = 4 + int(total_float_offset * 0.7)

            shadow_scale = 1.0 + (total_float_offset * 0.0007)
            shadow_width = int(current_texture.get_width() * shadow_scale)
            shadow_height = int(current_texture.get_height() * shadow_scale)

            shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, shadow_alpha))

            shadow_x = center_x - shadow_width / 2 + shadow_offset
            shadow_y = center_y - shadow_height / 2 + shadow_offset

            surface.blit(shadow_surf, (shadow_x, shadow_y))

            surface.blit(current_texture, (pos_x, pos_y))

            if self.face_up and self.is_hovered:

                overlay_width = current_texture.get_width()
                overlay_height = current_texture.get_height() // 2

                is_defeated_monster = False

                if hasattr(self, 'is_defeated') and self.is_defeated:
                    is_defeated_monster = True

                if not is_defeated_monster and pygame.display.get_surface():

                    try:

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
                    pass

                elif hasattr(self, 'is_equipped') and self.is_equipped:

                    full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                    full_overlay.fill((200, 60, 60))
                    full_overlay.set_alpha(120)
                    surface.blit(full_overlay, (pos_x, pos_y))

                elif hasattr(self, 'in_inventory') and self.in_inventory:

                    top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                    top_overlay.fill((200, 60, 60))

                    bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

                    if self.type == "weapon":
                        bottom_overlay.fill((60, 180, 60))
                    elif self.type == "potion":
                        bottom_overlay.fill((220, 160, 50))

                    top_alpha = 120
                    bottom_alpha = 120
                    if self.hover_selection == "top":
                        top_alpha = 180
                        bottom_alpha = 100
                    elif self.hover_selection == "bottom":
                        top_alpha = 100
                        bottom_alpha = 180

                    top_overlay.set_alpha(top_alpha)
                    bottom_overlay.set_alpha(bottom_alpha)

                    surface.blit(top_overlay, (pos_x, pos_y))
                    surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))

                elif self.can_add_to_inventory:
                    if hasattr(self, 'inventory_available') and self.inventory_available:

                        top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        top_overlay.fill(self.inventory_colour)

                        bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        if self.type == "weapon":
                            bottom_overlay.fill(self.equip_colour)
                        else:
                            bottom_overlay.fill(self.use_colour)

                        top_alpha = 120
                        bottom_alpha = 120
                        if self.hover_selection == "top":

                            top_alpha = 180
                            bottom_alpha = 120
                        elif self.hover_selection == "bottom":

                            top_alpha = 120
                            bottom_alpha = 180

                        top_overlay.set_alpha(top_alpha)
                        bottom_overlay.set_alpha(bottom_alpha)

                        surface.blit(top_overlay, (pos_x, pos_y))
                        surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))

                    else:

                        full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)

                        if self.type == "weapon":
                            full_overlay.fill(self.equip_colour)
                        else:
                            full_overlay.fill(self.use_colour)

                        full_overlay.set_alpha(130)

                        surface.blit(full_overlay, (pos_x, pos_y))

                elif self.can_show_attack_options:

                    if self.weapon_available and not self.weapon_attack_not_viable:

                        top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        top_overlay.fill(self.weapon_attack_colour)

                        bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                        bottom_overlay.fill(self.bare_hands_colour)

                        top_alpha = 120
                        bottom_alpha = 120
                        if self.hover_selection == "top":

                            top_alpha = 180
                            bottom_alpha = 120
                        elif self.hover_selection == "bottom":

                            top_alpha = 120
                            bottom_alpha = 180

                        top_overlay.set_alpha(top_alpha)
                        bottom_overlay.set_alpha(bottom_alpha)

                        surface.blit(top_overlay, (pos_x, pos_y))
                        surface.blit(bottom_overlay, (pos_x, pos_y + overlay_height))
                    else:

                        full_overlay = pygame.Surface((overlay_width, overlay_height*2), pygame.SRCALPHA)
                        full_overlay.fill(self.bare_hands_colour)
                        full_overlay.set_alpha(120)

                        surface.blit(full_overlay, (pos_x, pos_y))

    def draw_hover_text(self, surface):
        """Draw hover action text to the right of the card"""

        card_in_inventory = hasattr(self, 'in_inventory') and self.in_inventory

        is_defeated_monster = hasattr(self, 'is_defeated') and self.is_defeated

        if is_defeated_monster:
            if not (self.is_hovered and self.face_up):
                return

        elif card_in_inventory:

            if not (self.is_hovered and self.face_up):
                return
        else:

            show_for_inventory = self.face_up and self.can_add_to_inventory and self.is_hovered and self.hover_selection
            show_for_monster = self.face_up and self.can_show_attack_options and self.is_hovered and self.hover_selection

            if not (show_for_inventory or show_for_monster):
                return

        header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 32)
        body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)

        card_center_x = self.rect.centerx
        card_top = self.rect.top
        card_bottom = self.rect.bottom
        card_left = self.rect.left
        card_right = self.rect.right

        total_float_offset = 0
        if hasattr(self, 'idle_float_offset') and hasattr(self, 'hover_float_offset'):
            total_float_offset = self.idle_float_offset + self.hover_float_offset

        info_x = card_right + 10
        info_y = card_top - total_float_offset

        info_lines = []

        if self.type == "weapon":

            card_name = self.name if hasattr(self, 'name') and self.name else f"Weapon {self.value}"

            type_text = f"Weapon - {self.weapon_difficulty.upper()}"

            damage_text = f"Damage: {self.value}"

            action_text = ""
            action_colour = GOLD_COLOUR

            if hasattr(self, 'in_inventory') and self.in_inventory:

                if self.hover_selection == "top":
                    action_text = "DISCARD"
                    action_colour = (255, 120, 120)
                elif self.hover_selection == "bottom":
                    if self.type == "weapon":
                        action_text = "EQUIP"
                        action_colour = (120, 255, 120)
                    elif self.type == "potion":
                        action_text = "USE"
                        action_colour = (255, 220, 100)
                    else:

                        if self.type == "weapon":
                            action_text = "EQUIP or DISCARD"
                        elif self.type == "potion":
                            action_text = "USE or DISCARD"

            elif hasattr(self, 'is_equipped') and self.is_equipped:
                action_text = "DISCARD"
                action_colour = (255, 120, 120)

            else:
                    if self.hover_selection == "top":
                        action_text = "INVENTORY"
                        action_colour = (120, 120, 255)
                    elif self.hover_selection == "bottom":
                        if self.type == "weapon":
                            action_text = "EQUIP"
                            action_colour = (120, 255, 120)
                        elif self.type == "potion":
                            action_text = "USE"
                            action_colour = (255, 220, 100)

            info_lines = [
                {"text": card_name, "font": header_font, "colour": WHITE},
                {"text": type_text, "font": body_font, "colour": GOLD_COLOUR},
                {"text": damage_text, "font": body_font, "colour": WHITE}
            ]

            if action_text:
                info_lines.append({"text": action_text, "font": body_font, "colour": action_colour})

        elif self.type == "potion":

            card_name = self.name if hasattr(self, 'name') and self.name else f"Potion {self.value}"

            type_text = "Potion - Healing"

            heal_text = f"Restores {self.value} health"

            action_text = ""
            action_colour = GOLD_COLOUR

            if hasattr(self, 'in_inventory') and self.in_inventory:
                if self.hover_selection == "top":
                    action_text = "DISCARD"
                    action_colour = (255, 120, 120)
                elif self.hover_selection == "bottom":
                    action_text = "USE"
                    action_colour = (255, 220, 100)
                else:

                    action_text = "USE or DISCARD"

            else:
                if self.hover_selection == "top":
                    action_text = "INVENTORY"
                    action_colour = (120, 120, 255)
                elif self.hover_selection == "bottom":
                    action_text = "USE"
                    action_colour = (255, 220, 100)

            info_lines = [
                {"text": card_name, "font": header_font, "colour": WHITE},
                {"text": type_text, "font": body_font, "colour": GOLD_COLOUR},
                {"text": heal_text, "font": body_font, "colour": WHITE}
            ]

            if action_text:
                info_lines.append({"text": action_text, "font": body_font, "colour": action_colour})

        elif self.type == "monster":

            monster_name = self.name if hasattr(self, 'name') and self.name else f"Monster {self.value}"

            type_text = f"{self.monster_type} - Value {self.value}" if hasattr(self, 'monster_type') and self.monster_type else f"Monster - Value {self.value}"

            action_text = ""
            warning_text = ""
            action_colour = GOLD_COLOUR
            defeated_text = ""

            is_defeated_monster = False

            if hasattr(self, 'is_defeated') and self.is_defeated:
                is_defeated_monster = True

            if not is_defeated_monster and pygame.display.get_surface():

                try:

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

                defeated_text = "DEFEATED"
            else:

                if self.weapon_available and not self.weapon_attack_not_viable:
                    if self.hover_selection == "top":
                        action_text = "WEAPON ATTACK"
                        action_colour = (120, 170, 255)
                    elif self.hover_selection == "bottom":
                        action_text = "BARE HANDS"
                        action_colour = (255, 120, 120)
                elif self.weapon_available and self.weapon_attack_not_viable:
                    warning_text = "TOO POWERFUL FOR WEAPON"
                    action_text = "BARE HANDS ONLY"
                    action_colour = (255, 120, 120)
                else:
                    action_text = "BARE HANDS ONLY"
                    action_colour = (255, 120, 120)

            info_lines = [
                {"text": monster_name, "font": header_font, "colour": WHITE},
                {"text": type_text, "font": body_font, "colour": GOLD_COLOUR}
            ]

            if defeated_text:
                info_lines.append({"text": defeated_text, "font": body_font, "colour": (150, 150, 150)})

            elif warning_text:
                info_lines.append({"text": warning_text, "font": body_font, "colour": (255, 100, 100)})

            elif action_text:
                info_lines.append({"text": action_text, "font": body_font, "colour": action_colour})

        else:

            info_lines = [
                {"text": f"Card {self.suit.capitalize()} {self.value}", "font": header_font, "colour": WHITE},
                {"text": f"Type: {self.type.capitalize()}", "font": body_font, "colour": GOLD_COLOUR}
            ]

        min_info_width = 300

        max_text_width = min_info_width - 20

        rendered_texts = []
        for line in info_lines:
            text_surface = line["font"].render(line["text"], True, line["colour"])
            rendered_texts.append(text_surface)

            max_text_width = max(max_text_width, text_surface.get_width() + 20)

        info_width = max(min_info_width, max_text_width)

        total_text_height = 0
        line_spacing = 5
        for line in info_lines:
            total_text_height += line["font"].get_height() + line_spacing

        info_height = 10 + total_text_height + 5

        main_panel_right = pygame.display.get_surface().get_width() - 10
        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_right = self.main_panel.rect.right - 10

        if info_x + info_width > main_panel_right:
            info_x = card_left - info_width - 10

        main_panel_left = 10
        main_panel_bottom = pygame.display.get_surface().get_height() - 10

        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_left = self.main_panel.rect.left + 10
            main_panel_bottom = self.main_panel.rect.bottom - 10

        if info_x < main_panel_left:

            if card_bottom + info_height + 10 <= main_panel_bottom:

                info_x = card_center_x - (info_width // 2)
                info_y = card_bottom + 10
            else:

                info_x = card_center_x - (info_width // 2)
                info_y = card_top - info_height - 10

        main_panel_top = 10

        if hasattr(self, 'main_panel') and hasattr(self.main_panel, 'rect'):
            main_panel_top = self.main_panel.rect.top + 10

        info_x = max(main_panel_left, min(info_x, main_panel_right - info_width))
        info_y = max(main_panel_top, min(info_y, main_panel_bottom - info_height))

        panel_colour = (60, 50, 40)

        if hasattr(self, 'is_defeated') and self.is_defeated:
            panel_colour = (60, 50, 40)

        elif hasattr(self, 'in_inventory') and self.in_inventory:
            if self.hover_selection == "top":
                if self.type == "weapon":
                    panel_colour = (60, 100, 40)
                elif self.type == "potion":
                    panel_colour = (100, 90, 40)
            elif self.hover_selection == "bottom":
                panel_colour = (100, 40, 40)

        elif hasattr(self, 'is_equipped') and self.is_equipped:
            panel_colour = (100, 40, 40)

        elif self.type == "weapon" and self.hover_selection:
            if self.hover_selection == "top":
                panel_colour = (60, 50, 100)
            elif self.hover_selection == "bottom":
                panel_colour = (60, 100, 40)

        elif self.type == "potion" and self.hover_selection:
            if self.hover_selection == "top":
                panel_colour = (60, 50, 100)
            elif self.hover_selection == "bottom":
                panel_colour = (100, 90, 40)

        elif self.type == "monster":
            if self.weapon_attack_not_viable:
                panel_colour = (100, 40, 40)
            elif self.hover_selection == "top":
                panel_colour = (40, 60, 100)
            elif self.hover_selection == "bottom":
                panel_colour = (100, 40, 40)

        info_panel = Panel(
            (info_width, info_height),
            (info_x, info_y),
            colour=panel_colour,
            alpha=220,
            border_radius=8,
            dungeon_style=True
        )
        info_panel.draw(surface)

        current_y = info_y + 10
        for i, line in enumerate(info_lines):

            if i < len(rendered_texts):
                text_surface = rendered_texts[i]
            else:

                text_surface = line["font"].render(line["text"], True, line["colour"])

            text_rect = text_surface.get_rect(centerx=info_x + info_width//2, top=current_y)
            surface.blit(text_surface, text_rect)
            current_y = text_rect.bottom + line_spacing

    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        previous_selection = self.hover_selection

        self.hover_selection = None

        self.is_hovered = True

        if self.is_hovered and self.face_up:

            card_midpoint_y = self.rect.y + self.rect.height / 2

            is_defeated_monster = False

            if hasattr(self, 'is_defeated') and self.is_defeated:
                is_defeated_monster = True

            if not is_defeated_monster and pygame.display.get_surface():
                try:
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

                self.hover_selection = None

            elif hasattr(self, 'is_equipped') and self.is_equipped:

                self.hover_selection = "bottom"

            elif hasattr(self, 'in_inventory') and self.in_inventory:

                if mouse_pos[1] < card_midpoint_y:
                    self.hover_selection = "top"
                else:
                    self.hover_selection = "bottom"

            elif self.can_add_to_inventory:

                if hasattr(self, 'inventory_available') and self.inventory_available:

                    if mouse_pos[1] < card_midpoint_y:
                        self.hover_selection = "top"
                    else:
                        self.hover_selection = "bottom"
                else:

                    self.hover_selection = "bottom"
            elif self.can_show_attack_options:

                if self.weapon_available and not self.weapon_attack_not_viable:

                    if mouse_pos[1] < card_midpoint_y:
                        self.hover_selection = "top"
                    else:
                        self.hover_selection = "bottom"
                else:

                    self.hover_selection = "bottom"

        return previous_hover != self.is_hovered or previous_selection != self.hover_selection

def crop_center(img_path, output_path, target_width, target_height):
    """Crop an image to the specified dimensions, centered on the original image."""

    img = Image.open(img_path)
    width, height = img.size

    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    if left < 0 or top < 0 or right > width or bottom > height:

        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)

    cropped_img = img.crop((left, top, right, bottom))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    cropped_img.save(output_path)