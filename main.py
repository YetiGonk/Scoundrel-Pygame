"""
    Scoundrel - The 52-Card Roguelike Dungeon Crawler
    A roguelike card game where you navigate through multiple floors of monsters, 
    weapons, and potions.
"""

import math
import asyncio
import os
import sys
import random
import pygame
from pathlib import Path
from glob import glob
from PIL import Image
from pygame.locals import *

SCREEN_WIDTH = 1222
SCREEN_HEIGHT = 686
FLOOR_WIDTH = 750
FLOOR_HEIGHT = 617
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (64, 64, 64)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
CARD_RED = (171, 82, 54)

GOLD_COLOUR = (255, 215, 0)
GOLD_HIGHLIGHT = (255, 240, 120)
GOLD_BORDER = (184, 134, 11)
GOLD_TEXT = (255, 230, 150)

HEALTH_COLOUR_GOOD = (50, 180, 50)
HEALTH_COLOUR_WARNING = (220, 160, 40)
HEALTH_COLOUR_DANGER = (200, 50, 50)

HEALTH_GLOW_GOOD = (70, 220, 70, 40)
HEALTH_GLOW_WARNING = (240, 180, 60, 40)
HEALTH_GLOW_DANGER = (240, 90, 90, 40)

PANEL_DEFAULT_BORDER = (80, 60, 40)
PANEL_WOODEN = (80, 60, 30)
PANEL_WOODEN_BORDER = (130, 100, 40)
PANEL_HEALTH = (60, 30, 30)
PANEL_HEALTH_BORDER = (100, 50, 50)

EFFECT_HEALING_COLOUR = (60, 180, 80)
EFFECT_HEALING_PANEL = (40, 100, 50)
EFFECT_HEALING_BORDER = (70, 190, 90)
EFFECT_DAMAGE_COLOUR = (190, 60, 60)
EFFECT_DAMAGE_PANEL = (100, 40, 40)
EFFECT_DAMAGE_BORDER = (200, 70, 70)
EFFECT_GOLD_COLOUR = (220, 180, 50)
EFFECT_GOLD_PANEL = (100, 80, 30)
EFFECT_GOLD_BORDER = (230, 190, 60)
EFFECT_DEFAULT_COLOUR = (100, 100, 160)
EFFECT_DEFAULT_PANEL = (50, 50, 80)
EFFECT_DEFAULT_BORDER = (120, 120, 180)

CARD_WIDTH = 99
CARD_HEIGHT = 135

MENU_WIDTH = 600
MENU_HEIGHT = 150
MENU_POSITION = (
    SCREEN_WIDTH//2 - MENU_WIDTH//2,
    SCREEN_HEIGHT//2 - MENU_HEIGHT
)

WEAPON_POSITION = (486, 420)

MONSTER_STACK_OFFSET = (30, 10)
MONSTER_START_OFFSET = (150, 0)

RUN_WIDTH = 76
RUN_HEIGHT = 40
RUN_POSITION = (1050, 283)

DECK_POSITION = (SCREEN_WIDTH//2 - FLOOR_WIDTH//2 - CARD_WIDTH - 50, SCREEN_HEIGHT//2 - FLOOR_HEIGHT//2)

DISCARD_POSITION = (SCREEN_WIDTH//2 - FLOOR_WIDTH//2 - CARD_WIDTH - 50, FLOOR_HEIGHT - 145 - CARD_HEIGHT)

FLOOR_ROOM_TITLE_WIDTH = 350
FLOOR_ROOM_TITLE_HEIGHT = 70
FLOOR_ROOM_TITLE_POSITION = (SCREEN_WIDTH//2 - FLOOR_ROOM_TITLE_WIDTH//2, 50)

INVENTORY_PANEL_WIDTH = CARD_WIDTH + 60
INVENTORY_PANEL_HEIGHT = 400
INVENTORY_PANEL_X = (1.5 * SCREEN_WIDTH + FLOOR_WIDTH // 2) // 2 - (INVENTORY_PANEL_WIDTH // 2)
INVENTORY_PANEL_Y = SCREEN_HEIGHT // 2 - INVENTORY_PANEL_HEIGHT // 2

HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 24
HEALTH_BAR_POSITION = (20, SCREEN_HEIGHT - 30)

GOLD_BAR_WIDTH = 200
GOLD_BAR_HEIGHT = 24
GOLD_BAR_POSITION = (HEALTH_BAR_POSITION[0], HEALTH_BAR_POSITION[1] - GOLD_BAR_HEIGHT - 10)

EFFECT_ICON_SIZE = 40
EFFECT_ICON_SPACING = 10
EFFECT_START_POSITION = (SCREEN_WIDTH//2 - 100, 20)

PANEL_BORDER_RADIUS = 8
PANEL_ALPHA = 230
PANEL_BORDER_WIDTH = 2

BUTTON_PANEL_COLOUR = (60, 45, 35)
BUTTON_BORDER_WIDTH = 3
BUTTON_BORDER_RADIUS = 8
BUTTON_ALPHA = 250
BUTTON_GLOW_SIZE = 6
BUTTON_HOVER_GLOW_WHITE = (255, 255, 255, 30)
BUTTON_HOVER_GLOW_DARK = (0, 0, 0, 30)
BUTTON_HOVER_LIGHTEN = 0.3
BUTTON_ROUND_CORNER = 5

GOLD_CHANGE_DURATION = 2000
GOLD_PARTICLE_FADE_SPEED = (0.5, 1.5)
GOLD_PARTICLE_SPEED = (0.2, 0.6)
GOLD_PARTICLE_SIZE = (1, 2.5)
GOLD_PARTICLE_SPREAD = 5

EFFECT_PULSE_PERMANENT = (0.9, 0.1, 800)
EFFECT_PULSE_TEMPORARY = (0.8, 0.2, 200)
EFFECT_EXPIRE_THRESHOLD = 2000

STARTING_HEALTH = 20
MAX_HEALTH = 20

DECK_TOTAL_COUNT = 52
DECK_MONSTER_COUNT = (18, 25)
DECK_BLACK_VALUE_RANGE = (2, 14)
DECK_HEARTS_VALUE_RANGE = (2, 10)
DECK_DIAMONDS_VALUE_RANGE = (2, 10)

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

TITLE_FONT_SIZE = 64
HEADER_FONT_SIZE = 36
BODY_FONT_SIZE = 28
NORMAL_FONT_SIZE = 20

SUITS = ["diamonds", "hearts", "spades", "clubs"]

FLOOR_NAMES = {
    "first": [
        "Forgotten", "Ancient", "Haunted", "Cursed", "Twisted",
        "Shattered", "Bloody", "Forsaken", "Decaying", "Mournful",
        "Serpent's", "Witch's", "Dragon's", "Necromancer's", "Whispering",
        "Smouldering", "Frozen", "Sunken", "Pestilent", "Glittering",
        "Rotting", "Screaming", "Demon's", "Tainted", "Molten",
        "Corrupted", "Grim", "Spectral", "Shifting", "Shadowy",
        "Fractured", "Giant's", "Sorcerer's", "Abyssal", "Verdant",
        "Raven's", "Burning", "Drowned", "Wretched", "Crystalline",
        "Forbidden", "Baron's", "Endless", "Thorned", "Wailing",
        "Primal", "Queen's", "Arcane", "Infested", "Ruined"
    ],
    "second": [
        "Catacombs", "Forest", "Library", "Crypt", "Labyrinth",
        "Caverns", "Throne", "Sanctum", "Chambers", "Dungeon",
        "Keep", "Grotto", "Spire", "Pits", "Halls",
        "Temple", "Gardens", "Mines", "Abyss", "Wasteland",
        "Tower", "Fortress", "Vault", "Tombs", "Warren",
        "Marsh", "Basin", "Observatory", "Citadel", "Foundry",
        "Prison", "Arsenal", "Workshop", "Nexus", "Chasm",
        "Passage", "Hollows", "Rookery", "Barrows", "Laboratory",
        "Oubliette", "Colosseum"
    ]
}

FLOOR_TOTAL = 20

STARTING_ATTRIBUTES = {
    "life_points": 20,
    "max_life": 20,
}

""" Monster definitions for the roguelike elements of Scoundrel. """

MONSTER_RANKS = {
    2: "easy",
    3: "easy",
    4: "easy",
    5: "easy",
    6: "medium",
    7: "medium",
    8: "medium",
    9: "medium",
    10: "hard",
    11: "hard",
    12: "hard",
    13: "insane",
    14: "insane"
}

MONSTER_CLASSES = ["Animal", "Dragon", "Ghost", "Goblin", "Other", "Slime"]

MONSTER_CLASS_MAP = {
    "Animal": ["Basilisk", "Giant Ant", "Giant Brown Bats", "Giant Centipede", "Giant Fire Ant", "Giant Scorpion", "Giant Tarantula", "Giant Wolf Spider", "Lion", "Rat", "Rat King", "Snake", "Tiger", "Vampire Bats", "Wolf"],
    "Dragon": ["Armoured Dragon", "Black Dragon", "Black Drake", "Blue Dragon", "Blue Drake", "Chromatic Dragon", "Earth Dragon", "Energy Dragon", "Evil Dragon", "Gold Dragon", "Gold Drake", "Green Dragon", "Green Drake", "Magic Dragon", "Orange Dragon", "Orange Drake", "Red Dragon", "Red Drake", "Undead Dragon"],
    "Ghost": ["Banshee", "Ghost Dragon", "Painting Ghost", "Goblin Ghost", "Lantern Ghost", "Little Ghost", "Magic Ghost", "Three-Headed Ghost", "Will-O'-The-Wisp"],
    "Goblin": ["Goblin", "Goblin Archer", "Goblin King", "Goblin Magician", "Goblin Merchant", "Goblin Thief", "Goblin Warrior", "Three-Headed Troll"],
    "Other": ["Blue Myconid", "Centaur", "Cerberus", "Celestial", "Ent", "Fire Elemental", "Hydra", "Mummy", "Pegasus", "Stone Golem", "Unicorn"],
    "Slime": ["Black Slime", "Blue Slime", "Green Slime", "Orange Slime", "Ooze Dragon", "Slime King"]
}

MONSTER_DIFFICULTY_MAP = {
    "easy": [
        "monsters/Animal/Giant Brown Bats.png",
        "monsters/Animal/Giant Fruit Bats.png",
        "monsters/Animal/Rat.png",
        "monsters/Animal/Snake.png",
        "monsters/Dragon/Dragon Egg.png",
        "monsters/Ghost/Little Ghost.png",
        "monsters/Ghost/Will-O'-The-Wisp.png",
        "monsters/Goblin/Goblin.png",
        "monsters/Slime/Blue Slime.png",
        "monsters/Slime/Green Slime.png",
        "monsters/Slime/Orange Slime.png"
    ],
    "medium": [
        "monsters/Animal/Giant Ant.png",
        "monsters/Animal/Giant Centipede.png",
        "monsters/Animal/Giant Fire Ant.png",
        "monsters/Animal/Vampire Bats.png",
        "monsters/Animal/Wolf.png",
        "monsters/Dragon/Black Drake.png",
        "monsters/Dragon/Blue Drake.png",
        "monsters/Dragon/Gold Drake.png",
        "monsters/Dragon/Green Drake.png",
        "monsters/Dragon/Orange Drake.png",
        "monsters/Dragon/Red Drake.png",
        "monsters/Ghost/Banshee.png",
        "monsters/Ghost/Ghost.png",
        "monsters/Ghost/Painting Ghost.png",
        "monsters/Ghost/Lantern Ghost.png",
        "monsters/Goblin/Goblin Archer.png",
        "monsters/Goblin/Goblin Magician.png",
        "monsters/Goblin/Goblin Merchant.png",
        "monsters/Goblin/Goblin Thief.png",
        "monsters/Goblin/Goblin Warrior.png",
        "monsters/Other/Blue Myconid.png",
        "monsters/Other/Green Myconid.png",
        "monsters/Other/Orange Myconid.png",
        "monsters/Slime/Black Slime.png"
    ],
    "hard": [
        "monsters/Animal/Basilisk.png",
        "monsters/Animal/Giant Scorpion.png",
        "monsters/Animal/Giant Tarantula.png",
        "monsters/Animal/Giant Wolf Spider.png",
        "monsters/Animal/Lion.png",
        "monsters/Animal/Rat King.png",
        "monsters/Animal/Tiger.png",
        "monsters/Dragon/Black Dragon.png",
        "monsters/Dragon/Blue Dragon.png",
        "monsters/Dragon/Earth Dragon.png",
        "monsters/Dragon/Green Dragon.png",
        "monsters/Dragon/Orange Dragon.png",
        "monsters/Dragon/Red Dragon.png",
        "monsters/Ghost/Ghost Dragon.png",
        "monsters/Ghost/Goblin Ghost.png",
        "monsters/Ghost/Magic Ghost.png",
        "monsters/Ghost/Three-Headed Ghost.png",
        "monsters/Goblin/Goblin King.png",
        "monsters/Goblin/Troll.png",
        "monsters/Other/Centaur.png",
        "monsters/Other/Ent.png",
        "monsters/Other/Fire Elemental.png",
        "monsters/Other/Mummy.png",
        "monsters/Other/Pegasus.png",
        "monsters/Other/Stone Golem.png",
        "monsters/Other/Unicorn.png",
        "monsters/Slime/Slime King.png"
    ],
    "insane": [
        "monsters/Dragon/Armoured Dragon.png",
        "monsters/Dragon/Chromatic Dragon.png",
        "monsters/Dragon/Energy Dragon.png",
        "monsters/Dragon/Evil Dragon.png",
        "monsters/Dragon/Gold Dragon.png",
        "monsters/Dragon/Magic Dragon.png",
        "monsters/Dragon/Undead Dragon.png",
        "monsters/Goblin/Three-Headed Troll.png",
        "monsters/Other/Celestial.png",
        "monsters/Other/Cerberus.png",
        "monsters/Other/Hydra.png",
        "monsters/Slime/Ooze Dragon.png"
    ]
}

WEAPON_RANKS = {
    2: "novice",
    3: "novice",
    4: "novice",
    5: "novice",
    6: "intermediate",
    7: "intermediate",
    8: "intermediate",
    9: "intermediate",
    10: "adept",
    11: "adept",
    12: "adept",
    13: "master",
    14: "master"
}

WEAPON_RANK_MAP = {
    "novice": [
        "dagger",
        "shortsword",
        "shield",
        "axe",
        "mace",
        "spear",
    ],
    "intermediate": [
        "spear",
        "flail",
        "axe",
        "pickaxe",
        "club",
        "shortsword",
        "rapier",
    ],
    "adept": [
        "warhammer",
        "longbow",
        "battleaxe",
        "scythe",
        "halberd",
        "greatsword",
    ],
    "master": [
        "greatsword",
        "crossbow",
        "battleaxe",
        "warhammer",
    ]
}

WEAPON_DAMAGE_TYPES = {
    "shortsword": "slashing",
    "shield": "bludgeoning",
    "axe": "slashing",
    "warhammer": "bludgeoning",
    "flail": "bludgeoning",
    "club": "bludgeoning",
    "scythe": "slashing",
    "greatsword": "slashing",
    "crossbow": "piercing",
    "longbow": "piercing",
    "spear": "piercing",
    "dagger": "piercing",
    "halberd": "slashing",
    "battleaxe": "slashing",
    "mace": "bludgeoning",
    "rapier": "piercing",
    "pickaxe": "piercing"
}

class GameState:
    """Base class for all game states."""

    def __init__(self, game_manager):
        self.game_manager = game_manager

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, delta_time):
        pass

    def draw(self, surface):
        pass

class ResourceLoader:
    """Class for loading and caching game resources."""

    _image_cache = {}
    _font_cache = {}

    @classmethod
    def load_image(cls, name, scale=1, cache=True):
        cache_key = f"{name}_{scale}"
        if cache and cache_key in cls._image_cache:
            return cls._image_cache[cache_key]

        try:
            image = pygame.image.load(relative_to_assets(name))

            if scale != 1:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)

            if cache:
                cls._image_cache[cache_key] = image

            return image
        except pygame.error as e:
            return pygame.Surface((CARD_WIDTH, CARD_HEIGHT))

    @classmethod
    def load_font(cls, name, size):
        cache_key = f"{name}_{size}"
        if cache_key in cls._font_cache:
            return cls._font_cache[cache_key]

        try:
            font = pygame.font.Font(relative_to_assets(name), size)

            cls._font_cache[cache_key] = font

            return font
        except pygame.error as e:
            return pygame.font.SysFont(None, size)

    @classmethod
    def clear_cache(cls):
        cls._image_cache.clear()
        cls._font_cache.clear()

class AnimationController:
    """Manages all animations in the game."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def animate_card_to_discard(self, card):
        """Animate a card being destroyed and appearing in the discard pile."""

        if card.type == "monster":
            effect_type = "slash"
        elif card.type == "weapon":
            effect_type = "shatter"
        elif card.type == "potion":
            effect_type = "burn"
        else:
            effect_type = random.choice(["slash", "burn", "shatter"])

        destroy_anim = DestructionAnimation(
            card,
            effect_type,
            duration=0.5,
            on_complete=lambda: self.materialise_card_at_discard(card)
        )

        self.playing_state.animation_manager.add_animation(destroy_anim)

    def materialise_card_at_discard(self, card):
        """Materialise the card at the discard pile position."""

        card.update_position(self.playing_state.discard_pile.position)

        materialise_anim = MaterialiseAnimation(
            card,
            self.playing_state.discard_pile.position,
            effect_type="sparkle",
            duration=0.3,
            on_complete=lambda: self.playing_state.room_manager.remove_and_discard(card)
        )

        self.playing_state.animation_manager.add_animation(materialise_anim)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None,
        on_complete=None):
        """Create a simple, direct animation for card movement with optional callback."""
        if easing is None:
            easing = EasingFunctions.ease_out_quad

        animation = MoveAnimation(
            card,
            card.rect.topleft,
            target_pos,
            duration,
            easing,
            on_complete
        )

        self.playing_state.animation_manager.add_animation(animation)

    def position_monster_stack(self, preserve_positions=False):
        """Position defeated monsters in a stack."""
        if not self.playing_state.defeated_monsters or "node" not in self.playing_state.equipped_weapon:
            return

        weapon_card = self.playing_state.equipped_weapon["node"]
        is_default_weapon_position = (weapon_card.rect.x == WEAPON_POSITION[0] and weapon_card.rect.y == WEAPON_POSITION[1])

        start_x = weapon_card.rect.x + MONSTER_START_OFFSET[0]

        for i, monster in enumerate(self.playing_state.defeated_monsters):

            has_valid_position = hasattr(monster, 'rect') and monster.rect.x > 0 and monster.rect.y > 0

            new_stack_position = (
                start_x + i * MONSTER_STACK_OFFSET[0],
                weapon_card.rect.y + MONSTER_STACK_OFFSET[1] * i
            )

            if not has_valid_position or not preserve_positions:
                self.animate_card_movement(monster, new_stack_position)

        if is_default_weapon_position:
            new_weapon_position = (
                weapon_card.rect.x - MONSTER_STACK_OFFSET[1]*2,
                weapon_card.rect.y
            )
            self.animate_card_movement(weapon_card, new_weapon_position)

    def schedule_delayed_animation(self, delay, callback):
        """Schedule an animation to start after a delay."""

        timer = Animation(delay, on_complete=callback)
        self.playing_state.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        """Start the flip animation for a card."""
        card.start_flip()

    def animate_health_change(self, is_damage, amount):
        """Create animation for health change."""

        health_display_x = self.playing_state.deck.rect.x + 100
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y - 30

        health_anim = HealthChangeAnimation(
            is_damage,
            amount,
            (health_display_x, health_display_y),
            self.playing_state.body_font
        )

        self.playing_state.animation_manager.add_animation(health_anim)

    def animate_card_to_inventory(self, card):
        """Animate a card moving to its position in the inventory."""

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        card_scale = 1.0

        card.update_scale(card_scale)

        card.in_inventory = True

        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)

        inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)

        num_cards = len(self.playing_state.inventory)

        if num_cards == 1:

            inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
        elif num_cards == 2:

            existing_card = self.playing_state.inventory[0]
            top_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)

            if existing_card.rect.y != top_y:
                self.animate_card_movement(existing_card, (inventory_x, top_y))

            inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)

        inventory_pos = (inventory_x, inventory_y)

        self.animate_card_movement(card, inventory_pos, on_complete=lambda: self.playing_state.position_inventory_cards())

class Animation:
    """Base class for animations."""

    def __init__(self, duration, on_complete=None):
        self.duration = duration
        self.elapsed_time = 0
        self.is_completed = False
        self.on_complete = on_complete

    def update(self, delta_time):
        if self.is_completed:
            return True

        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.elapsed_time = self.duration
            self.is_completed = True
            if self.on_complete:
                self.on_complete()
            return True

        return False

    def reset(self):
        self.elapsed_time = 0
        self.is_completed = False

    def get_progress(self):
        return min(1.0, self.elapsed_time / self.duration)

class EasingFunctions:
    """Static class containing various easing functions."""

    @staticmethod
    def linear(progress):
        return progress

    @staticmethod
    def ease_in_quad(progress):
        return progress * progress

    @staticmethod
    def ease_out_quad(progress):
        return 1 - (1 - progress) * (1 - progress)

    @staticmethod
    def ease_in_out_quad(progress):
        if progress < 0.5:
            return 2 * progress * progress
        else:
            return 1 - pow(-2 * progress + 2, 2) / 2

class MoveAnimation(Animation):
    """Animation for moving an object from one position to another."""

    def __init__(self, target_object, start_pos, end_pos, duration, easing_function=EasingFunctions.ease_out_quad, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.easing_function = easing_function

    def update(self, delta_time):
        completed = super().update(delta_time)

        progress = self.easing_function(self.get_progress())
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

        self.target_object.update_position((current_x, current_y))

        return completed

class DestructionAnimation(Animation):
    """Animation for making a card disappear with effects."""

    def __init__(self, target_object, effect_type, duration=0.3, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.effect_type = effect_type
        self.original_scale = 1.0
        self.original_position = target_object.rect.topleft
        self.particles = []

        if effect_type == "slash":

            self.slash_angle = random.randint(25, 65)
            self.slash_direction = 1 if random.random() > 0.5 else -1
            self.slash_width = 4
            self.slash_colour = (200, 200, 200)

        elif effect_type == "burn":

            for _ in range(20):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(3, 8),
                    'speed_y': -random.random() * 2 - 1,
                    'colour': (
                        random.randint(200, 255),
                        random.randint(50, 150),
                        0
                    )
                })

        elif effect_type == "shatter":

            for _ in range(15):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(5, 15),
                    'speed_x': (random.random() - 0.5) * 6,
                    'speed_y': (random.random() - 0.5) * 6,
                    'rotation': random.randint(0, 360),
                    'colour': (100, 200, 255)
                })

    def draw(self, surface):
        progress = self.get_progress()

        if self.effect_type == "slash":
            if progress < 0.4:

                self.target_object.draw(surface)

                slash_progress = progress / 0.4
                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                slash_length = self.target_object.rect.width * 1.4

                offset = (slash_progress - 0.5) * self.target_object.rect.width * 1.5

                start_x = center_x - slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                start_y = center_y - slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3

                end_x = center_x + slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                end_y = center_y + slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3

                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width + 2
                )

                pygame.draw.line(
                    surface,
                    self.slash_colour,
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width
                )

                for i in range(5):
                    spark_pos_x = start_x + (end_x - start_x) * (i / 4)
                    spark_pos_y = start_y + (end_y - start_y) * (i / 4)
                    spark_size = random.randint(1, 3)
                    pygame.draw.circle(
                        surface,
                        (255, 255, 255),
                        (int(spark_pos_x), int(spark_pos_y)),
                        spark_size
                    )

            elif progress < 0.55:

                self.target_object.draw(surface)

                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                cut_length = self.target_object.rect.width * 1.2

                start_x = center_x - cut_length/2 * math.cos(math.radians(self.slash_angle))
                start_y = center_y - cut_length/2 * math.sin(math.radians(self.slash_angle))

                end_x = center_x + cut_length/2 * math.cos(math.radians(self.slash_angle))
                end_y = center_y + cut_length/2 * math.sin(math.radians(self.slash_angle))

                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    2
                )

            else:

                split_progress = (progress - 0.55) / 0.45
                split_distance = 120 * math.pow(split_progress, 1.5)

                cut_height = self.target_object.rect.height * 0.5

                rotation = 5 * split_progress * self.slash_direction

                top_half = self.target_object.texture.subsurface(
                    (0, 0, self.target_object.rect.width, int(cut_height))
                )

                if rotation != 0:
                    top_half = pygame.transform.rotate(top_half, -rotation)

                surface.blit(
                    top_half,
                    (
                        self.target_object.rect.x - split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y - split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )

                bottom_half = self.target_object.texture.subsurface(
                    (0, int(cut_height),
                     self.target_object.rect.width, self.target_object.rect.height - int(cut_height))
                )

                if rotation != 0:
                    bottom_half = pygame.transform.rotate(bottom_half, rotation)

                surface.blit(
                    bottom_half,
                    (
                        self.target_object.rect.x + split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y + cut_height + split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )

                if split_progress < 0.7:
                    center_x = self.target_object.rect.centerx
                    center_y = self.target_object.rect.centery

                    for _ in range(3):
                        particle_x = center_x + (random.random() - 0.5) * 30
                        particle_y = center_y + (random.random() - 0.5) * 10
                        particle_size = random.randint(1, 3)

                        pygame.draw.circle(
                            surface,
                            (220, 220, 220),
                            (int(particle_x), int(particle_y)),
                            particle_size
                        )

        elif self.effect_type == "burn":
            if progress < 0.4:

                scale = 1.0 - progress * 0.2
                self.target_object.update_scale(scale)
                self.target_object.draw(surface)

                for particle in self.particles:
                    size = int(particle['size'] * (1 - progress * 2))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['colour'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] + progress * 40 * particle['speed_y'])
                            ),
                            size
                        )
            elif progress < 0.7:
                burn_progress = (progress - 0.4) / 0.3

                height = int(self.target_object.rect.height * (1 - burn_progress))
                if height > 0:
                    card_texture = self.target_object.texture.subsurface(
                        (0, 0, self.target_object.rect.width, height)
                    )
                    surface.blit(card_texture, (self.target_object.rect.x, self.target_object.rect.y))

                for particle in self.particles:
                    size = int(particle['size'] * (1 - burn_progress))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['colour'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] - burn_progress * 60)
                            ),
                            size
                        )

            else:
                fade_progress = (progress - 0.7) / 0.3

                for particle in self.particles:
                    alpha = int(255 * (1 - fade_progress))
                    if alpha > 0:
                        particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
                        colour_with_alpha = (particle['colour'][0], particle['colour'][1], particle['colour'][2], alpha)
                        pygame.draw.circle(
                            particle_surface,
                            colour_with_alpha,
                            (particle['size'], particle['size']),
                            particle['size']
                        )
                        surface.blit(
                            particle_surface,
                            (
                                int(self.target_object.rect.x + particle['x'] - particle['size']),
                                int(self.target_object.rect.y + particle['y'] - 80 * fade_progress - particle['size'])
                            )
                        )

        elif self.effect_type == "shatter":
            if progress < 0.3:
                shake_amount = 3 * math.sin(progress * 20)
                shake_x = self.original_position[0] + shake_amount
                shake_y = self.original_position[1] + shake_amount * 0.5
                self.target_object.update_position((shake_x, shake_y))
                self.target_object.draw(surface)
            else:
                shatter_progress = (progress - 0.3) / 0.7

                if shatter_progress < 0.5:
                    fade_alpha = int(255 * (1 - shatter_progress * 2))
                    if fade_alpha > 0:
                        original_texture = self.target_object.texture.copy()

                        faded_texture = pygame.Surface(original_texture.get_size(), pygame.SRCALPHA)
                        faded_texture.fill((255, 255, 255, fade_alpha))

                        faded_texture.blit(original_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        surface.blit(faded_texture, self.target_object.rect.topleft)

                for particle in self.particles:

                    current_x = particle['x'] + particle['speed_x'] * 100 * shatter_progress
                    current_y = particle['y'] + particle['speed_y'] * 100 * shatter_progress

                    rotation = particle['rotation'] + shatter_progress * 360
                    scale = 1.0 - shatter_progress * 0.8

                    size = int(particle['size'] * scale)
                    if size > 2:
                        fragment = pygame.Surface((size, size), pygame.SRCALPHA)
                        pygame.draw.rect(
                            fragment,
                            particle['colour'],
                            pygame.Rect(0, 0, size, size)
                        )

                        fragment = pygame.transform.rotate(fragment, rotation)

                        alpha = int(255 * (1 - shatter_progress))
                        if alpha > 0:
                            fragment.set_alpha(alpha)
                            surface.blit(
                                fragment,
                                (
                                    int(self.target_object.rect.x + current_x - size/2),
                                    int(self.target_object.rect.y + current_y - size/2)
                                )
                            )

    def update(self, delta_time):
        completed = super().update(delta_time)

        if completed:
            self.target_object.is_visible = False

        return completed

class MaterialiseAnimation(Animation):
    """Animation for making a card appear at a destination."""

    def __init__(self, target_object, position, effect_type="sparkle", duration=0.3, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.position = position
        self.effect_type = effect_type
        self.particles = []

        self.target_object.update_position(position)
        self.target_object.is_visible = True

        if effect_type == "sparkle":

            for _ in range(20):
                self.particles.append({
                    'x': random.randint(-20, target_object.rect.width + 20),
                    'y': random.randint(-20, target_object.rect.height + 20),
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 1,
                    'angle': random.random() * 360,
                    'colour': (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(100, 200)
                    )
                })

    def draw(self, surface):
        progress = self.get_progress()

        if self.effect_type == "sparkle":

            if progress < 0.7:

                scale = 0.2 + progress * 1.1
                if scale > 1.0 and progress > 0.6:
                    scale = 1.0 + (0.7 - progress) * 2

                self.target_object.update_scale(scale)

                alpha = int(min(255, progress * 2 * 255))
                card_texture = self.target_object.texture.copy()
                card_texture.set_alpha(alpha)
                surface.blit(card_texture, self.target_object.rect.topleft)
            else:

                self.target_object.update_scale(1.0)
                self.target_object.draw(surface)

            for particle in self.particles:

                radius = particle['speed'] * progress * 50
                x = self.target_object.rect.centerx + particle['x'] + math.cos(math.radians(particle['angle'])) * radius
                y = self.target_object.rect.centery + particle['y'] + math.sin(math.radians(particle['angle'])) * radius

                if progress < 0.5:
                    size = particle['size'] * progress * 2
                else:
                    size = particle['size'] * (1 - (progress - 0.5) * 2)

                if size > 0:
                    pygame.draw.circle(
                        surface,
                        particle['colour'],
                        (int(x), int(y)),
                        int(size)
                    )

    def update(self, delta_time):
        completed = super().update(delta_time)

        if completed:
            self.target_object.is_visible = True
            self.target_object.update_scale(1.0)

        return completed

class HealthChangeAnimation(Animation):
    """Animation for displaying health changes with effects."""

    def __init__(self, is_damage, amount, position, font, duration=0.8, on_complete=None):
        super().__init__(duration, on_complete)
        self.is_damage = is_damage
        self.amount = amount
        self.position = position
        self.font = font
        self.particles = []

        num_particles = min(20, max(5, abs(amount) * 2))
        for _ in range(num_particles):
            self.particles.append({
                'x': random.randint(-10, 10),
                'y': random.randint(-5, 5),
                'speed_x': (random.random() - 0.5) * 5,
                'speed_y': -random.random() * 8 - 2,
                'size': random.randint(3, 7),
                'fade_speed': random.random() * 0.3 + 0.7
            })

    def draw(self, surface):
        progress = self.get_progress()

        if progress < 0.4:
            scale = 1.0 + progress * 0.5
            alpha = int(255 * min(1.0, progress * 3))

        elif progress < 0.7:
            scale = 1.2
            alpha = 255

        else:
            fade_progress = (progress - 0.7) / 0.3
            scale = 1.2 - fade_progress * 0.2
            alpha = int(255 * (1 - fade_progress))

        if self.is_damage:
            colour = (255, 80, 80)
            text_prefix = "-"
        else:
            colour = (80, 255, 80)
            text_prefix = "+"

        text = self.font.render(f"{text_prefix}{abs(self.amount)}", True, colour)

        if scale != 1.0:
            orig_size = text.get_size()
            text = pygame.transform.scale(
                text,
                (int(orig_size[0] * scale), int(orig_size[1] * scale))
            )

        if alpha < 255:
            text.set_alpha(alpha)

        text_rect = text.get_rect(center=(
            self.position[0],
            self.position[1] - 40 * progress
        ))
        surface.blit(text, text_rect)

        for particle in self.particles:

            particle_x = self.position[0] + particle['x'] + particle['speed_x'] * progress * 60
            particle_y = self.position[1] + particle['y'] + particle['speed_y'] * progress * 60

            particle_alpha = int(255 * (1 - progress * particle['fade_speed']))

            particle_size = max(1, int(particle['size'] * (1 - progress * 0.5)))

            if particle_alpha <= 10 or particle_size <= 0:
                continue

            particle_colour = colour + (particle_alpha,)
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_colour, (particle_size, particle_size), particle_size)
            surface.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))

class AnimationManager:
    """Manager for handling multiple animations."""

    def __init__(self):
        self.animations = []
        self.effect_animations = []
        self.ui_animations = []

    def add_animation(self, animation):
        self.animations.append(animation)

        if isinstance(animation, (DestructionAnimation, MaterialiseAnimation)):
            self.effect_animations.append(animation)
        elif isinstance(animation, (HealthChangeAnimation)):
            self.ui_animations.append(animation)

    def update(self, delta_time):

        self.animations = [anim for anim in self.animations if not anim.update(delta_time)]

        self.effect_animations = [anim for anim in self.effect_animations if not anim.is_completed]
        self.ui_animations = [anim for anim in self.ui_animations if not anim.is_completed]

    def draw_effects(self, surface):

        for animation in self.effect_animations:
            animation.draw(surface)

    def draw_ui_effects(self, surface):

        for animation in self.ui_animations:
            animation.draw(surface)

    def clear(self):
        self.animations.clear()
        self.effect_animations.clear()
        self.ui_animations.clear()

    def is_animating(self):
        return len(self.animations) > 0

class Button:
    def __init__(self, rect, text, font, text_colour=BLACK, bg_colour=LIGHT_GRAY, border_colour=BLACK,
                dungeon_style=False, panel_colour=None, border_width=None, callback=None):

        if panel_colour is None:
            panel_colour = BUTTON_PANEL_COLOUR
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

        self.text_surface = font.render(text, True, text_colour)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        if self.dungeon_style:
            self._create_dungeon_panel()

    def _create_dungeon_panel(self):
        """Create a dungeon-styled panel for the button"""
        try:

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

            self.dungeon_style = False

    def update_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_colour)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def check_hover(self, mouse_pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if previous_hover != self.is_hovered and self.dungeon_style and self.panel:
            if self.is_hovered:

                lighter_border = self._lighten_colour(self.border_colour, BUTTON_HOVER_LIGHTEN)
                self.panel.update_style(True, self.border_width, lighter_border)
            else:

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

            self.panel.draw(surface)

            if self.is_hovered:

                glow_size = BUTTON_GLOW_SIZE
                glow_surface = pygame.Surface(
                    (self.text_surface.get_width() + glow_size*2,
                        self.text_surface.get_height() + glow_size*2
                    ),
                    pygame.SRCALPHA
                )

                if self.text_colour == WHITE or sum(self.text_colour) > 400:
                    glow_colour = BUTTON_HOVER_GLOW_WHITE
                else:
                    glow_colour = BUTTON_HOVER_GLOW_DARK

                pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
                glow_rect = glow_surface.get_rect(center=self.text_rect.center)
                surface.blit(glow_surface, glow_rect)

            surface.blit(self.text_surface, self.text_rect)
        else:

            pygame.draw.rect(surface, self.bg_colour, self.rect, border_radius=BUTTON_ROUND_CORNER)

            pygame.draw.rect(surface, self.border_colour, self.rect, 2, border_radius=BUTTON_ROUND_CORNER)

            surface.blit(self.text_surface, self.text_rect)

class CardActionManager:
    """Manages card-related actions such as attacking monsters, using equipment, and potions."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def resolve_card(self, card, event_pos=None):
        """Process a card that has been clicked by the player."""
        if (not card.face_up or card.is_flipping or
                self.playing_state.animation_manager.is_animating()):
            return

        self.playing_state.ran_last_turn = False
        card.is_selected = True

        if card.can_add_to_inventory and event_pos:
            inventory_is_full = len(self.playing_state.inventory) >= self.playing_state.MAX_INVENTORY_SIZE
            card.inventory_available = not inventory_is_full

            center_x = card.rect.centerx

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            center_y = card.rect.centery - total_float_offset

            if not inventory_is_full and event_pos[1] < center_y:
                self.add_to_inventory(card)
                return

        elif card.can_show_attack_options and event_pos:
            center_x = card.rect.centerx

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            center_y = card.rect.centery - total_float_offset

            if card.weapon_available and not getattr(card, 'weapon_attack_not_viable', False):
                if event_pos[1] < center_y:
                    self.attack_monster(card)
                    return
                else:
                    self.attack_barehanded(card)
                    return
            else:
                self.attack_barehanded(card)
                return

        if card.type == "monster":
            self.attack_barehanded(card)
        elif card.type == "weapon":
            self.equip_weapon(card)
        elif card.type == "potion":
            self.use_potion(card)

    def attack_barehanded(self, monster):
        """Process player attacking a monster card with bare hands (takes full damage)."""
        monster_value = monster.value
        self.playing_state.room.remove_card(monster)

        if monster_value > 0:
            self.playing_state.change_health(-monster_value)

        self.playing_state.animate_card_to_discard(monster)
        self.playing_state.show_message(f"Attacked {monster.name} bare-handed! Took full damage.")

        if len(self.playing_state.room.cards) > 0:
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def attack_monster(self, monster):
        """Process player attacking a monster card with equipped weapon."""
        monster_value = monster.value
        self.playing_state.room.remove_card(monster)

        if self.playing_state.equipped_weapon:
            weapon_node = self.playing_state.equipped_weapon.get("node", None)
            weapon_value = self.playing_state.equipped_weapon.get("value", 0)

            if self.playing_state.defeated_monsters:
                if self.playing_state.defeated_monsters[-1].value > monster_value:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0

                    if damage > 0:
                        self.playing_state.change_health(-damage)

                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:

                    if monster_value > 0:
                        self.playing_state.change_health(-monster_value)

                        self.playing_state.animate_card_to_discard(monster)
            else:
                if monster_value <= weapon_value:
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    monster.is_defeated = True

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0

                    if damage > 0:
                        self.playing_state.change_health(-damage)

                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1

                    monster.is_defeated = True

                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
        else:

            if monster_value > 0:
                self.playing_state.change_health(-monster_value)

            self.playing_state.animate_card_to_discard(monster)

        if len(self.playing_state.room.cards) > 0:

            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def equip_weapon(self, weapon):
        """Equip a weapon card."""

        old_weapon = self.playing_state.equipped_weapon.get("node", None)
        old_monsters = self.playing_state.defeated_monsters.copy()

        self.playing_state.room.remove_card(weapon)

        weapon.is_equipped = True

        self.playing_state.equipped_weapon = {
            "suit": weapon.suit,
            "value": weapon.value,
            "node": weapon,
            "difficulty": weapon.weapon_difficulty,
        }
        self.playing_state.defeated_monsters = []

        weapon.z_index = self.playing_state.z_index_counter
        self.playing_state.z_index_counter += 1

        self.playing_state.animate_card_movement(weapon, WEAPON_POSITION)

        self.playing_state.show_message(f"Equipped {weapon.name}")

        if old_weapon or old_monsters:
            for i, monster in enumerate(old_monsters):

                delay = 0.08 * i
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=monster: self.playing_state.animate_card_to_discard(card)
                )

            if old_weapon:
                delay = 0.08 * len(old_monsters)
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda: self.playing_state.animate_card_to_discard(old_weapon)
                )

    def use_potion(self, potion):
        """Use a potion card to heal the player."""

        self.playing_state.change_health(potion.value)

        self.playing_state.room.remove_card(potion)

        self.playing_state.animate_card_to_discard(potion)

        if len(self.playing_state.room.cards) > 0:

            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

    def add_to_inventory(self, card):
        """Add a card to the player's inventory if space is available."""
        if len(self.playing_state.inventory) >= self.playing_state.MAX_INVENTORY_SIZE:

            return False

        card.is_selected = True

        card.in_inventory = True

        self.playing_state.room.remove_card(card)

        self.playing_state.inventory.append(card)

        self.playing_state.animate_card_to_inventory(card)

        if len(self.playing_state.room.cards) > 0:
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True,
                    animation_manager=self.playing_state.animation_manager
                )
            )

        return True

    def use_inventory_card(self, card, event_pos=None):
        """Use a card from the inventory with optional click position to determine action."""
        if card in self.playing_state.inventory:

            card.is_selected = True

            discard_only = False

            if event_pos:

                center_x = card.rect.centerx

                total_float_offset = 0
                if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                    total_float_offset = card.idle_float_offset + card.hover_float_offset

                center_y = card.rect.centery - total_float_offset

                if event_pos[1] < center_y:

                    discard_only = True
                    card.hover_selection = "top"
                else:

                    discard_only = False
                    card.hover_selection = "bottom"

            card.in_inventory = False

            self.playing_state.inventory.remove(card)

            self.playing_state.position_inventory_cards()

            if card.type == "weapon":
                if discard_only:

                    self.playing_state.show_message(f"{card.name} discarded")

                    self.playing_state.animate_card_to_discard(card)
                else:

                    card.update_scale(1.0)

                    self.playing_state.room.add_card(card)

                    self.equip_weapon(card)
            elif card.type == "potion":
                if discard_only:

                    self.playing_state.show_message(f"{card.name} discarded")

                    self.playing_state.animate_card_to_discard(card)
                else:

                    self.playing_state.change_health(card.value)

                    self.playing_state.show_message(f"Used {card.name}. Restored {card.value} health.")

                    self.playing_state.animate_card_to_discard(card)
            else:

                self.playing_state.show_message(f"{card.name} discarded")
                self.playing_state.animate_card_to_discard(card)

    def discard_equipped_weapon(self):
        """Discard the currently equipped weapon."""
        if self.playing_state.equipped_weapon and "node" in self.playing_state.equipped_weapon:
            weapon = self.playing_state.equipped_weapon["node"]

            self.playing_state.equipped_weapon = {}

            weapon.is_equipped = False

            self.playing_state.show_message(f"{weapon.name} discarded")

            self.playing_state.animate_card_to_discard(weapon)

            for monster in self.playing_state.defeated_monsters:
                self.playing_state.animate_card_to_discard(monster)

            self.playing_state.defeated_monsters = []

            return True
        return False

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

class Deck:
    """ Represents a deck of cards in the game. """

    def __init__(self, floor):

        self.floor = floor
        self.position = DECK_POSITION
        self.cards = []
        self.card_stack = []
        self.card_spacing = (0, 3)
        self.texture = ResourceLoader.load_image("cards/card_back.png")
        self.texture = pygame.transform.scale(self.texture, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def initialise_deck(self):
        """Initialise the deck for a floor."""
        self.cards = []

        self._generate_random_deck()

        random.shuffle(self.cards)
        self.initialise_visuals()

    def _generate_random_deck(self):
        """Generate a random deck"""
        monster_count = random.randint(DECK_MONSTER_COUNT[0], DECK_MONSTER_COUNT[1])

        weapon_potion_count = DECK_TOTAL_COUNT - monster_count

        if weapon_potion_count % 2 != 0:
            weapon_potion_count -= 1
            monster_count += 1

        weapon_count = potion_count = weapon_potion_count // 2

        card_counts = {}

        self._add_cards_to_deck(["clubs", "spades"], range(DECK_BLACK_VALUE_RANGE[0], DECK_BLACK_VALUE_RANGE[1] + 1), monster_count, card_counts)

        self._add_cards_to_deck(["diamonds"], range(DECK_DIAMONDS_VALUE_RANGE[0], DECK_DIAMONDS_VALUE_RANGE[1] + 1), weapon_count, card_counts)

        self._add_cards_to_deck(["hearts"], range(DECK_HEARTS_VALUE_RANGE[0], DECK_HEARTS_VALUE_RANGE[1] + 1), potion_count, card_counts)

    def _add_cards_to_deck(self, suits, value_range, count, card_counts):
        """Add cards to the deck while respecting the duplicate limit."""
        cards_added = 0

        while cards_added < count:

            suit = random.choice(suits)
            value = random.choice(list(value_range))

            card_key = (suit, value)
            current_count = card_counts.get(card_key, 0)

            if current_count < 4:

                self.cards.append({"suit": suit, "value": value, "floor_type": self.floor})

                card_counts[card_key] = current_count + 1
                cards_added += 1

    def initialise_visuals(self):
        self.card_stack = []
        for i in range(len(self.cards)):
            card_pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
            self.card_stack.append(card_pos)

    def draw_card(self):
        if self.cards:
            return self.cards.pop(0)
        return None

    def add_to_bottom(self, card_data):
        self.cards.append(card_data)

    def draw(self, surface):

        if self.card_stack:
            for i, pos in enumerate(self.card_stack):
                surface.blit(self.texture, pos)
        else:

            pygame.draw.rect(surface, GRAY, self.rect, 2)

class DiscardPile:
    """Represents a discard pile in the game."""

    def __init__(self):
        self.position = DISCARD_POSITION
        self.cards = []
        self.card_spacing = (0, -3)
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def add_card(self, card):
        self.cards.append(card)

    def get_card_count(self):
        return len(self.cards)

    def draw(self, surface):
        if self.cards:
            for i, card in enumerate(self.cards):
                pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
                surface.blit(card.texture, pos)
        else:

            pygame.draw.rect(surface, GRAY, self.rect, 2)

def extract_weapons():

    output_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/individual"
    os.makedirs(output_dir, exist_ok=True)

    dark_colour = (171, 82, 54)
    light_colour = (214, 123, 86)

    def process_weapon(source_img, x, y, width, height, index):

        weapon = source_img.crop((x, y, x + width, y + height))

        new_weapon = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for py in range(height):
            for px in range(width):

                pixel = weapon.getpixel((px, py))

                if (120 < pixel[0] < 160 and
                    100 < pixel[1] < 140 and
                    70 < pixel[2] < 110):
                    continue

                if (130 < pixel[0] < 170 and
                    110 < pixel[1] < 150 and
                    80 < pixel[2] < 120):
                    continue

                if len(pixel) == 4 and pixel[3] == 0:
                    continue

                brightness = sum(pixel[:3]) / 3

                if brightness > 180:
                    new_colour = light_colour
                else:
                    new_colour = dark_colour

                alpha = pixel[3] if len(pixel) == 4 else 255

                new_weapon.putpixel((px, py), (*new_colour, alpha))

        output_path = os.path.join(output_dir, f"weapon{index}.png")
        new_weapon.save(output_path)

    weapons1_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons1.png"
    weapons1 = Image.open(weapons1_path).convert("RGBA")

    for row in range(3):
        for col in range(3):
            index = row * 3 + col + 1
            process_weapon(weapons1, col * 32, row * 32, 32, 32, index)

    weapons2_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons2.jpg"
    weapons2 = Image.open(weapons2_path).convert("RGBA")

    weapon_positions = [
        (12, 11, 32, 32),
        (60, 10, 32, 32),
        (114, 10, 32, 32),
        (12, 58, 32, 32),
        (60, 58, 32, 32),
        (114, 58, 32, 32),
        (12, 106, 32, 32),
        (60, 106, 32, 32),
        (114, 106, 32, 32)
    ]

    for i, (x, y, w, h) in enumerate(weapon_positions):
        index = i + 10
        process_weapon(weapons2, x, y, w, h, index)

class FloorManager:
    """Manages the different floors in a run."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.floors = [f"{random.choice(FLOOR_NAMES['first'])} {random.choice(FLOOR_NAMES['second'])}" for _ in range(FLOOR_TOTAL)]
        self.current_floor_index = 0
        self.current_room = 1
        self.total_floors = FLOOR_TOTAL

    def initialise_run(self):
        """Initialise a new run with randomised floor order."""
        self.current_floor_index = 0

        self.current_room = 1
        return self.get_current_floor()

    def get_current_floor(self):
        """Get the current floor type."""
        if not self.floors or self.current_floor_index >= len(self.floors):

            if not self.floors:
                self.initialise_run()

            if not self.floors or self.current_floor_index >= len(self.floors):
                return "dungeon"

        return self.floors[self.current_floor_index]

    def advance_room(self):
        """Move to the next room in the current floor."""
        old_room = self.current_room
        self.current_room += 1

        if self.current_room > FLOOR_TOTAL:
            return self.advance_floor()

        return {
            "floor": self.get_current_floor(),
            "room": self.current_room
        }

    def advance_floor(self):
        """Move to the next floor."""
        self.current_floor_index += 1

        self.current_room = 1

        if self.current_floor_index >= len(self.floors):
            return {"run_complete": True}

        if hasattr(self.game_manager, 'states') and 'playing' in self.game_manager.states:
            playing_state = self.game_manager.states["playing"]
            if hasattr(playing_state, 'completed_rooms'):
                playing_state.completed_rooms = 0

        return {
            "floor": self.get_current_floor(),
            "room": self.current_room,
            "is_floor_start": True
        }

class FloorStartState(GameState):
    """The floor starting screen where players begin a new floor."""

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None

        self.panels = {}
        self.buttons = {}
        self.continue_button = None

    def enter(self):

        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()

        floor_image = f"floors/{current_floor_type}_floor.png"

        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:

            self.floor = ResourceLoader.load_image("floor.png")

        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        self.create_ui()

    def create_ui(self):
        """Create the UI elements for the floor start state."""

        self.panels["main"] = Panel(
            (600, 300),
            (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150),
            colour=DARK_GRAY
        )

        continue_rect = pygame.Rect(0, 0, 200, 50)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.bottom = self.panels["main"].rect.bottom - 30
        self.continue_button = Button(continue_rect, "Enter Floor", self.body_font)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:

            self.continue_button.check_hover(event.pos)

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:

            if self.continue_button.is_clicked(event.pos):
                self.game_manager.change_state("playing")
                return

    def update(self, delta_time):
        pass

    def draw(self, surface):

        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))

        for panel in self.panels.values():
            panel.draw(surface)

        floor_type = self.game_manager.floor_manager.get_current_floor()
        floor_index = max(1, self.game_manager.floor_manager.current_floor_index + 1)
        title_text = self.header_font.render(f"Floor {floor_index}: {floor_type.title()}", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 30)
        surface.blit(title_text, title_rect)

        welcome_text = self.body_font.render(f"Welcome to the {floor_type.title()}", True, WHITE)
        welcome_rect = welcome_text.get_rect(centerx=self.panels["main"].rect.centerx, top=title_rect.bottom + 30)
        surface.blit(welcome_text, welcome_rect)

        instruct_text = self.normal_font.render("Prepare yourself for the challenges ahead!", True, WHITE)
        instruct_rect = instruct_text.get_rect(centerx=self.panels["main"].rect.centerx, top=welcome_rect.bottom + 20)
        surface.blit(instruct_text, instruct_rect)

        self.continue_button.draw(surface)

class GameManager:
    """Manager for game states with roguelike elements."""

    def __init__(self):

        self.floor_manager = FloorManager(self)

        self.states = {
            "title": TitleState(self),
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self),
            "tutorial": TutorialState(self),
            "tutorial_watch": TutorialState(self, watch=True),
        }

        self.current_state = None
        self.game_data = {
            "life_points": STARTING_ATTRIBUTES["life_points"],
            "max_life": STARTING_ATTRIBUTES["max_life"],
            "victory": False,
            "run_complete": False
        }

        self.equipped_weapon = {}
        self.defeated_monsters = []
        self.last_card_data = None

        self.fade_alpha = 0
        self.fade_direction = 0
        self.fade_speed = 255 / 0.5
        self.pending_state = None
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)
        
        self.fade_surface = self.fade_surface.convert_alpha()

        self.change_state("title")

    def change_state(self, state_name, fade_duration=0.5):
        if self.current_state is None:
            self.current_state = self.states[state_name]
            self.current_state.enter()
            return

        if self.fade_direction != 0:
            return
            
        if self.current_state == self.states[state_name]:
            return
        
        self.fade_speed = 255 / fade_duration
        
        self.pending_state = state_name
        self.fade_direction = 1
        self.fade_alpha = 0

    def _execute_state_transition(self):
        if self.current_state:
            if type(self.current_state) == TutorialState:
                self.has_shown_tutorial = True
            self.current_state.exit()

        if self.pending_state == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()

        self.current_state = self.states[self.pending_state]
        self.current_state.enter()
        self.pending_state = None

    def change_state_instant(self, state_name):
        if self.current_state and self.current_state == self.states[state_name]:
            return

        if self.current_state:
            self.current_state.exit()

        if state_name == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()

        self.current_state = self.states[state_name]
        self.current_state.enter()

    def handle_event(self, event):
        if self.fade_direction != 0 and event.type == MOUSEBUTTONDOWN:
            return
            
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, delta_time):
        if self.fade_direction != 0:
            self.fade_alpha += self.fade_direction * self.fade_speed * delta_time
            
            if self.fade_direction == 1:
                if self.fade_alpha >= 255:
                    self.fade_alpha = 255
                    self._execute_state_transition()
                    self.fade_direction = -1
            else:
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0
        
        if self.current_state and not (self.fade_direction == 1):
            self.current_state.update(delta_time)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
        
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

    def start_new_run(self):
        """Initialise a new roguelike run."""

        self.game_data["life_points"] = STARTING_ATTRIBUTES["life_points"]
        self.game_data["max_life"] = STARTING_ATTRIBUTES["max_life"]
        self.game_data["victory"] = False
        self.game_data["run_complete"] = False

        self.floor_manager.initialise_run()

        self.is_new_run = True

        self.change_state("playing")

    def advance_to_next_room(self):
        """Advance to the next room in the current floor."""
        room_info = self.floor_manager.advance_room()

        if "run_complete" in room_info and room_info["run_complete"]:

            self.game_data["victory"] = True
            self.game_data["run_complete"] = True
            return

        if "is_floor_start" in room_info and room_info["is_floor_start"]:
            return

    def check_game_over(self):
        """Check if the game is over."""
        if self.game_data["life_points"] <= 0:
            self.game_data["victory"] = False

            self.change_state("game_over")
            return True
        return False

    def heal_player(self, amount=5):
        """Heal the player by the specified amount."""
        self.game_data["life_points"] = min(
            self.game_data["life_points"] + amount,
            self.game_data["max_life"]
        )

    def increase_max_health(self, amount=5):
        """Increase the player's maximum health."""
        self.game_data["max_life"] += amount
        self.game_data["life_points"] += amount

class GameOverState(GameState):
    """The game over state of the game."""

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None

        self.restart_button = None
        self.title_button = None

        self.game_over_panel = None

        self.particles = []

        self.playing_state = None

    def enter(self):

        self.playing_state = self.game_manager.states["playing"]

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 48)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)

        panel_width = 580
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        if self.game_manager.game_data["victory"]:
            panel_colour = (40, 60, 40)
            border_colour = (80, 180, 80)
        else:
            panel_colour = (60, 30, 30)
            border_colour = (150, 50, 50)

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

        button_width = 300
        button_height = 50
        button_spacing = 12
        buttons_y = panel_y + panel_height - button_height*2 - button_spacing - 33

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

        self._create_particles()

    def _create_particles(self):
        """Create particles based on victory/defeat state"""
        self.particles = []

        if self.game_manager.game_data["victory"]:
            num_particles = 40
            colours = [(120, 255, 120), (180, 255, 180), (220, 255, 220)]
        else:
            num_particles = 20
            colours = [(255, 120, 120), (255, 150, 150)]

        for _ in range(num_particles):

            edge = random.randint(0, 3)

            if edge == 0:
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.top - 20, self.game_over_panel.rect.top + 20)
            elif edge == 1:
                x = random.uniform(self.game_over_panel.rect.right - 20, self.game_over_panel.rect.right + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)
            elif edge == 2:
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.bottom - 20, self.game_over_panel.rect.bottom + 20)
            else:
                x = random.uniform(self.game_over_panel.rect.left - 20, self.game_over_panel.rect.left + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)

            colour = random.choice(colours)

            self.particles.append({
                'x': x,
                'y': y,
                'colour': colour,
                'size': random.uniform(1.5, 3.5),
                'life': 1.0,
                'decay': random.uniform(0.002, 0.005),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5)
            })

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:

            if self.restart_button and self.restart_button.is_clicked(event.pos):

                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False

                self.game_manager.states["playing"] = PlayingState(self.game_manager)

                self.game_manager.start_new_run()

            elif self.title_button and self.title_button.is_clicked(event.pos):

                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False

                self.game_manager.states["playing"] = PlayingState(self.game_manager)

                self.game_manager.change_state("title")

        mouse_pos = pygame.mouse.get_pos()
        if self.restart_button:
            self.restart_button.check_hover(mouse_pos)
        if self.title_button:
            self.title_button.check_hover(mouse_pos)

    def _update_particles(self, delta_time):
        """Update the particle effects"""

        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= particle['decay']

            if particle['life'] <= 0:
                self.particles.remove(particle)

        if random.random() < 0.1 and len(self.particles) < 60:
            self._create_particles()

    def update(self, delta_time):
        """Update game over state"""
        self._update_particles(delta_time)

    def draw(self, surface):

        if not self.playing_state:

            if not hasattr(self, 'background') or not self.background:
                self.background = ResourceLoader.load_image("bg.png")
                if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
                    self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

            surface.blit(self.background, (0, 0))

            if not hasattr(self, 'floor') or not self.floor:
                random_floor_type = random.choice(FLOOR_TYPES)
                floor_image = f"floors/{random_floor_type}_floor.png"

                try:
                    self.floor = ResourceLoader.load_image(floor_image)
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
                except:

                    self.floor = ResourceLoader.load_image("floor.png")
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

            surface.blit(self.floor, ((SCREEN_WIDTH - FLOOR_WIDTH)/2, (SCREEN_HEIGHT - FLOOR_HEIGHT)/2))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
        else:

            self.playing_state.draw(surface)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

        for particle in self.particles:
            alpha = int(255 * particle['life'])

            r, g, b = particle['colour']
            particle_colour = pygame.Color(r, g, b, alpha)
            pygame.draw.circle(
                surface,
                particle_colour,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )

        self.game_over_panel.draw(surface)

        if self.game_manager.game_data["victory"]:
            result_text = self.title_font.render("VICTORY!", True, (180, 255, 180))
            subtitle_text = self.header_font.render("You have conquered the dungeon", True, WHITE)
        else:
            result_text = self.title_font.render("DEFEATED", True, (255, 180, 180))
            subtitle_text = self.header_font.render("Your adventure ends here...", True, WHITE)

        result_rect = result_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.game_over_panel.rect.top + 32)
        surface.blit(result_text, result_rect)

        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=result_rect.bottom + 20)
        surface.blit(subtitle_text, subtitle_rect)

        stats_y = subtitle_rect.bottom + 25

        floors_text = self.body_font.render(
            f"Floors Completed: {self.game_manager.floor_manager.current_floor_index}",
            True, WHITE
        )
        floors_rect = floors_text.get_rect(centerx=SCREEN_WIDTH//2, top=stats_y)
        surface.blit(floors_text, floors_rect)

        if self.restart_button:
            self.restart_button.draw(surface)

        if self.title_button:
            self.title_button.draw(surface)

class GameStateController:
    """Manages game state transitions and end game conditions."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def check_game_over(self):
        """Check if the game is over due to player death."""
        if self.playing_state.life_points <= 0:
            self.end_game(False)
            return True
        return False

    def end_game(self, victory):
        """End the game with either victory or defeat."""

        self.playing_state.game_manager.game_data["victory"] = victory

        self.playing_state.game_manager.change_state("game_over")

    def show_message(self, message, duration=1.2):
        """Display a small, non-blocking notification above the room cards."""

        message_text = self.playing_state.body_font.render(message, True, self.playing_state.WHITE)

        room_top = self.playing_state.SCREEN_HEIGHT//2 - 120
        message_rect = message_text.get_rect(center=(self.playing_state.SCREEN_WIDTH//2, room_top - 25))

        padding_x, padding_y = 15, 8
        bg_rect = pygame.Rect(
            message_rect.left - padding_x,
            message_rect.top - padding_y,
            message_rect.width + padding_x * 2,
            message_rect.height + padding_y * 2
        )

        self.playing_state.message = {
            "text": message_text,
            "rect": message_rect,
            "bg_rect": bg_rect,
            "alpha": 0,
            "fade_in": True,
            "time_remaining": duration,
            "fade_speed": 510
        }

class HUD:
    """Heads-up display for showing active effects and status."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        self.small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)

        self.active_effects = []

        self.effect_icon_size = EFFECT_ICON_SIZE
        self.effect_spacing = EFFECT_ICON_SPACING
        self.effect_start_pos = EFFECT_START_POSITION

        self.last_particle_time = 0

        self.health_panel = None

    def update_fonts(self, normal_font, small_font=None):
        """Update fonts if they are loaded after initialization."""
        self.normal_font = normal_font
        if small_font:
            self.small_font = small_font

    def add_effect(self, effect_type, duration=None, value=None):
        """Add a new active effect to display."""
        self.active_effects.append({
            'type': effect_type,
            'duration': duration,
            'value': value,
            'start_time': pygame.time.get_ticks()
        })

    def update(self):
        """Update active effects and resource animations."""
        current_time = pygame.time.get_ticks()

        self.active_effects = [effect for effect in self.active_effects if (
            effect['duration'] is None) or
            ((current_time - effect['start_time']) < effect['duration'])
        ]

    def draw(self, surface):
        """Draw the HUD elements."""

        self.draw_active_effects(surface)

        self.draw_health_indicator(surface)

    def draw_active_effects(self, surface):
        """Draw icons for active effects with dungeon styling."""
        try:
            using_panels = True
        except ImportError:
            using_panels = False

        for i, effect in enumerate(self.active_effects):

            x = self.effect_start_pos[0] + i * (self.effect_icon_size + self.effect_spacing)
            y = self.effect_start_pos[1]

            effect_rect = pygame.Rect(x, y, self.effect_icon_size, self.effect_icon_size)

            effect_colour = EFFECT_DEFAULT_COLOUR
            if effect['type'] == 'healing':
                effect_colour = EFFECT_HEALING_COLOUR
                panel_colour = EFFECT_HEALING_PANEL
                border_colour = EFFECT_HEALING_BORDER
                icon_symbol = "+"
            elif effect['type'] == 'damage':
                effect_colour = EFFECT_DAMAGE_COLOUR
                panel_colour = EFFECT_DAMAGE_PANEL
                border_colour = EFFECT_DAMAGE_BORDER
                icon_symbol = "⚔"
            else:
                effect_colour = EFFECT_DEFAULT_COLOUR
                panel_colour = EFFECT_DEFAULT_PANEL
                border_colour = EFFECT_DEFAULT_BORDER
                icon_symbol = "◆"

            if using_panels:

                effect_panel = Panel(
                    (self.effect_icon_size, self.effect_icon_size),
                    (x, y),
                    colour=panel_colour,
                    alpha=PANEL_ALPHA,
                    border_radius=PANEL_BORDER_RADIUS - 2,
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=border_colour
                )
                effect_panel.draw(surface)

                current_time = pygame.time.get_ticks()
                if effect['duration'] is not None:

                    elapsed = (current_time - effect['start_time']) / effect['duration']

                    base, amplitude, frequency = EFFECT_PULSE_TEMPORARY
                    pulse_factor = base + amplitude * math.sin(elapsed * 10 + current_time / frequency)
                else:

                    base, amplitude, frequency = EFFECT_PULSE_PERMANENT
                    pulse_factor = base + amplitude * math.sin(current_time / frequency)

                glow_radius = int(self.effect_icon_size * 0.3 * pulse_factor)
                center_x = x + self.effect_icon_size // 2
                center_y = y + self.effect_icon_size // 2

                for r in range(glow_radius, 0, -1):
                    alpha = max(0, 150 - (glow_radius - r) * 20)
                    pygame.draw.circle(
                        surface, (*effect_colour, alpha),
                        (center_x, center_y), r
                    )

                symbol_font = pygame.font.SysFont(None, int(self.effect_icon_size * 0.6))
                symbol_text = symbol_font.render(icon_symbol, True, WHITE)
                symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
                surface.blit(symbol_text, symbol_rect)
            else:

                pygame.draw.rect(surface, effect_colour, effect_rect)
                pygame.draw.rect(surface, BLACK, effect_rect, 2)

            if effect['value'] is not None:
                value_text = self.normal_font.render(str(effect['value']), True, WHITE)
                value_rect = value_text.get_rect(center=effect_rect.center)

                if using_panels:
                    value_rect.midtop = (x + self.effect_icon_size // 2, y + self.effect_icon_size + 2)

                surface.blit(value_text, value_rect)

            if effect['duration'] is not None:
                remaining = max(0, effect['duration'] - (pygame.time.get_ticks() - effect['start_time']))
                remaining_text = self.small_font.render(f"{remaining//1000}s", True, WHITE)

                if effect['value'] is not None and using_panels:

                    remaining_rect = remaining_text.get_rect(
                        midtop=(
                            x + self.effect_icon_size // 2,
                            y + self.effect_icon_size + value_text.get_height() + 4
                        )
                    )
                else:

                    remaining_rect = remaining_text.get_rect(
                        midbottom=(
                            x + self.effect_icon_size // 2,
                            y + self.effect_icon_size + (10 if using_panels else 0)
                        )
                    )

                if remaining < EFFECT_EXPIRE_THRESHOLD:

                    remaining_text = self.small_font.render(f"{remaining//1000}s", True, (255, 100, 100))

                    pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 100)
                    scaled_size = int(remaining_text.get_width() * pulse), int(remaining_text.get_height() * pulse)
                    if scaled_size[0] > 0 and scaled_size[1] > 0:
                        pulsed_text = pygame.transform.scale(remaining_text, scaled_size)
                        remaining_rect = pulsed_text.get_rect(center=remaining_rect.center)
                        surface.blit(pulsed_text, remaining_rect)
                    else:
                        surface.blit(remaining_text, remaining_rect)
                else:
                    surface.blit(remaining_text, remaining_rect)

    def draw_health_indicator(self, surface):
        """Draw a health bar indicator with dungeon styling."""
        playing_state = self.game_manager.states["playing"]
        if not hasattr(playing_state, 'life_points') or not hasattr(playing_state, 'max_life'):
            return

        bar_width = HEALTH_BAR_WIDTH
        bar_height = HEALTH_BAR_HEIGHT
        x, y = HEALTH_BAR_POSITION

        if not self.health_panel:
            try:

                self.health_panel = Panel(
                    (bar_width, bar_height),
                    (x, y),
                    colour=PANEL_HEALTH,
                    alpha=PANEL_ALPHA + 10,
                    border_radius=PANEL_BORDER_RADIUS,
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=PANEL_HEALTH_BORDER
                )
            except ImportError:

                self.health_panel = None

        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int((bar_width - 10) * health_percent)

        if health_percent > 0.7:
            health_colour = HEALTH_COLOUR_GOOD
            glow_colour = HEALTH_GLOW_GOOD
        elif health_percent > 0.3:
            health_colour = HEALTH_COLOUR_WARNING
            glow_colour = HEALTH_GLOW_WARNING
        else:
            health_colour = HEALTH_COLOUR_DANGER
            glow_colour = HEALTH_GLOW_DANGER

        if self.health_panel:
            self.health_panel.draw(surface)

            health_rect = pygame.Rect(x + 5, y + 5, health_width, bar_height - 10)

            glow_surface = pygame.Surface((health_width + 10, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface, glow_colour,
                (5, 0, health_width, bar_height - 10), border_radius=4
            )
            surface.blit(glow_surface, (x, y))

            pygame.draw.rect(surface, health_colour, health_rect, border_radius=4)

            if health_width > 4:
                highlight_colour = self._lighten_colour(health_colour, 0.3)
                pygame.draw.rect(
                    surface, highlight_colour,
                    (x + 5, y + 5, health_width, 2), border_radius=2
                )
        else:

            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)

            health_rect = pygame.Rect(x, y, health_width, bar_height)
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)

        text_colour = WHITE
        health_text = self.normal_font.render(f"{playing_state.life_points}/{playing_state.max_life}", True, text_colour)
        health_text_rect = health_text.get_rect(center=(x + bar_width//2, y + bar_height//2))
        surface.blit(health_text, health_text_rect)

    def _lighten_colour(self, colour, factor=0.3):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))

class InventoryManager:
    """Manages the player's inventory of cards."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def position_inventory_cards(self):
        """Position inventory cards centered vertically within the panel."""

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        card_scale = 1.0

        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)

        num_cards = len(self.playing_state.inventory)

        for i, card in enumerate(self.playing_state.inventory):

            card.update_scale(card_scale)

            card.in_inventory = True

            inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)

            if num_cards == 1:

                inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
            elif num_cards == 2:

                if i == 0:

                    inventory_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
                else:

                    inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)

            card.update_position((inventory_x, inventory_y))

    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.playing_state.inventory:
            if card.rect.collidepoint(position):
                return card
        return None

class Panel:
    def __init__(self, width_height, top_left, colour=DARK_GRAY, alpha=None, border_radius=None,
            dungeon_style=True, border_width=None, border_colour=None):

        if alpha is None:
            alpha = PANEL_ALPHA
        if border_radius is None:
            border_radius = PANEL_BORDER_RADIUS
        if border_width is None:
            border_width = PANEL_BORDER_WIDTH
        if border_colour is None:
            border_colour = PANEL_DEFAULT_BORDER
        self.width_height = width_height
        self.top_left = top_left
        self.rect = pygame.Rect(self.top_left, self.width_height)
        self.colour = colour
        self.alpha = alpha
        self.border_radius = border_radius
        self.dungeon_style = dungeon_style
        self.border_width = border_width
        self.border_colour = border_colour

        self.noise_texture = None
        if self.dungeon_style:
            self._create_noise_texture()

        self._create_surface()

    def _create_noise_texture(self):
        """Create a subtle noise texture for the panel background"""
        width, height = self.rect.size
        self.noise_texture = pygame.Surface((width, height), pygame.SRCALPHA)

        grain_size = 3

        for x in range(0, width, grain_size):
            for y in range(0, height, grain_size):

                darkness = random.randint(0, 25)

                pygame.draw.rect(self.noise_texture, (0, 0, 0, darkness),
                                (x, y, grain_size, grain_size))

                if random.random() < 0.05:
                    lightness = random.randint(5, 15)
                    pygame.draw.rect(
                        self.noise_texture, (255, 255, 255, lightness),
                        (x, y, grain_size, grain_size)
                    )

    def _draw_decorative_border(self, surface, rect, border_radius):
        """Draw a decorative border with corner details for a dungeon feel"""

        darker_border = self._darken_colour(self.border_colour, 0.5)
        lighter_border = self._lighten_colour(self.border_colour, 0.3)

        pygame.draw.rect(surface, darker_border, rect,
            width=self.border_width+1, border_radius=border_radius
        )

        inner_rect = rect.inflate(-4, -4)
        pygame.draw.rect(surface, lighter_border, inner_rect,
            width=1, border_radius=max(0, border_radius-2)
        )

        corner_size = min(10, border_radius)
        if corner_size > 3:

            pygame.draw.line(surface, darker_border,
                (rect.left + border_radius//2, rect.top + 3),
                (rect.left + 3, rect.top + border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.right - border_radius//2, rect.top + 3),
                (rect.right - 3, rect.top + border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.left + border_radius//2, rect.bottom - 3),
                (rect.left + 3, rect.bottom - border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.right - border_radius//2, rect.bottom - 3),
                (rect.right - 3, rect.bottom - border_radius//2), 2)

    def _create_surface(self):
        """Create the panel surface with desired style"""

        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(self.surface, self.colour, rect, border_radius=self.border_radius)

        if self.dungeon_style and self.noise_texture:
            self.surface.blit(self.noise_texture, (0, 0))

        if self.dungeon_style:
            self._draw_decorative_border(self.surface, rect, self.border_radius)

        self.surface.set_alpha(self.alpha)

    def _darken_colour(self, colour, factor=0.7):
        """Create a darker version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (int(r * factor), int(g * factor), int(b * factor))

    def _lighten_colour(self, colour, factor=0.3):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))

    def _draw_rounded_rect(self, surface, rect, colour, border_radius):
        """Draw a rectangle with rounded corners"""
        rect_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, colour, rect_surf.get_rect(), border_radius=border_radius)
        surface.blit(rect_surf, rect.topleft)

    def update_position(self, pos):
        self.rect.topleft = pos

    def update_size(self, size):
        self.rect.size = size

        if self.dungeon_style:
            self._create_noise_texture()

        self._create_surface()

    def update_colour(self, colour):
        self.colour = colour
        self._create_surface()

    def update_alpha(self, alpha):
        self.alpha = alpha
        self.surface.set_alpha(alpha)

    def update_border_radius(self, border_radius):
        self.border_radius = border_radius
        self._create_surface()

    def update_style(self, dungeon_style, border_width=None, border_colour=None):
        """Update the styling options"""
        self.dungeon_style = dungeon_style
        if border_width is not None:
            self.border_width = border_width
        if border_colour is not None:
            self.border_colour = border_colour
        self._create_surface()

    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)

class PlayerStateManager:
    """Manages player state."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def change_health(self, amount):
        """Change player health with animation."""
        old_health = self.playing_state.life_points

        if amount > 0:

            self.playing_state.life_points = min(self.playing_state.life_points + amount, self.playing_state.max_life)
            actual_change = self.playing_state.life_points - old_health

            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(False, actual_change)
        else:

            self.playing_state.life_points = max(0, self.playing_state.life_points + amount)
            actual_change = old_health - self.playing_state.life_points

            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(True, actual_change)

class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""

    def __init__(self, game_manager):
        """Initialise the playing state."""
        super().__init__(game_manager)

        self._initialise_managers()

        self._initialise_state_variables()

        self._initialise_player_state()

        self._initialise_game_components()

        self._initialise_ui_elements()

    def _initialise_managers(self):
        """Initialise all manager and controller classes."""

        self.animation_manager = AnimationManager()

        self.resource_loader = ResourceLoader

        self.card_action_manager = CardActionManager(self)
        self.room_manager = RoomManager(self)
        self.animation_controller = AnimationController(self)
        self.player_state_manager = PlayerStateManager(self)
        self.inventory_manager = InventoryManager(self)
        self.ui_renderer = UIRenderer(self)
        self.game_state_controller = GameStateController(self)
        self.ui_factory = UIFactory(self)

    def _initialise_state_variables(self):
        """Initialise general state variables."""

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_GRAY = LIGHT_GRAY

        self.is_running = False
        self.ran_last_turn = False
        self.show_debug = False
        self.z_index_counter = 0

        self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        self.floor_completed = False
        self.room_completion_in_progress = False
        self.room_started_in_enter = False

        self.message = None

    def _initialise_player_state(self):
        """Initialise player stats and inventory."""

        self.life_points = 20
        self.max_life = 20
        self.equipped_weapon = {}
        self.defeated_monsters = []

        self.inventory = []
        self.MAX_INVENTORY_SIZE = 2

    def _initialise_game_components(self):
        """Initialise game components like deck, discard pile, room."""
        self.deck = None
        self.discard_pile = None
        self.room = None
        self.current_floor = None

    def _initialise_ui_elements(self):
        """Initialise UI elements and resources."""
        self.header_font = None
        self.body_font = None
        self.caption_font = None
        self.normal_font = None
        self.run_button = None
        self.background = None
        self.floor = None

        self.status_ui = StatusUI(self.game_manager)
        self.hud = HUD(self.game_manager)

    def enter(self):
        """Initialise the playing state when entering."""

        self._load_resources()

        self._setup_game_components()

        self._setup_player_state()

        self._start_initial_room()

        self._reset_state_tracking()

    def _load_resources(self):
        """Load fonts, background and floor image."""

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.caption_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()

        floor_image = f"floors/{current_floor_type}_floor.png"

        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:

            self.floor = ResourceLoader.load_image("floor.png")

        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

    def _setup_game_components(self):
        """Initialise deck, discard pile, and room."""

        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()

        if not self.current_floor:
            self.current_floor = "dungeon"

        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)

        if hasattr(self.deck, "initialise_visuals"):
            self.deck.initialise_visuals()

        if hasattr(self.discard_pile, "initialise_visuals"):
            self.discard_pile.initialise_visuals()

        if hasattr(self, "inventory_manager") and hasattr(self.inventory_manager, "position_inventory_cards"):
            self.inventory_manager.position_inventory_cards()

        self.ui_factory.create_run_button()

    def _setup_player_state(self):
        """Set up player stats and equipped weapon."""

        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]

    def _start_initial_room(self):
        """Start the initial room either with a card from fresh."""

        self.deck.initialise_deck()

        if self.discard_pile:
            self.discard_pile.cards = []
            if hasattr(self.discard_pile, 'card_stack'):
                self.discard_pile.card_stack = []

        self.room_manager.start_new_room()

        self.room_started_in_enter = True

        self.status_ui.update_fonts(self.header_font, self.normal_font)

        self.hud.update_fonts(self.normal_font, self.normal_font)

    def _reset_state_tracking(self):
        """Reset game state tracking variables."""

        self.floor_completed = False

        if self.game_manager.floor_manager.current_room == 1:
            self.completed_rooms = 0

    def exit(self):
        """Save state when exiting playing state."""

        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life

    def handle_event(self, event):
        """Handle player input events."""
        if self.animation_manager.is_animating():
            return

        if event.type == MOUSEMOTION:
            self._handle_hover(event)

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event)

    def _handle_hover(self, event):
        """Handle mouse hover events over cards and buttons."""

        inventory_is_full = len(self.inventory) >= self.MAX_INVENTORY_SIZE

        all_hoverable_cards = []

        for card in self.room.cards:

            if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
                card.weapon_available = bool(self.equipped_weapon)

                if self.equipped_weapon and self.defeated_monsters:
                    card.weapon_attack_not_viable = card.value >= self.defeated_monsters[-1].value
                else:
                    card.weapon_attack_not_viable = False

            if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
                card.inventory_available = not inventory_is_full

            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)

        for card in self.inventory:

            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)

        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]

            weapon_card.is_hovered = False
            if weapon_card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(weapon_card)

        for monster in self.defeated_monsters:

            monster.is_hovered = False
            if monster.rect.collidepoint(event.pos):
                all_hoverable_cards.append(monster)

        if all_hoverable_cards:
            closest_card = self._find_closest_card(event.pos, all_hoverable_cards)

            if closest_card:
                closest_card.check_hover(event.pos)

        self.run_button.check_hover(event.pos)

    def _find_closest_card(self, pos, cards):
        """Find the card closest to the given position."""
        if not cards:
            return None

        closest_card = None
        closest_distance = float('inf')

        for card in cards:

            card_center_x = card.rect.centerx
            card_center_y = card.rect.centery

            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset

            card_center_y -= total_float_offset

            dist_sq = (pos[0] - card_center_x) ** 2 + (pos[1] - card_center_y) ** 2

            if dist_sq < closest_distance:
                closest_distance = dist_sq
                closest_card = card

        return closest_card

    def _handle_click(self, event):
        """Handle mouse click events."""
        if self.life_points <= 0:
            return

        if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
            self.room_manager.run_from_room()
            return

        clicked_card = None

        card = self.room.get_card_at_position(event.pos)
        if card:
            self.card_action_manager.resolve_card(card, event_pos=event.pos)
            return

        clicked_inventory_card = self.inventory_manager.get_inventory_card_at_position(event.pos)
        if clicked_inventory_card:
            self.card_action_manager.use_inventory_card(clicked_inventory_card, event.pos)
            return

        if "node" in self.equipped_weapon and self.equipped_weapon["node"].rect.collidepoint(event.pos):
            self.card_action_manager.discard_equipped_weapon()

    def update(self, delta_time):
        """Update game state for this frame."""

        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()

        animations_just_finished = previous_animating and not current_animating

        self._update_message(delta_time)
        self._update_cards(delta_time)

        if not current_animating:
            self._process_game_state(animations_just_finished)

        self.game_state_controller.check_game_over()

    def _update_message(self, delta_time):
        """Update any active message fade animation."""
        if hasattr(self, 'message') and self.message and 'alpha' in self.message:

            if self.message['fade_in']:

                self.message['alpha'] = min(255, self.message['alpha'] + self.message['fade_speed'] * delta_time)

                if self.message['alpha'] >= 255:
                    self.message['fade_in'] = False
            else:

                self.message['time_remaining'] -= delta_time

                if self.message['time_remaining'] <= 0:
                    self.message['alpha'] = max(0, self.message['alpha'] - self.message['fade_speed'] * delta_time)

                    if self.message['alpha'] <= 0:
                        self.message = None

    def _update_cards(self, delta_time):
        """Update all card animations."""

        for card in self.room.cards:

            card.update(delta_time)

            if card.is_flipping:
                card.update_flip(delta_time)

        for card in self.inventory:
            card.update(delta_time)
            if card.is_flipping:
                card.update_flip(delta_time)

        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].update(delta_time)

        for monster in self.defeated_monsters:
            monster.update(delta_time)

    def _process_game_state(self, animations_just_finished):
        """Process game state changes after animations."""
        if self.is_running:
            self.room_manager.on_run_completed()
            return

        if self.room_started_in_enter:
            self.room_started_in_enter = False
            return

        if len(self.room.cards) == 0:
            self._handle_empty_room()

        elif len(self.room.cards) == 1 and animations_just_finished and len(self.deck.cards) > 0:
            self._handle_single_card_room()

    def _handle_empty_room(self):
        """Handle logic for when the room is empty (all cards processed)."""
        if not self.room_completion_in_progress:
            self.room_completion_in_progress = True
            self.completed_rooms += 1

        if len(self.deck.cards) > 0:
            self.game_manager.advance_to_next_room()

            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()

            if self.game_manager.current_state == self:
                self.room_manager.start_new_room()
        else:
            self._handle_floor_completion()

    def _handle_single_card_room(self):
        """Handle logic for rooms with a single card remaining."""
        if not self.room_completion_in_progress:

            self.room_completion_in_progress = True

            self.completed_rooms += 1

            self.game_manager.advance_to_next_room()

            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()

        self.room_manager.start_new_room(self.room.cards[0])

    def _handle_floor_completion(self):
        """Handle logic for when the floor is completed."""
        if not self.floor_completed:
            self.floor_completed = True

            if self.game_manager.floor_manager.current_floor_index >= len(self.game_manager.floor_manager.floors) - 1:

                self.game_manager.game_data["victory"] = True
                self.game_manager.game_data["run_complete"] = True
                self.game_manager.change_state("game_over")
            else:

                floor_type = self.game_manager.floor_manager.get_current_floor()
                if "'" in floor_type:
                    b = []
                    for temp in floor_type.split():
                        b.append(temp.capitalize())
                    floor_type = " ".join(b)
                else:
                    floor_type = floor_type.title()
                next_floor_index = self.game_manager.floor_manager.current_floor_index + 1
                next_floor_type = self.game_manager.floor_manager.floors[next_floor_index]
                if "'" in next_floor_type:
                    b = []
                    for temp in next_floor_type.split():
                        b.append(temp.capitalize())
                    next_floor_type = " ".join(b)
                else:
                    next_floor_type = next_floor_type.title()
                self.game_state_controller.show_message(f"Floor {floor_type} completed! Moving to {next_floor_type}...")

                self.animation_controller.schedule_delayed_animation(
                    3.0,
                    lambda: self.room_manager.transition_to_next_floor()
                )

    def draw(self, surface):
        """Draw game elements to the screen."""

        self._draw_background(surface)

        self._draw_cards_and_piles(surface)

        self._draw_inventory(surface)

        self._draw_ui_elements(surface)

    def _draw_background(self, surface):
        """Draw background and floor."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))

    def _draw_cards_and_piles(self, surface):
        """Draw deck, discard pile, equipped weapon, and defeated monsters."""

        self.deck.draw(surface)

        self.discard_pile.draw(surface)

        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]

            weapon_is_hovered = weapon_card.is_hovered and weapon_card.face_up

            weapon_card.draw(surface)

            hovered_monsters = []
            non_hovered_monsters = []

            for monster in self.defeated_monsters:
                if monster.is_hovered and monster.face_up:
                    hovered_monsters.append(monster)
                else:
                    non_hovered_monsters.append(monster)

            for monster in non_hovered_monsters:
                monster.draw(surface)

            for monster in hovered_monsters:

                monster.draw(surface)

    def _draw_inventory(self, surface):
        """Draw inventory panel and cards."""
        vertical_center = SCREEN_HEIGHT // 2

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        if not hasattr(self, 'inventory_panel'):

            parchment_colour = (60, 45, 35)
            self.inventory_panel = Panel(
                (inv_width, inv_height),
                (inv_x, inv_y),
                colour=parchment_colour,
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)
            )

        self.inventory_panel.draw(surface)

        inv_rect = self.inventory_panel.rect

        inv_title = self.body_font.render("Inventory", True, WHITE)

        glow_surface = pygame.Surface((inv_title.get_width() + 10, inv_title.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (255, 240, 200, 50)
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())

        glow_rect = glow_surface.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 35)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)

        surface.blit(glow_surface, glow_rect)
        surface.blit(inv_title, title_rect)

        sorted_cards = sorted(self.inventory, key=lambda c: 1 if c.is_hovered else 0)

        for card in sorted_cards:
            self.ui_renderer._draw_card_shadow(surface, card)

        for card in sorted_cards:

            card.draw(surface)

            if card.face_up and card.is_hovered:

                type_text = ""
                if card.type == "weapon" and hasattr(card, 'weapon_type') and card.weapon_type:
                    weapon_type = card.weapon_type.upper()

                    if hasattr(card, 'damage_type') and card.damage_type:
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                elif card.type == "potion":
                    type_text = "HEALING"

    def _draw_ui_elements(self, surface):
        """Draw room cards, UI elements, and status displays."""

        self.room.draw(surface)

        self.animation_manager.draw_effects(surface)

        for card in self.inventory:
            if card.is_hovered and card.face_up:
                card.draw_hover_text(surface)

        if "node" in self.equipped_weapon and self.equipped_weapon["node"].is_hovered and self.equipped_weapon["node"].face_up:
            self.equipped_weapon["node"].draw_hover_text(surface)

        for monster in self.defeated_monsters:
            monster.is_defeated = True

        for monster in self.defeated_monsters:
            if monster.is_hovered and monster.face_up:
                monster.draw_hover_text(surface)

        self.ui_renderer.draw_health_display(surface)

        self.ui_renderer.draw_deck_count(surface)

        self.animation_manager.draw_ui_effects(surface)

        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:

            button_rect = self.run_button.rect

            pygame.draw.rect(surface, LIGHT_GRAY, button_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=5)

            button_text = self.body_font.render("RUN", True, (150, 150, 150))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)

        self._draw_message(surface)

        self.status_ui.draw(surface)

    def _draw_message(self, surface):
        """Draw any active message with fade effect."""
        if hasattr(self, 'message') and self.message:

            if "alpha" in self.message:

                current_alpha = self.message["alpha"]
                text_with_alpha = self.message["text"].copy()
                text_with_alpha.set_alpha(current_alpha)

                bg_surface = pygame.Surface((self.message["bg_rect"].width, self.message["bg_rect"].height), pygame.SRCALPHA)
                bg_colour = (0, 0, 0, int(current_alpha * 0.7))
                pygame.draw.rect(bg_surface, bg_colour, bg_surface.get_rect(), border_radius=8)

                border_colour = (200, 200, 200, int(current_alpha * 0.5))
                pygame.draw.rect(bg_surface, border_colour, bg_surface.get_rect(), 1, border_radius=8)

                surface.blit(bg_surface, self.message["bg_rect"])
                surface.blit(text_with_alpha, self.message["rect"])
            else:

                pygame.draw.rect(surface, BLACK, self.message["bg_rect"], border_radius=8)
                pygame.draw.rect(surface, WHITE, self.message["bg_rect"], 2, border_radius=8)
                surface.blit(self.message["text"], self.message["rect"])

    def change_health(self, amount):
        """Forward health change to player state manager."""
        self.player_state_manager.change_health(amount)

    def position_inventory_cards(self):
        """Forward inventory positioning to inventory manager."""
        self.inventory_manager.position_inventory_cards()

    def animate_card_to_discard(self, card):
        """Forward card discard animation to animation controller."""
        self.animation_controller.animate_card_to_discard(card)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None, on_complete=None):
        """Forward card movement animation to animation controller."""
        self.animation_controller.animate_card_movement(card, target_pos, duration, easing, on_complete)

    def schedule_delayed_animation(self, delay, callback):
        """Forward delayed animation to animation controller."""
        self.animation_controller.schedule_delayed_animation(delay, callback)

    def start_card_flip(self, card):
        """Forward card flip to animation controller."""
        self.animation_controller.start_card_flip(card)

    def position_monster_stack(self):
        """Forward monster stack positioning to animation controller."""
        self.animation_controller.position_monster_stack()

    def animate_card_to_inventory(self, card):
        """Forward card inventory animation to animation controller."""
        self.animation_controller.animate_card_to_inventory(card)

    def show_message(self, message, duration=2.0):
        """Forward message display to game state controller."""
        self.game_state_controller.show_message(message, duration)

def replace_colour(image_path, old_colour, new_colour):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        if item == old_colour:
            new_data.append(new_colour)
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(image_path)

class RoomManager:
    """Manages room creation, transitions, and completion."""

    def __init__(self, playing_state):
        self.playing_state = playing_state

    def start_new_room(self, last_card=None):
        """Start a new room with cards from the deck."""

        if self.playing_state.life_points <= 0:
            return

        if self.playing_state.animation_manager.is_animating():
            return

        if hasattr(self.playing_state, 'room_started_in_enter') and self.playing_state.room_started_in_enter:
            return

        self.playing_state.room_completion_in_progress = False

        self.playing_state.room.clear()

        if last_card:
            self.playing_state.room.add_card(last_card)
            last_card.face_up = True

            num_cards = min(4, len(self.playing_state.deck.cards) + 1)
            total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
            start_x = (SCREEN_WIDTH - total_width) // 2
            start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

            first_position = (start_x, start_y)

            self.playing_state.animate_card_movement(last_card, first_position)

        cards_to_draw = min(4 - len(self.playing_state.room.cards), len(self.playing_state.deck.cards))

        num_cards = min(4, len(self.playing_state.deck.cards) + len(self.playing_state.room.cards))
        total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        target_positions = []
        for i in range(num_cards):
            target_positions.append((
                int(start_x + i * (CARD_WIDTH + self.playing_state.room.card_spacing)),
                int(start_y)
            ))

        for i in range(cards_to_draw):
            if self.playing_state.deck.cards:
                card_data = self.playing_state.deck.draw_card()

                floor_type = card_data.get("floor_type", self.playing_state.current_floor)
                card = Card(card_data["suit"], card_data["value"], floor_type)

                card.face_up = False

                if self.playing_state.deck.card_stack:
                    card.update_position(self.playing_state.deck.card_stack[-1])
                else:
                    card.update_position(self.playing_state.deck.position)

                self.playing_state.room.add_card(card)

                card_position_index = i + (1 if last_card else 0)

                if card_position_index < len(target_positions):
                    target_pos = target_positions[card_position_index]
                else:

                    target_pos = target_positions[-1]

                delay = 0.1 * i

                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=card, pos=target_pos: self.playing_state.animate_card_movement(
                        card,
                        pos,
                        duration=0.3,
                        on_complete=lambda c=card: self.playing_state.start_card_flip(c)
                    )
                )

        if self.playing_state.deck.card_stack:
            for i in range(cards_to_draw):
                if self.playing_state.deck.card_stack:
                    self.playing_state.deck.card_stack.pop()
        self.playing_state.deck.initialise_visuals()

    def run_from_room(self):
        """Run from the current room, moving all cards to the bottom of the deck."""
        if len(self.playing_state.room.cards) != 4 or self.playing_state.animation_manager.is_animating():
            return

        for card in self.playing_state.room.cards:
            if not card.face_up or card.is_flipping:
                return

        self.playing_state.is_running = True

        for card in list(self.playing_state.room.cards):

            if self.playing_state.deck.card_stack:
                target_pos = self.playing_state.deck.card_stack[0]
            else:
                target_pos = self.playing_state.deck.position

            card.z_index = -100

            self.playing_state.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )

            card_data = {"suit": card.suit, "value": card.value}
            self.playing_state.deck.add_to_bottom(card_data)

        self.playing_state.deck.initialise_visuals()

    def on_run_completed(self):
        """Complete the running action after animations finish."""

        self.playing_state.room.clear()
        self.playing_state.is_running = False

        self.playing_state.deck.initialise_visuals()

        self.playing_state.ran_last_turn = True

        self.playing_state.game_manager.advance_to_next_room()

        if hasattr(self.playing_state, 'status_ui') and hasattr(self.playing_state.status_ui, 'update_status'):
            self.playing_state.status_ui.update_status()

        if hasattr(self.playing_state, 'hire_manager'):

            original_chance = self.playing_state.hire_manager.hire_encounter_chance
            self.playing_state.hire_manager.hire_encounter_chance = original_chance / 2

            hire_encounter_started = self.playing_state.hire_manager.try_start_hire_encounter()

            self.playing_state.hire_manager.hire_encounter_chance = original_chance

            if hire_encounter_started:

                return

        self.start_new_room()

    def transition_to_next_floor(self):
        """Helper method to transition to the next floor."""

        current_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        current_floor = self.playing_state.game_manager.floor_manager.get_current_floor()

        if hasattr(self.playing_state, 'discard_pile') and self.playing_state.discard_pile:
            self.playing_state.discard_pile.cards = []
            if hasattr(self.playing_state.discard_pile, 'card_stack'):
                self.playing_state.discard_pile.card_stack = []

        self.playing_state.game_manager.floor_manager.advance_floor()
        next_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        next_floor = self.playing_state.game_manager.floor_manager.get_current_floor()

        self.playing_state.floor_completed = False

        self.playing_state.game_manager.game_data["life_points"] = self.playing_state.life_points
        self.playing_state.game_manager.game_data["max_life"] = self.playing_state.max_life

        self.playing_state.completed_rooms = 0

        self.playing_state._start_initial_room()

    def remove_and_discard(self, card):
        """Remove a card from the room and add it to the discard pile."""
        if card in self.playing_state.room.cards:
            self.playing_state.room.remove_card(card)

        if card in self.playing_state.defeated_monsters:
            self.playing_state.defeated_monsters.remove(card)

        if self.playing_state.equipped_weapon and card == self.playing_state.equipped_weapon["node"]:
            self.playing_state.equipped_weapon = {}

        self.playing_state.discard_pile.add_card(card)

class Room:
    """Represents a room containing cards in the game."""

    def __init__(self, animation_manager=None, card_spacing=35):
        self.cards = []
        self.card_spacing = card_spacing
        self.z_index_counter = 0
        self.animation_manager = animation_manager

        self.name_font = None

    def add_card(self, card):
        self.cards.append(card)

        card.z_index = self.z_index_counter
        self.z_index_counter += 1

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)

            if len(self.cards) > 0:
                self.position_cards(animate=True, animation_manager=self.animation_manager)

    def clear(self):
        self.cards.clear()

    def get_card_count(self):
        return len(self.cards)

    def position_cards(self, animate=False, animation_manager=None):
        if not self.cards:
            return

        num_cards = len(self.cards)
        total_width = (CARD_WIDTH * num_cards) + (self.card_spacing * (num_cards - 1))

        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)

        for i, card in enumerate(sorted_cards):
            card_position = (0, 0)
            if num_cards == 1:

                card_position = (
                    int(start_x - (CARD_WIDTH + self.card_spacing) * 1.5),
                    int(start_y)
                )
            else:
                card_position = (
                    int(start_x + i * (CARD_WIDTH + self.card_spacing)),
                    int(start_y)
                )

            if animate and animation_manager is not None:

                animation = MoveAnimation(
                    card,
                    card.rect.topleft,
                    card_position,
                    0.3,
                    EasingFunctions.ease_out_quad
                )
                animation_manager.add_animation(animation)
            else:

                card.update_position(card_position)

    def get_card_at_position(self, position):
        for card in reversed(sorted(self.cards, key=lambda c: c.z_index)):
            if card.rect.collidepoint(position):
                return card
        return None

    def draw(self, surface):

        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)

        for card in sorted_cards:
            card.draw(surface)

        for card in sorted_cards:
            if card.is_hovered and card.face_up:

                if (hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory) or \
                    (hasattr(card, 'can_show_attack_options') and card.can_show_attack_options):
                    card.draw_hover_text(surface)

class RulesState(GameState):
    """The rules screen state of the game."""

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.normal_font = None
        self.background = None
        self.floor = None
        self.alpha = 255
        self.alpha_direction = True
        self.speed = 40

    def enter(self):

        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 23)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:

            self.game_manager.change_state("title")

    def update(self, delta_time):
        pass

    def draw(self, surface):

        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))

        panel = Panel((800, 610), (SCREEN_WIDTH//2-400, SCREEN_HEIGHT//2-305), colour=DARK_GRAY)
        panel.draw(surface)

        title_text = self.header_font.render("HOW TO PLAY", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, panel.rect.top + 40))
        surface.blit(title_text, title_rect)

        rules = [
            "Welcome to SCOUNDREL",
            "The card-base roguelike dungeon crawler:",
            "",
            "- Each dungeon floor is a deck of cards",
            "- Each set of 4 cards represents a floor room",
            "- Cards represent:",
            "  - Monsters (Clubs & Spades)",
            "  - Weapons (Diamonds)",
            "  - Potions (Hearts)",
            "- You start with 20 life points",
            "- Equip weapons and defeat monsters",
            "- Defeat them with weapons and block some damage",
            "- Or defeat them bare-handed and take full damage",
            "- Weapons lose durability and can only battle weaker monsters each time",
            "- Heal health with potions",
            "- You can run from dangerous rooms before you choose",
            "- But you cannot run twice in a row",
            "- Win by surviving until the deck is empty",
            "- Lose if your health reaches zero"
        ]

        y_offset = title_rect.bottom + 10
        for i, line in enumerate(rules):
            rule_text = self.normal_font.render(line, True, WHITE)
            rule_rect = rule_text.get_rect(centerx=panel.rect.centerx, top=y_offset) if i < 2 else rule_text.get_rect(left=panel.rect.left + 40, top=y_offset)
            surface.blit(rule_text, rule_rect)
            y_offset += 25

        continue_text = self.body_font.render("Left-click to continue...", True, WHITE)
        if self.alpha_direction:
            if self.alpha > 0:
                self.alpha -= 255/self.speed
            else:
                self.alpha_direction = False
                self.alpha += 255/self.speed
        else:
            if self.alpha < 255:
                self.alpha += 255/self.speed
            else:
                self.alpha_direction = True
                self.alpha -= 255/self.speed

        continue_text.set_alpha(self.alpha)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, panel.rect.bottom - 30))
        surface.blit(continue_text, continue_rect)

def split_image(image_path, output_dir, rows, cols):
    """Split an image into smaller images."""

    img = Image.open(image_path)
    img_width, img_height = img.size

    split_width = img_width // cols
    split_height = img_height // rows

    os.makedirs(output_dir, exist_ok=True)

    for row in range(rows):
        for col in range(cols):
            left = col * split_width
            upper = row * split_height
            right = left + split_width
            lower = upper + split_height

            cropped_img = img.crop((left, upper, right, lower))

            output_path = os.path.join(output_dir, f"{os.path.basename(image_path).split('.')[0]}_{row}_{col}.png")
            cropped_img.save(output_path)

class StatusUI:
    """Displays current floor, room, and player stats during gameplay."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)
        self.panel_rect = None

    def update_fonts(self, header_font, normal_font):
        """Update fonts if they are loaded after initialization."""
        self.header_font = header_font
        self.normal_font = normal_font

    def update_status(self):
        """Update the status UI with current room/floor information."""
        pass

    def draw(self, surface):
        """Draw the status UI with a dungeon-themed panel."""

        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()

        if "'" in current_floor:
            b = []
            for temp in current_floor.split():
                b.append(temp.capitalize())
            current_floor = " ".join(b)
        else:
            current_floor = current_floor.title()
        current_floor_index = max(1, floor_manager.current_floor_index + 1)

        current_room = floor_manager.current_room

        total_rooms = FLOOR_TOTAL

        floor_text = self.header_font.render(f"Floor {current_floor_index}: {current_floor}", True, WHITE)

        panel_width = 650

        panel_padding = 60
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH//2 - panel_width//2, 50),
            (650, 90)
        )

        if not hasattr(self, 'styled_panel'):

            self.styled_panel = Panel(
                (self.panel_rect.width, self.panel_rect.height),
                (self.panel_rect.left, self.panel_rect.top),
                colour=(70, 60, 45),
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(110, 90, 50)
            )

        self.styled_panel.draw(surface)

        floor_rect = floor_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 15)

        glow_surface = pygame.Surface((floor_text.get_width() + 10, floor_text.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (230, 220, 170, 30)
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        glow_rect = glow_surface.get_rect(center=floor_rect.center)

        surface.blit(glow_surface, glow_rect)
        surface.blit(floor_text, floor_rect)

        room_text = self.normal_font.render(f"Room {current_room}", True, (220, 220, 200))
        room_rect = room_text.get_rect(centerx=self.panel_rect.centerx, top=floor_rect.bottom + 10)
        surface.blit(room_text, room_rect)

class TitleState(GameState):
    """The atmospheric title screen state of the game."""

    def __init__(self, game_manager):
        super().__init__(game_manager)

        self.title_font = None
        self.subtitle_font = None
        self.body_font = None

        self.background = None
        self.floor = None
        self.title_panel = None
        self.start_button = None
        self.tutorial_button = None
        self.rules_button = None

        self.particles = []
        self.torches = []
        self.torch_anim = None
        self.torch_anim_indexes = (0, 0)
        self.torch_lights = []
        self.title_glow = 0
        self.title_glow_dir = 1

        self.cards = []
        self.card_images = {}
        self.monster_imgs = []
        self.weapon_imgs = []
        self.potion_imgs = []

        self.title_clicks = 0
        self.last_click_count = 0
        self.last_tagline_index = -1
        self.seen_taglines = set()

    def enter(self):

        if not self.game_manager.floor_manager.floors:
            self.game_manager.floor_manager.initialise_run()

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 72)
        self.subtitle_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.torch_anim = [pygame.transform.scale(ResourceLoader.load_image(f"torch_anim/torch_{i}.png"),(128,128)) for i in range(5)]

        self.torch_anim_indexes = random.sample(range(5), 2)
        self.torches = [self.torch_anim[i] for i in self.torch_anim_indexes]

        floor_image = "floor.png"
        self.floor = ResourceLoader.load_image(floor_image)
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        panel_width = 730
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        self.title_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 30),
            alpha=230,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=(120, 100, 80)
        )

        button_width = 300
        button_height = 60
        button_spacing = 10
        buttons_y = panel_y + panel_height - button_height*3 - button_spacing*2 - 25

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
            panel_colour=(60, 30, 30),
            border_colour=(150, 70, 70)
        )

        tutorial_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing),
            button_width,
            button_height
        )
        self.tutorial_button = Button(
            tutorial_button_rect,
            "WATCH TUTORIAL",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(30, 60, 30),
            border_colour=(70, 150, 70)
        )

        rules_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing)*2,
            button_width,
            button_height
        )
        self.rules_button = Button(
            rules_button_rect,
            "GAME RULES",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(30, 30, 60),
            border_colour=(70, 70, 150)
        )

        self._create_torch_lights()

        self._load_card_images()
        self._create_animated_cards()

    def _create_torch_lights(self):
        """Create torch light effects around the title screen"""
        self.torch_lights = []

        self.torch_lights.append({
            'x': SCREEN_WIDTH * 0.1,
            'y': SCREEN_HEIGHT // 2 - 40,
            'radius': 80,
            'flicker': 0,
            'flicker_speed': random.uniform(0.1, 0.2),
            'colour': (255, 150, 50)
        })

        self.torch_lights.append({
            'x': SCREEN_WIDTH * 0.9,
            'y': SCREEN_HEIGHT // 2 - 40,
            'radius': 80,
            'flicker': random.uniform(0, 2 * math.pi),
            'flicker_speed': random.uniform(0.1, 0.2),
            'colour': (255, 150, 50)
        })

    def _load_card_images(self):
        """Load a selection of card images for visual effect"""
        self.card_images = {}

        for monster_class in os.listdir(relative_to_assets("monsters")):
            for monster_name in os.listdir(os.path.join(relative_to_assets("monsters"), monster_class)):
                self.monster_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("monsters"), monster_class, monster_name), cache=False))
        for weapon_name in os.listdir(relative_to_assets("weapons")):
            self.weapon_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("weapons"), weapon_name), cache=False))
        for potion_name in os.listdir(relative_to_assets("potions")):
            self.potion_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("potions"), potion_name), cache=False))

        for value in range(2, 15):
            key = f"spades_{value}"
            black_card_surf = ResourceLoader.load_image(f"cards/spades_{value}.png")
            self.card_images[key] = self.add_monster_card(black_card_surf, value)

        for value in range(2, 11):
            key = f"diamonds_{value}"
            weapon_card_surf = ResourceLoader.load_image(f"cards/diamonds_{value}.png")
            self.card_images[key] = self.add_weapon_card(weapon_card_surf, value)

        for value in range(2, 11):
            key = f"hearts_{value}"
            potion_card_surf = ResourceLoader.load_image(f"cards/hearts_{value}.png")
            self.card_images[key] = self.add_potion_card(potion_card_surf, value)

        self.card_images["card_back"] = ResourceLoader.load_image("cards/card_back.png")

    def add_monster_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        monster_img = random.choice(self.monster_imgs)
        monster_size = 96
        monster_img = pygame.transform.scale(monster_img, (monster_size, monster_size))
        monster_surface = pygame.Surface((monster_size, monster_size), pygame.SRCALPHA)
        monster_surface.blit(monster_img, (0, 0))

        monster_pos = ((card_width - monster_size) // 2, (card_height - monster_size) // 2)
        new_surface.blit(monster_surface, monster_pos)

        return new_surface

    def add_weapon_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        weapon_img = random.choice(self.weapon_imgs)
        weapon_size = 96
        weapon_img = pygame.transform.scale(weapon_img, (weapon_size, weapon_size))
        weapon_surface = pygame.Surface((weapon_size, weapon_size), pygame.SRCALPHA)
        weapon_surface.blit(weapon_img, (0, 0))

        weapon_pos = ((card_width - weapon_size) // 2, (card_height - weapon_size) // 2)
        new_surface.blit(weapon_surface, weapon_pos)

        return new_surface

    def add_potion_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        potion_img = random.choice(self.potion_imgs)
        potion_size = 96
        potion_img = pygame.transform.scale(potion_img, (potion_size, potion_size))
        potion_surface = pygame.Surface((potion_size, potion_size), pygame.SRCALPHA)
        potion_surface.blit(potion_img, (0, 0))

        potion_pos = ((card_width - potion_size) // 2, (card_height - potion_size) // 2)
        new_surface.blit(potion_surface, potion_pos)

        return new_surface

    def _create_animated_cards(self, num_cards=8):
        """Create animated cards that float around the title screen"""

        if len(self.cards) == 0:
            self.cards = []
            card_count = num_cards
        else:

            card_count = 1

        for _ in range(card_count):
            card_keys = list(self.card_images.keys())
            card_key = random.choice(card_keys)

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.2, 0.5)

            if random.random() < 0.5:

                x = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                y = random.uniform(100, SCREEN_HEIGHT - 100)
            else:

                x = random.uniform(100, SCREEN_WIDTH - 100)
                y = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100

            self.cards.append({
                'image': self.card_images[card_key],
                'x': x,
                'y': y,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-0.5, 0.5),
                'scale': random.uniform(0.7, 1.0),
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'shown': False,
                'flip_progress': 0,
                'flip_speed': random.uniform(0.02, 0.04),
                'flip_direction': 1,
                'front_image': self.card_images[card_key],
                'back_image': self.card_images["card_back"],
                'dragging': False,
                'drag_offset_x': 0,
                'drag_offset_y': 0,
                'z_index': random.random(),
                'hover': False
            })

    def _add_particle(self, x, y, colour=(255, 215, 0)):
        """Add a particle effect at the specified position"""
        self.particles.append({
            'x': x,
            'y': y,
            'colour': colour,
            'size': random.uniform(1, 3),
            'life': 1.0,
            'decay': random.uniform(0.005, 0.02),
            'dx': random.uniform(-0.7, 0.7),
            'dy': random.uniform(-0.7, 0.7)
        })

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.start_button.check_hover(mouse_pos)
            self.rules_button.check_hover(mouse_pos)

            card_clicked = False

            sorted_cards = sorted(self.cards, key=lambda card: card['z_index'], reverse=True)

            for card in sorted_cards:

                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )

                expanded_rect = card_rect.inflate(20, 20)

                if expanded_rect.collidepoint(mouse_pos):

                    card['dragging'] = True
                    card['drag_offset_x'] = card['x'] - mouse_pos[0]
                    card['drag_offset_y'] = card['y'] - mouse_pos[1]

                    card['z_index'] = max([c['z_index'] for c in self.cards]) + 0.1

                    if not card['shown']:
                        card['flip_direction'] = 1

                    card_clicked = True
                    break

            if not card_clicked:
                if self.start_button.is_clicked(mouse_pos):
                    if not hasattr(self.game_manager, 'has_shown_tutorial') or not self.game_manager.has_shown_tutorial:
                        self.game_manager.has_shown_tutorial = True
                        self.game_manager.change_state("tutorial")
                    else:
                        self.game_manager.change_state("playing")
                elif self.tutorial_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("tutorial_watch")
                elif self.rules_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("rules")

                title_rect = pygame.Rect(
                    (SCREEN_WIDTH - 600) // 2,
                    self.title_panel.rect.top + 40,
                    600,
                    150
                )
                if title_rect.collidepoint(mouse_pos):
                    self.title_clicks += 1

                    for _ in range(10):
                        self._add_particle(mouse_pos[0], mouse_pos[1], (255, 200, 50))

        elif event.type == MOUSEBUTTONUP and event.button == 1:

            for card in self.cards:
                if card['dragging']:
                    card['dragging'] = False

                    speed_factor = 0.2
                    card['dx'] = random.uniform(-0.5, 0.5) * speed_factor
                    card['dy'] = random.uniform(-0.5, 0.5) * speed_factor

        elif event.type == MOUSEMOTION:

            for card in self.cards:
                if card['dragging']:
                    card['x'] = mouse_pos[0] + card['drag_offset_x']
                    card['y'] = mouse_pos[1] + card['drag_offset_y']

                    card['dx'] = 0
                    card['dy'] = 0

            for card in self.cards:

                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )

                expanded_rect = card_rect.inflate(20, 20)
                card['hover'] = expanded_rect.collidepoint(mouse_pos)

        card_under_cursor = any(card['hover'] for card in self.cards)
        if not card_under_cursor:
            self.start_button.check_hover(mouse_pos)
            self.tutorial_button.check_hover(mouse_pos)
            self.rules_button.check_hover(mouse_pos)
        else:
            self.start_button.hovered = False
            self.tutorial_button.hovered = False
            self.rules_button.hovered = False

    def _update_particles(self, delta_time):
        """Update the particle effects"""

        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= particle['decay']

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def _update_torches(self, delta_time):
        """Update the torch animation by cycling through frame indexes at a steady speed"""
        for i, torch in enumerate(self.torches):
            self.torch_anim_indexes[i] += delta_time * 4
            self.torches[i] = self.torch_anim[int(self.torch_anim_indexes[i]) % len(self.torch_anim)]

    def _update_torch_lights(self, delta_time):
        """Update the torch light effects"""
        for torch in self.torch_lights:
            torch['flicker'] += torch['flicker_speed']

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

        for card in self.cards:

            if card['dragging']:
                continue

            card['x'] += card['dx']
            card['y'] += card['dy']

            if card['hover']:
                card['rotation'] += card['rot_speed'] * 0.3
            else:
                card['rotation'] += card['rot_speed']

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

            if (card['x'] < -150 or card['x'] > SCREEN_WIDTH + 150 or
                card['y'] < -150 or card['y'] > SCREEN_HEIGHT + 150):

                if random.random() < 0.5:

                    card['x'] = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                    card['y'] = random.uniform(100, SCREEN_HEIGHT - 100)
                else:

                    card['x'] = random.uniform(100, SCREEN_WIDTH - 100)
                    card['y'] = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100

                card['shown'] = False
                card['flip_progress'] = 0

                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 0.5)
                card['dx'] = math.cos(angle) * speed
                card['dy'] = math.sin(angle) * speed

                card['rot_speed'] = random.uniform(-0.5, 0.5)

                card_keys = list(self.card_images.keys())
                card_key = random.choice(card_keys[:-1])
                card['front_image'] = self.card_images[card_key]

            if (100 < card['x'] < SCREEN_WIDTH - 100 and
                100 < card['y'] < SCREEN_HEIGHT - 100 and
                not card['shown'] and card['flip_progress'] == 0):
                card['flip_direction'] = 1

        if len(self.cards) < 8 and random.random() < 0.01:
            self._create_animated_cards()

    def update(self, delta_time):

        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.tutorial_button.check_hover(mouse_pos)
        self.rules_button.check_hover(mouse_pos)

        glow_speed = 0.5
        self.title_glow += glow_speed * self.title_glow_dir * delta_time
        if self.title_glow >= 1.0:
            self.title_glow = 1.0
            self.title_glow_dir = -1
        elif self.title_glow <= 0.0:
            self.title_glow = 0.0
            self.title_glow_dir = 1

        self._update_particles(delta_time)

        self._update_torches(delta_time)

        self._update_torch_lights(delta_time)

        self._update_cards(delta_time)

        if random.random() < 0.05:
            x = random.uniform(self.title_panel.rect.left + 50, self.title_panel.rect.right - 50)
            y = random.uniform(self.title_panel.rect.top + 50, self.title_panel.rect.bottom - 50)
            self._add_particle(x, y)

    def draw(self, surface):

        surface.blit(self.background, (0, 0))

        for i, torch in enumerate(self.torches):
            torch_rect = torch.get_rect(center=(SCREEN_WIDTH * (0.1 + 0.8*i), SCREEN_HEIGHT // 2))
            surface.blit(torch, torch_rect)

        for torch in self.torch_lights:

            glow_size = int(torch['radius'] * 2 * (1 + 0.1 * math.sin(torch['flicker'])))
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            for r in range(glow_size//2, 0, -1):
                alpha = max(0, int(90 * r / (glow_size//2) * (0.8 + 0.2 * math.sin(torch['flicker']))))
                pygame.draw.circle(
                    glow_surface,
                    (*torch['colour'], alpha),
                    (glow_size//2, glow_size//2),
                    r
                )

            glow_rect = glow_surface.get_rect(center=(torch['x'], torch['y']))
            surface.blit(glow_surface, glow_rect)

        floor_x = (SCREEN_WIDTH - self.floor.get_width()) // 2
        floor_y = (SCREEN_HEIGHT - self.floor.get_height()) // 2
        surface.blit(self.floor, (floor_x, floor_y))

        sorted_cards = sorted(self.cards, key=lambda card: card['z_index'])

        for card in sorted_cards:

            flip_width = int(card['image'].get_width() * card['scale'] * abs(math.cos(card['flip_progress'] * math.pi)))
            if flip_width < 1:
                flip_width = 1

            card_height = int(card['image'].get_height() * card['scale'])
            card_surface = pygame.Surface((flip_width, card_height), pygame.SRCALPHA)

            if card['flip_progress'] < 0.5:

                image = pygame.transform.scale(
                    card['back_image'],
                    (flip_width, card_height)
                )
            else:

                image = pygame.transform.scale(
                    card['front_image'],
                    (flip_width, card_height)
                )

            card_surface.blit(image, (0, 0))

            if card['hover'] or card['dragging']:

                highlight_rect = pygame.Rect(0, 0, flip_width, card_height)
                pygame.draw.rect(
                    card_surface,
                    (255, 215, 0) if card['dragging'] else (180, 180, 255),
                    highlight_rect,
                    width=3,
                    border_radius=3
                )

                if card['dragging'] and random.random() < 0.05:
                    self._add_particle(card['x'] + random.uniform(-20, 20),
                        card['y'] + random.uniform(-30, 30),
                        (255, 215, 0))

            rotated_card = pygame.transform.rotate(card_surface, card['rotation'])

            card_rect = rotated_card.get_rect(center=(card['x'], card['y']))
            surface.blit(rotated_card, card_rect)

        self.title_panel.draw(surface)

        glow_intensity = int(40 + 30 * self.title_glow)
        glow_colour = (255, 200, 50, glow_intensity)

        title_text = self.title_font.render("SCOUNDREL", True, WHITE)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.title_panel.rect.top + 50)

        glow_size = 15
        glow_surface = pygame.Surface((title_text.get_width() + glow_size*2, title_text.get_height() + glow_size*2), pygame.SRCALPHA)

        for r in range(glow_size, 0, -1):
            alpha = int(glow_colour[3] * r / glow_size)
            pygame.draw.rect(
                glow_surface,
                (*glow_colour[:3], alpha),
                pygame.Rect(glow_size-r, glow_size-r, title_text.get_width()+r*2, title_text.get_height()+r*2),
                border_radius=10
            )

        glow_rect = glow_surface.get_rect(center=title_rect.center)
        surface.blit(glow_surface, glow_rect)
        surface.blit(title_text, title_rect)

        subtitle_text = self.subtitle_font.render("The 52-Card Dungeon Crawler", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 40)
        surface.blit(subtitle_text, subtitle_rect)

        taglines = [
            "Navigate with cunning, defeat with paper cuts",
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
            "Don't give up! Gambate! Fighto!",
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
            "Gambling is illegal, but this is a dungeon!",
            "Flipping you off is a card game term!",
            "Original rules by Kurt Bieg and Zach Gage!",
            "You are not allowed a calculator on this exam",
            "Scoundrel this, scoundrel that",
            "You can drag the title cards around!",
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
            "I feel like we are connecting on a deeper level through this title screen...",
            "PyGame is a cruel mistress",
            "Scoundrel, shmoundrel!",
            "Scoundrel 2: Electric Boogaloo",
            "Sconedrel: Argue about how to pronounce it.",
            "SCOUNDRELLLLL!",
            "The sequel will be a dating sim.",
            "I slipped you a red 10 in there somewhere, thank me later <3",
            "Adventurer hires, merchants and gold coming soon!"
        ]

        if not hasattr(self, 'last_tagline_index'):
            self.last_tagline_index = -1

        if self.title_clicks > 0 and hasattr(self, 'last_click_count') and self.title_clicks > self.last_click_count:

            available_indices = [i for i in range(len(taglines)) if i != self.last_tagline_index]

            if len(self.seen_taglines) >= len(taglines) - 1:
                self.seen_taglines = {self.last_tagline_index}

            unseen_indices = [i for i in available_indices if i not in self.seen_taglines]
            seen_indices = [i for i in available_indices if i in self.seen_taglines]

            if unseen_indices and (not seen_indices or random.random() < 0.8):
                self.last_tagline_index = random.choice(unseen_indices)
            else:
                self.last_tagline_index = random.choice(seen_indices or available_indices)

            self.seen_taglines.add(self.last_tagline_index)

        self.last_click_count = self.title_clicks

        if self.title_clicks == 0:

            tagline = taglines[0]
        else:
            tagline = taglines[self.last_tagline_index]

        max_width = 600

        test_text = self.body_font.render(tagline, True, (200, 200, 200))

        if test_text.get_width() > max_width:

            words = tagline.split()
            total_words = len(words)
            middle_point = total_words // 2

            break_point = middle_point

            line1 = " ".join(words[:break_point])

            line2 = " ".join(words[break_point:])

            line1_text = self.body_font.render(line1, True, (200, 200, 200))
            line2_text = self.body_font.render(line2, True, (200, 200, 200))

            line1_rect = line1_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 15)
            line2_rect = line2_text.get_rect(centerx=SCREEN_WIDTH//2, top=line1_rect.bottom + 5)

            surface.blit(line1_text, line1_rect)
            surface.blit(line2_text, line2_rect)
        else:

            tagline_text = self.body_font.render(tagline, True, (200, 200, 200))
            tagline_rect = tagline_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 25)
            surface.blit(tagline_text, tagline_rect)

        self.start_button.draw(surface)
        self.tutorial_button.draw(surface)
        self.rules_button.draw(surface)

        for particle in self.particles:
            alpha = int(255 * particle['life'])
            particle_colour = (*particle['colour'], alpha)
            pygame.draw.circle(
                surface,
                particle_colour,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )

class TutorialState(GameState):
    """Tutorial state with typing text, animated merchant, and demo UI."""
    
    def __init__(self, game_manager, watch=False):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.name_font = None
        self.background = None
        self.floor = None
        
        self.watch = watch
        
        self.current_dialogue_index = 0
        self.dialogue_complete = False
        self.typing_complete = False
        
        self.current_text = ""
        self.target_text = ""
        self.char_index = 0
        self.typing_speed = 0.03  # seconds per character
        self.typing_timer = 0
        
        self.merchant_image = None
        self.merchant_shake_amount = 0
        self.merchant_base_pos = None
        
        self.dialogue_panel = None
        self.name_panel = None
        self.next_button = None
        self.skip_button = None
        
        self.dialogues = [
            {
                "speaker": "Mysterious Merchant",
                "graphic": None,
                "text": "Well, well, well... Another brave soul ventures into the depths of the dungeon!"
            },
            {
                "speaker": "Mysterious Merchant",
                "graphic": None,
                "text": "Welcome to the dungeon, adventurer! I am the Bartholomew, a merchant who trades in these dark halls."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "But you don't care about me, do you? You want to know how to survive in this place!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Very well then, let me explain the rules of this cruel mistress."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show 4 card room",
                "text": "Each floor is a deck of 52 cards. You'll face them in ROOMS OF 4 at a time."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the 2 monster cards",
                "text": "MONSTERS lurk in the Clubs and Spades. They'll damage you based on their value!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the weapon card",
                "text": "WEAPONS are found in Diamonds. Equip them to reduce damage from monsters."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the potion card",
                "text": "POTIONS hide in Hearts. They'll restore your precious health."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show weapon durability",
                "text": "But beware! Weapons lose DURABILITY with each use. They can only defeat weaker monsters after each battle."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show 4 cards and run button",
                "text": "Sometimes when you enter a new room, RUNNING is wise... but you can't run twice in a row!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Each floor's deck is UNIQUE, with some having more high cards than others, so don't try to card-count!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show inventory panel",
                "text": "Your inventory holds up to 2 red cards, either WEAPONS or POTIONS. Save them for when you need them most!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Now GO FORTH, brave adventurer! May fortune favor your draws!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "I might even see you again if you survive long enough!"
            }
        ]
        
        self.text_line_num = 1
        self.line_height = 30
        self.final_line_str = ""
        
        self.demo_cards = []
        self.demo_weapon = None
        self.demo_monsters = []
        self.demo_run_button = None
        self.demo_inventory_panel = None
        self.demo_position = None
        
        self.highlight_indices = []
        
    def enter(self):
        """Initialize tutorial state."""
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.name_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        self.merchant_image = ResourceLoader.load_image("hires/Merchant.png")
        merchant_scale = 14
        self.merchant_image = pygame.transform.scale(self.merchant_image, (int(self.merchant_image.get_width()*merchant_scale), int(self.merchant_image.get_height()*merchant_scale)))
        
        self.merchant_base_pos = (SCREEN_WIDTH - self.merchant_image.get_width() - 50, SCREEN_HEIGHT - self.merchant_image.get_height() - 40)
        
        self._create_ui()
        
        self._start_dialogue(0)

    def _create_demo_cards(self):
        """Create demonstration cards for the tutorial."""
        self.demo_cards = []
        
        for suit, value in [("clubs", 10), ("spades", 7), ("diamonds", 8), ("hearts", 5)]:
            card = Card(suit, value, "dungoen")
            card.face_up = True
            card.is_flipping = False
            self.demo_cards.append(card)

        self._position_demo_cards()
        
    def _create_weapon_durability_demo(self):
        """Create weapon and monster stack for durability demonstration."""
        self.demo_weapon = Card("diamonds", 12, "dungeon")
        self.demo_weapon.face_up = True
        self.demo_weapon.is_flipping = False
        
        self.demo_monsters = []
        monster_values = [12, 10, 8, 5]
        
        for value in monster_values:
            monster = Card("spades", value, "dungeon")
            monster.face_up = True
            monster.is_flipping = False
            self.demo_monsters.append(monster)
            
        weapon_x = self.demo_position[0] - 150
        weapon_y = self.demo_position[1]
        self.demo_weapon.update_position((weapon_x, weapon_y))
        
        start_x = weapon_x + 150
        for i, monster in enumerate(self.demo_monsters):
            monster_x = start_x + i * 30
            monster_y = weapon_y + i * 10
            monster.update_position((monster_x, monster_y))
            
    def _position_demo_cards(self):
        """Position the 4 demo cards centered on screen."""
        if not self.demo_cards:
            return
            
        card_spacing = 35
        total_width = (CARD_WIDTH * 4) + (card_spacing * 3)
        start_x = self.demo_position[0] - total_width // 2
        start_y = self.demo_position[1]
        
        for i, card in enumerate(self.demo_cards):
            card_x = start_x + i * (CARD_WIDTH + card_spacing)
            card.update_position((card_x, start_y))

    def _create_ui(self):
        """Create the UI panels and buttons."""
        panel_width = 700
        panel_height = 200
        panel_x = 50
        panel_y = SCREEN_HEIGHT - panel_height - 50
        
        self.dialogue_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 25),
            alpha=240,
            border_radius=10,
            dungeon_style=True,
            border_width=3,
            border_colour=(80, 60, 40)
        )
        self.demo_position = (self.dialogue_panel.rect.center[0], SCREEN_HEIGHT // 2 - 160)
        
        name_width = 300
        name_height = 40
        name_x = panel_x + 25
        name_y = panel_y - name_height + 10
        
        self.name_panel = Panel(
            (name_width, name_height),
            (name_x, name_y),
            colour=(50, 40, 35),
            alpha=240,
            border_radius=8,
            dungeon_style=True,
            border_width=2,
            border_colour=(90, 70, 50)
        )
        
        button_width = 140
        button_height = 50
        button_y = panel_y + panel_height - button_height - 15
        button_spacing = 20
        
        total_button_width = button_width * 2 + button_spacing
        button_start_x = panel_x + (panel_width - total_button_width) // 2
        
        next_button_rect = pygame.Rect(
            button_start_x,
            button_y,
            button_width,
            button_height
        )
        self.next_button = Button(
            next_button_rect,
            "NEXT",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 60, 40),
            border_colour=(70, 100, 70)
        )
        
        skip_button_rect = pygame.Rect(
            button_start_x + button_width + button_spacing,
            button_y,
            button_width,
            button_height
        )
        self.skip_button = Button(
            skip_button_rect,
            "SKIP ALL",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 40, 40),
            border_colour=(100, 70, 70)
        )
        
    def _start_dialogue(self, index):
        """Start displaying a new dialogue."""
        if index < len(self.dialogues):
            self.current_dialogue_index = index
            self.target_text = self.dialogues[index]["text"]
            self.current_text = ""
            self.char_index = 0
            self.typing_timer = 0
            self.typing_complete = False
            
            graphic_type = self.dialogues[index]["graphic"]
            self._setup_graphic(graphic_type)
            
    def _setup_graphic(self, graphic_type):
        """Set up the demonstration graphic for the current dialogue."""
        self.demo_cards = []
        self.demo_weapon = None
        self.demo_monsters = []
        self.demo_run_button = None
        self.demo_inventory_panel = None
        self.highlight_indices = []
        
        if graphic_type == "show 4 card room":
            self._create_demo_cards()
            
        elif graphic_type == "highlight the 2 monster cards":
            self._create_demo_cards()
            self.highlight_indices = [0, 1]  # first two cards are monsters
            
        elif graphic_type == "highlight the weapon card":
            self._create_demo_cards()
            self.highlight_indices = [2]  # third card is weapon
            
        elif graphic_type == "highlight the potion card":
            self._create_demo_cards()
            self.highlight_indices = [3]  # fourth card is potion
            
        elif graphic_type == "show weapon durability":
            self._create_weapon_durability_demo()
            
        elif graphic_type == "show 4 cards and run button":
            self._create_demo_cards()
            run_rect = pygame.Rect(
                self.demo_position[0] - 45,
                self.demo_position[1] - 90,
                90, 45
            )
            self.demo_run_button = Button(
                run_rect,
                "RUN",
                self.body_font,
                text_colour=WHITE,
                dungeon_style=True,
                panel_colour=(70, 20, 20),
                border_colour=(120, 40, 40)
            )
            
        elif graphic_type == "show inventory panel":
            inv_width = INVENTORY_PANEL_WIDTH
            inv_height = INVENTORY_PANEL_HEIGHT // 2  # just show top portion
            inv_x = self.demo_position[0] - inv_width // 2
            inv_y = self.demo_position[1] - 40
            
            self.demo_inventory_panel = Panel(
                (inv_width, inv_height),
                (inv_x, inv_y),
                colour=(60, 45, 35),
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)
            )
            
    def _complete_typing(self):
        """Instantly complete the current typing animation."""
        self.current_text = self.target_text
        self.char_index = len(self.target_text)
        self.typing_complete = True
        
    def handle_event(self, event):
        """Handle tutorial input events."""
        if event.type == MOUSEMOTION:
            self.next_button.check_hover(event.pos)
            self.skip_button.check_hover(event.pos)
            
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not self.typing_complete and self.dialogue_panel.rect.collidepoint(event.pos):
                self._complete_typing()
                return
                
            if self.typing_complete:
                if self.next_button.is_clicked(event.pos):
                    if self.current_dialogue_index < len(self.dialogues) - 1:
                        self._start_dialogue(self.current_dialogue_index + 1)
                    else:
                        if self.watch:
                            self.game_manager.change_state("title")
                        else:
                            self.game_manager.change_state("playing")
                        
                elif self.skip_button.is_clicked(event.pos):
                    if self.watch:
                        self.game_manager.change_state("title")
                    else:
                        self.game_manager.change_state("playing")
                    
    def update(self, delta_time):
        """Update tutorial animations and typing effect."""
        if not self.typing_complete and self.char_index < len(self.target_text):
            self.typing_timer += delta_time
            
            while self.typing_timer >= self.typing_speed and self.char_index < len(self.target_text):
                self.current_text += self.target_text[self.char_index]
                self.char_index += 1
                self.typing_timer -= self.typing_speed
                
                self.merchant_shake_amount = 2.0
                
            if self.char_index >= len(self.target_text):
                self.typing_complete = True
                
        if self.merchant_shake_amount > 0:
            self.merchant_shake_amount = max(0, self.merchant_shake_amount - delta_time * 10)
            
    def draw(self, surface):
        """Draw the tutorial screen."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - FLOOR_WIDTH)//2, (SCREEN_HEIGHT - FLOOR_HEIGHT)//2))
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        self._draw_demonstration_graphics(surface)
        
        if self.merchant_image:
            shake_x = 0
            shake_y = 0
            if self.merchant_shake_amount > 0:
                shake_x = random.uniform(-self.merchant_shake_amount, self.merchant_shake_amount)
                shake_y = random.uniform(-self.merchant_shake_amount * 0.5, self.merchant_shake_amount * 0.5)
                
            merchant_pos = (
                self.merchant_base_pos[0] + shake_x,
                self.merchant_base_pos[1] + shake_y
            )
            surface.blit(self.merchant_image, merchant_pos)
            
        self.dialogue_panel.draw(surface)
        
        self.name_panel.draw(surface)
        
        speaker_name = self.dialogues[self.current_dialogue_index]["speaker"]
        name_text = self.name_font.render(speaker_name, True, WHITE)
        name_rect = name_text.get_rect(center=self.name_panel.rect.center)
        surface.blit(name_text, name_rect)
        
        self._draw_wrapped_text(surface, self.current_text)
        
        if not self.typing_complete:
            cursor_x, cursor_y = self._get_cursor_position()
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
                cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, 20)
                pygame.draw.rect(surface, WHITE, cursor_rect)
                
        if self.typing_complete:
            self.next_button.draw(surface)
            self.skip_button.draw(surface)
            
            if self.current_dialogue_index == len(self.dialogues) - 1:
                self.next_button.update_text("BEGIN")
                
    def _draw_demonstration_graphics(self, surface):
        """Draw the demonstration graphics for the current dialogue."""
        if self.demo_cards:
            for i, card in enumerate(self.demo_cards):
                if self.highlight_indices and i not in self.highlight_indices:
                    dark_overlay = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 150))
                    card.draw(surface)
                    surface.blit(dark_overlay, card.rect.topleft)
                else:
                    card.draw(surface)
                    
            if self.highlight_indices:
                highlighted_cards = [self.demo_cards[i] for i in self.highlight_indices]
                if highlighted_cards:
                    min_x = min(card.rect.left for card in highlighted_cards)
                    max_x = max(card.rect.right for card in highlighted_cards)
                    min_y = min(card.rect.top for card in highlighted_cards)
                    max_y = max(card.rect.bottom for card in highlighted_cards)
                    
                    padding = 10
                    highlight_rect = pygame.Rect(
                        min_x - padding,
                        min_y - padding,
                        max_x - min_x + padding * 2,
                        max_y - min_y + padding * 2
                    )
                    pygame.draw.rect(surface, (255, 215, 0), highlight_rect, 3, border_radius=5)
                    
        if self.demo_weapon:
            self.demo_weapon.draw(surface)
            
        if self.demo_monsters:
            for monster in self.demo_monsters:
                monster.draw(surface)
                
        if self.demo_run_button:
            highlight_padding = 8
            highlight_rect = self.demo_run_button.rect.inflate(highlight_padding * 2, highlight_padding * 2)
            pygame.draw.rect(surface, (255, 215, 0), highlight_rect, 3, border_radius=8)
            
            self.demo_run_button.draw(surface)
            
        if self.demo_inventory_panel:
            self.demo_inventory_panel.draw(surface)
            
            inv_title = self.body_font.render("Inventory", True, WHITE)
            title_rect = inv_title.get_rect(
                centerx=self.demo_inventory_panel.rect.centerx,
                centery=self.demo_inventory_panel.rect.centery - 70
            )
            surface.blit(inv_title, title_rect)
                
    def _draw_wrapped_text(self, surface, text):
        """Draw text with word wrapping inside the dialogue panel."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        max_width = self.dialogue_panel.rect.width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = self.body_font.render(test_line, True, WHITE)
            
            if text_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        y_offset = self.dialogue_panel.rect.top + 30
        
        for line in lines:
            text_surface = self.body_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(
                left=self.dialogue_panel.rect.left + 20,
                top=y_offset
            )
            surface.blit(text_surface, text_rect)
            y_offset += self.line_height
        
        if self.text_line_num != len(lines):
            self.text_line_num = len(lines)
        
        self.final_line_str = lines[-1]

    def _get_cursor_position(self):
        """Calculate cursor position for typing effect."""
        text_start_x = self.dialogue_panel.rect.left + 20
        text_start_y = self.dialogue_panel.rect.top + 30
        
        x = self.body_font.render(self.final_line_str, True, WHITE).get_width() + text_start_x if self.current_text else text_start_x
        y = self.line_height * (self.text_line_num - 1) + text_start_y if self.current_text else text_start_y
        
        return (x, y)

class UIFactory:
    """Creates and manages UI elements."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def create_run_button(self):
        """Create the run button with dungeon styling."""

        run_width = 90
        run_height = 45

        run_x = SCREEN_WIDTH // 2
        run_y = 170

        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)

        self.playing_state.run_button = Button(
            run_button_rect,
            "RUN",
            self.playing_state.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(70, 20, 20),
            border_colour=(120, 40, 40)
        )

class UIRenderer:
    """Handles rendering of UI elements and game objects."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""

        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y
        health_bar_width = 140
        health_bar_height = 40

        if not hasattr(self, 'health_panel'):
            panel_rect = pygame.Rect(
                health_display_x - 10,
                health_display_y - health_bar_height - 20,
                health_bar_width + 20,
                health_bar_height + 20
            )

            self.health_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)
            )

        self.health_panel.draw(surface)

        bar_bg_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            health_bar_height
        )

        stone_bg = pygame.Surface((bar_bg_rect.width, bar_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(stone_bg, (50, 50, 55), pygame.Rect(0, 0, bar_bg_rect.width, bar_bg_rect.height), border_radius=5)

        for x in range(0, bar_bg_rect.width, 3):
            for y in range(0, bar_bg_rect.height, 3):

                noise = random.randint(0, 25)
                stone_colour = (50 + noise, 50 + noise, 55 + noise, 255)
                pygame.draw.rect(stone_bg, stone_colour, (x, y, 3, 3))

        surface.blit(stone_bg, bar_bg_rect.topleft)

        health_percent = self.playing_state.life_points / self.playing_state.max_life
        health_width = int(health_bar_width * health_percent)

        if health_percent > 0.7:
            health_colour = (50, 220, 100)
            glow_colour = (100, 255, 150, 40)
        elif health_percent > 0.3:
            health_colour = (255, 155, 20)
            glow_colour = (255, 180, 50, 40)
        else:
            health_colour = (255, 30, 30)
            glow_colour = (255, 70, 70, 40)

        if health_width > 0:
            health_rect = pygame.Rect(
                health_display_x,
                health_display_y - health_bar_height - 10,
                health_width,
                health_bar_height
            )

            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)

            glow_surf = pygame.Surface((health_width, health_bar_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_colour, pygame.Rect(0, 0, health_width, health_bar_height), border_radius=5)

            surface.blit(glow_surf, health_rect.topleft)

        shadow_rect = pygame.Rect(
            health_display_x,
            health_display_y - health_bar_height - 10,
            health_bar_width,
            8
        )
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        surface.blit(shadow_surface, shadow_rect)

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

        health_text = self.playing_state.body_font.render(f"{self.playing_state.life_points}/{self.playing_state.max_life}", True, WHITE)
        health_text_rect = health_text.get_rect(center=bar_bg_rect.center)

        glow_surf = pygame.Surface((health_text.get_width() + 10, health_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 255, 255, 30), glow_surf.get_rect())
        glow_rect = glow_surf.get_rect(center=health_text_rect.center)

        surface.blit(glow_surf, glow_rect)
        surface.blit(health_text, health_text_rect)

    def draw_deck_count(self, surface):
        """Draw deck card counter display with current and total cards."""

        count_panel_width = 80
        count_panel_height = 40
        count_panel_x = 87 + CARD_WIDTH//2 - count_panel_width//2
        count_panel_y = 35 + (len(self.playing_state.deck.cards)-1)*3 + CARD_HEIGHT//2 - count_panel_height//2

        if not hasattr(self, 'count_panel'):
            panel_rect = pygame.Rect(
                count_panel_x,
                count_panel_y,
                count_panel_width,
                count_panel_height
            )

            self.count_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)
            )
        else:

            self.count_panel.rect.topleft = (count_panel_x, count_panel_y)

        self.count_panel.draw(surface)

        count_text = self.playing_state.caption_font.render(f"{len(self.playing_state.deck.cards)}/{DECK_TOTAL_COUNT}", True, WHITE)
        count_text_rect = count_text.get_rect(center=self.count_panel.rect.center)
        surface.blit(count_text, count_text_rect)

    def _draw_card_shadow(self, surface, card):
        """Draw shadow effect for a card"""
        shadow_alpha = 60
        shadow_width = 4
        shadow_rect = card.rect.inflate(shadow_width * 2, shadow_width * 2)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=3)
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

def isolate_card_corners(image_path, output_path):
    """Keeps only the suit and rank in the top-left and bottom-right corners of a playing card image."""
    img = Image.open(image_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    corner_width = int(width / 4.6)
    corner_height = int(height / 3)

    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]

            if not ((x < corner_width and y < corner_height) or (x > width - corner_width - (5 if "10" in image_path else 0) and y > height - corner_height)):
                if a > 0:
                    pixels[x, y] = (255, 255, 255, 255)

    img.save(output_path, "PNG")

def process_all_cards(input_folder):
    """Processes all card images in the given folder that start with clubs, hearts, diamonds, or spades."""
    for filename in os.listdir(input_folder):
        if filename.startswith(("clubs", "hearts", "diamonds", "spades")) and filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(input_folder, filename)
            isolate_card_corners(input_path, output_path)

async def main():
    """ Main entry point for the game. """
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scoundrel - The 52-Card Roguelike Dungeon Crawler")
    clock = pygame.time.Clock()

    game_manager = GameManager()

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                game_manager.handle_event(event)
        game_manager.update(delta_time)
        game_manager.draw(screen)
        pygame.display.flip()
        
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
