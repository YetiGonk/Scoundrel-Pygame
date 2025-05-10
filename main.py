"""
    Scoundrel - The 52-Card Roguelike Dungeon Crawler

    A roguelike card game where you navigate through multiple floors of monsters, 
    weapons, and potions.
"""

import math
import os
import sys
import random
import pygame
from glob import glob
from PIL import Image
from pygame.locals import *

# Screen dimensions
SCREEN_WIDTH = 1222
SCREEN_HEIGHT = 686
FLOOR_WIDTH = 750
FLOOR_HEIGHT = 617
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (64, 64, 64)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
CARD_RED = (171, 82, 54)

# UI Colors
GOLD_COLOR = (255, 215, 0)
GOLD_HIGHLIGHT = (255, 240, 120)
GOLD_BORDER = (184, 134, 11)
GOLD_TEXT = (255, 230, 150)

HEALTH_COLOR_GOOD = (50, 180, 50)
HEALTH_COLOR_WARNING = (220, 160, 40)
HEALTH_COLOR_DANGER = (200, 50, 50)

HEALTH_GLOW_GOOD = (70, 220, 70, 40)
HEALTH_GLOW_WARNING = (240, 180, 60, 40)
HEALTH_GLOW_DANGER = (240, 90, 90, 40)

# UI Panel Colors
PANEL_DEFAULT_BORDER = (80, 60, 40)
PANEL_WOODEN = (80, 60, 30)
PANEL_WOODEN_BORDER = (130, 100, 40)
PANEL_HEALTH = (60, 30, 30)
PANEL_HEALTH_BORDER = (100, 50, 50)


# Effect Colors
EFFECT_HEALING_COLOR = (60, 180, 80)
EFFECT_HEALING_PANEL = (40, 100, 50)
EFFECT_HEALING_BORDER = (70, 190, 90)
EFFECT_DAMAGE_COLOR = (190, 60, 60)
EFFECT_DAMAGE_PANEL = (100, 40, 40)
EFFECT_DAMAGE_BORDER = (200, 70, 70)
EFFECT_GOLD_COLOR = (220, 180, 50)
EFFECT_GOLD_PANEL = (100, 80, 30)
EFFECT_GOLD_BORDER = (230, 190, 60)
EFFECT_DEFAULT_COLOR = (100, 100, 160)
EFFECT_DEFAULT_PANEL = (50, 50, 80)
EFFECT_DEFAULT_BORDER = (120, 120, 180)

# Card dimensions
CARD_WIDTH = 99
CARD_HEIGHT = 135   

# UI positions and sizes
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

# UI HUD dimensions
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 24
HEALTH_BAR_POSITION = (20, SCREEN_HEIGHT - 30)

GOLD_BAR_WIDTH = 200
GOLD_BAR_HEIGHT = 24
GOLD_BAR_POSITION = (HEALTH_BAR_POSITION[0], HEALTH_BAR_POSITION[1] - GOLD_BAR_HEIGHT - 10)

EFFECT_ICON_SIZE = 40
EFFECT_ICON_SPACING = 10
EFFECT_START_POSITION = (SCREEN_WIDTH//2 - 100, 20)

# UI styling parameters
PANEL_BORDER_RADIUS = 8
PANEL_ALPHA = 230
PANEL_BORDER_WIDTH = 2

# Button styling
BUTTON_PANEL_COLOR = (60, 45, 35)
BUTTON_BORDER_WIDTH = 3
BUTTON_BORDER_RADIUS = 8
BUTTON_ALPHA = 250
BUTTON_GLOW_SIZE = 6
BUTTON_HOVER_GLOW_WHITE = (255, 255, 255, 30)
BUTTON_HOVER_GLOW_DARK = (0, 0, 0, 30)
BUTTON_HOVER_LIGHTEN = 0.3
BUTTON_ROUND_CORNER = 5

# Animation constants
GOLD_CHANGE_DURATION = 2000  # ms
GOLD_PARTICLE_FADE_SPEED = (0.5, 1.5)
GOLD_PARTICLE_SPEED = (0.2, 0.6)
GOLD_PARTICLE_SIZE = (1, 2.5)
GOLD_PARTICLE_SPREAD = 5  # px

EFFECT_PULSE_PERMANENT = (0.9, 0.1, 800)  # base, amplitude, frequency
EFFECT_PULSE_TEMPORARY = (0.8, 0.2, 200)  # base, amplitude, frequency
EFFECT_EXPIRE_THRESHOLD = 2000  # ms

# Game settings
STARTING_HEALTH = 20
MAX_HEALTH = 20

# Deck creation constants
DECK_TOTAL_COUNT = 3
DECK_MONSTER_COUNT = (1, 2) # (min, max)
DECK_BLACK_VALUE_RANGE = (2, 14) # (min, max)
DECK_HEARTS_VALUE_RANGE = (2, 10) # (min, max)
DECK_DIAMONDS_VALUE_RANGE = (2, 10) # (min, max)

# File paths
ASSETS_PATH = "assets"
CARDS_PATH = f"{ASSETS_PATH}/cards"
FONTS_PATH = f"{ASSETS_PATH}/fonts"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
BACKGROUNDS_PATH = f"{ASSETS_PATH}/backgrounds"

# Font settings
TITLE_FONT_SIZE = 64
HEADER_FONT_SIZE = 36
BODY_FONT_SIZE = 28
NORMAL_FONT_SIZE = 20
FONT_FILE = f"{FONTS_PATH}/Pixel Times.ttf"

# Decks
SUITS = ["diamonds", "hearts", "spades", "clubs"]

# Debug mode settings
DEBUG_MODE = True  # Set to True to enable debug features

# Floor names
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

# Starting player attributes
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
    
    _image_cache = {}  # Class variable to cache loaded images
    _font_cache = {}   # Class variable to cache loaded fonts
    
    @classmethod
    def load_image(cls, name, scale=1, cache=True):
        # Check if the image is already in the cache
        cache_key = f"{name}_{scale}"
        if cache and cache_key in cls._image_cache:
            return cls._image_cache[cache_key]
        
        try:
            # Load the image
            image_path = os.path.join(ASSETS_PATH, name)
            image = pygame.image.load(image_path)
            
            # Scale the image if needed
            if scale != 1:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            
            # Cache the image if requested
            if cache:
                cls._image_cache[cache_key] = image
                
            return image
        except pygame.error as e:
            print(f"Cannot load image: {image_path}")
            print(e)
            # Return a placeholder surface
            return pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    
    @classmethod
    def load_font(cls, name, size):
        # Check if the font is already in the cache
        cache_key = f"{name}_{size}"
        if cache_key in cls._font_cache:
            return cls._font_cache[cache_key]
        
        try:
            # Load the font
            font_path = os.path.join(ASSETS_PATH, name)
            print(f"Loading font from: {font_path}")
            font = pygame.font.Font(font_path, size)
            
            # Cache the font
            cls._font_cache[cache_key] = font
                
            return font
        except pygame.error as e:
            print(f"Cannot load font: {font_path}")
            print(e)
            # Return a system font as fallback
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
        # First create a destruction animation
        
        # Choose a random destruction effect based on card type
        if card.type == "monster":
            effect_type = "slash"  # Monsters get slashed
        elif card.type == "weapon":
            effect_type = "shatter"  # Weapons shatter
        elif card.type == "potion":
            effect_type = "burn"  # Potions burn away
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
        # Update card position to discard pile
        card.update_position(self.playing_state.discard_pile.position)
        
        # Create materialise animation
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
        """Position defeated monsters in a stack.
        
        Args:
            preserve_positions: If True, don't change positions of cards that already have positions
        """
        if not self.playing_state.defeated_monsters or "node" not in self.playing_state.equipped_weapon:
            return        
        # Determine if weapon is at default position or has a custom position
        weapon_card = self.playing_state.equipped_weapon["node"]
        is_default_weapon_position = (weapon_card.rect.x == WEAPON_POSITION[0] and weapon_card.rect.y == WEAPON_POSITION[1])
        
        # Calculate starting position for monster stack
        start_x = weapon_card.rect.x + MONSTER_START_OFFSET[0]
        
        # Position each monster card in the stack
        for i, monster in enumerate(self.playing_state.defeated_monsters):
            # Check if monster already has a valid position and we're preserving positions
            has_valid_position = hasattr(monster, 'rect') and monster.rect.x > 0 and monster.rect.y > 0
            
            # Calculate new position for this monster
            new_stack_position = (
                start_x + i * MONSTER_STACK_OFFSET[0],
                weapon_card.rect.y + MONSTER_STACK_OFFSET[1] * i
            )
            
            # Only position if doesn't have valid position or we're not preserving positions
            if not has_valid_position or not preserve_positions:
                self.animate_card_movement(monster, new_stack_position)
        
        # Move the weapon slightly left to make room for monster stack
        # Only do this if weapon is at the default position (not custom loaded position)
        if is_default_weapon_position:
            new_weapon_position = (
                weapon_card.rect.x - MONSTER_STACK_OFFSET[1]*2,
                weapon_card.rect.y
            )
            self.animate_card_movement(weapon_card, new_weapon_position)
    
    def schedule_delayed_animation(self, delay, callback):
        """Schedule an animation to start after a delay."""
        # Add a "timer" animation that does nothing except wait
        # When it completes, it will run the callback to create the real animation
        timer = Animation(delay, on_complete=callback)
        self.playing_state.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        """Start the flip animation for a card."""
        card.start_flip()
    
    def animate_health_change(self, is_damage, amount):
        """Create animation for health change."""
        # Position for the animation
        health_display_x = self.playing_state.deck.rect.x + 100  # Center of health bar
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y - 30  # Middle of health bar
        
        # Create animation
        health_anim = HealthChangeAnimation(
            is_damage,
            amount,
            (health_display_x, health_display_y),
            self.playing_state.body_font
        )
        
        # Add to animation manager
        self.playing_state.animation_manager.add_animation(health_anim)
    
    def animate_card_to_inventory(self, card):
        """Animate a card moving to its position in the inventory."""
        # Define inventory panel location - match the dimensions in playing_state.py
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Use standard card size (no scaling) for inventory cards
        card_scale = 1.0
        
        # Scale the card
        card.update_scale(card_scale)
        
        # Mark card as being in inventory to reduce animations
        card.in_inventory = True
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Center X position (horizontally centered in panel)
        inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)
        
        # Get number of cards in inventory (including this new one)
        num_cards = len(self.playing_state.inventory)
        
        # Calculate Y position based on number of cards
        if num_cards == 1:
            # Single card - center vertically in panel
            inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
        elif num_cards == 2:
            # If this is the second card, position cards one above center, one below center
            # Reposition existing card to top position
            existing_card = self.playing_state.inventory[0]
            top_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
            
            # Only reposition if it's not already at the right position
            if existing_card.rect.y != top_y:
                self.animate_card_movement(existing_card, (inventory_x, top_y))
            
            # Position new card in bottom half
            inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)
        
        inventory_pos = (inventory_x, inventory_y)
        
        # Animate the card movement
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
        
        # Calculate the current position
        progress = self.easing_function(self.get_progress())
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        # Update the target object's position
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
        
        # Based on effect type, setup initial animation state
        if effect_type == "slash":
            # Create slash line data - more diagonal angle
            self.slash_angle = random.randint(25, 65)
            self.slash_direction = 1 if random.random() > 0.5 else -1
            self.slash_width = 4
            self.slash_colour = (200, 200, 200)  # Silver/grey colour for sword
            
        elif effect_type == "burn":
            # Create particles for burning effect
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(3, 8),
                    'speed_y': -random.random() * 2 - 1,
                    'colour': (
                        random.randint(200, 255),  # Red
                        random.randint(50, 150),   # Green
                        0                          # Blue
                    )
                })
                
        elif effect_type == "shatter":
            # Create particles for shatter effect
            for _ in range(15):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(5, 15),
                    'speed_x': (random.random() - 0.5) * 6,
                    'speed_y': (random.random() - 0.5) * 6,
                    'rotation': random.randint(0, 360),
                    'colour': (100, 200, 255)  # Light blue for shatter
                })
    
    def draw(self, surface):
        progress = self.get_progress()
        
        if self.effect_type == "slash":
            if progress < 0.4:  # First phase: show card with moving slash line
                # Draw the card
                self.target_object.draw(surface)
                
                # Draw moving slash line
                slash_progress = progress / 0.4  # Scale to 0-1 range
                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                slash_length = self.target_object.rect.width * 1.4  # Longer slash
                
                # Calculate slash position based on progress
                # Moving from top-left to bottom-right (or opposite depending on direction)
                offset = (slash_progress - 0.5) * self.target_object.rect.width * 1.5
                
                # Start position
                start_x = center_x - slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                start_y = center_y - slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3
                
                # End position
                end_x = center_x + slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                end_y = center_y + slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3
                
                # Draw slash glow (slightly larger white line behind)
                pygame.draw.line(
                    surface, 
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width + 2
                )
                
                # Draw the slash line
                pygame.draw.line(
                    surface, 
                    self.slash_colour,
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width
                )
                
                # Draw small sparkles along the slash
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
                
            elif progress < 0.55:  # Second phase: slight pause with visible cut
                # Draw the card
                self.target_object.draw(surface)
                
                # Draw cut line
                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                cut_length = self.target_object.rect.width * 1.2
                
                # Start position
                start_x = center_x - cut_length/2 * math.cos(math.radians(self.slash_angle))
                start_y = center_y - cut_length/2 * math.sin(math.radians(self.slash_angle))
                
                # End position
                end_x = center_x + cut_length/2 * math.cos(math.radians(self.slash_angle))
                end_y = center_y + cut_length/2 * math.sin(math.radians(self.slash_angle))
                
                # Draw the cut line - thin white line
                pygame.draw.line(
                    surface, 
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    2
                )
                
            else:  # Third phase: card splits apart
                # Calculate split distance - non-linear for more dramatic effect
                split_progress = (progress - 0.55) / 0.45  # Scale to 0-1 range
                split_distance = 120 * math.pow(split_progress, 1.5)  # Accelerating movement
                
                # Calculate split line angle and cut position
                cut_height = self.target_object.rect.height * 0.5  # Default to middle
                
                # Add slight rotation to each half
                rotation = 5 * split_progress * self.slash_direction
                
                # Draw top half
                top_half = self.target_object.texture.subsurface(
                    (0, 0, self.target_object.rect.width, int(cut_height))
                )
                # Rotate top half if needed
                if rotation != 0:
                    top_half = pygame.transform.rotate(top_half, -rotation)
                    
                surface.blit(
                    top_half, 
                    (
                        self.target_object.rect.x - split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y - split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )
                
                # Draw bottom half
                bottom_half = self.target_object.texture.subsurface(
                    (0, int(cut_height), 
                     self.target_object.rect.width, self.target_object.rect.height - int(cut_height))
                )
                
                # Rotate bottom half if needed
                if rotation != 0:
                    bottom_half = pygame.transform.rotate(bottom_half, rotation)
                    
                surface.blit(
                    bottom_half, 
                    (
                        self.target_object.rect.x + split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y + cut_height + split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )
                
                # Add some small particles/sparkles at the cut point
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
            if progress < 0.4:  # First phase: show card
                # Scale card based on progress (slight shrinking)
                scale = 1.0 - progress * 0.2
                self.target_object.update_scale(scale)
                self.target_object.draw(surface)
                
                # Draw fire particles
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
            elif progress < 0.7:  # Second phase: card burns away
                burn_progress = (progress - 0.4) / 0.3  # Normalise to 0-1
                # Draw partially burned card (decreasing height)
                height = int(self.target_object.rect.height * (1 - burn_progress))
                if height > 0:
                    card_texture = self.target_object.texture.subsurface(
                        (0, 0, self.target_object.rect.width, height)
                    )
                    surface.blit(card_texture, (self.target_object.rect.x, self.target_object.rect.y))
                
                # Draw more fire particles
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
            # In final phase: card is completely gone, just some lingering particles
            else:
                fade_progress = (progress - 0.7) / 0.3  # Normalise to 0-1
                # Draw fading particles
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
            if progress < 0.3:  # First phase: card shakes
                shake_amount = 3 * math.sin(progress * 20)
                shake_x = self.original_position[0] + shake_amount
                shake_y = self.original_position[1] + shake_amount * 0.5
                self.target_object.update_position((shake_x, shake_y))
                self.target_object.draw(surface)
            else:  # Second phase: card shatters
                shatter_progress = (progress - 0.3) / 0.7  # Normalise to 0-1
                
                # Draw fading original card
                if shatter_progress < 0.5:
                    fade_alpha = int(255 * (1 - shatter_progress * 2))
                    if fade_alpha > 0:
                        original_texture = self.target_object.texture.copy()
                        # Create surface with alpha
                        faded_texture = pygame.Surface(original_texture.get_size(), pygame.SRCALPHA)
                        faded_texture.fill((255, 255, 255, fade_alpha))
                        # Use blend mode to apply alpha
                        faded_texture.blit(original_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        surface.blit(faded_texture, self.target_object.rect.topleft)
                
                # Draw particles
                for particle in self.particles:
                    # Apply velocity to position
                    current_x = particle['x'] + particle['speed_x'] * 100 * shatter_progress
                    current_y = particle['y'] + particle['speed_y'] * 100 * shatter_progress
                    
                    # Rotate and scale
                    rotation = particle['rotation'] + shatter_progress * 360
                    scale = 1.0 - shatter_progress * 0.8
                    
                    # Create a small card-like fragment
                    size = int(particle['size'] * scale)
                    if size > 2:
                        fragment = pygame.Surface((size, size), pygame.SRCALPHA)
                        pygame.draw.rect(
                            fragment,
                            particle['colour'],
                            pygame.Rect(0, 0, size, size)
                        )
                        
                        # Rotate fragment
                        fragment = pygame.transform.rotate(fragment, rotation)
                        
                        # Draw with fade out
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
        
        # Make the card invisible when animation is completed
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
        
        # Set initial card position
        self.target_object.update_position(position)
        self.target_object.is_visible = True
        
        # Initialise effect
        if effect_type == "sparkle":
            # Create sparkle particles
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(-20, target_object.rect.width + 20),
                    'y': random.randint(-20, target_object.rect.height + 20),
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 1,
                    'angle': random.random() * 360,
                    'colour': (
                        random.randint(200, 255),  # R
                        random.randint(200, 255),  # G
                        random.randint(100, 200)   # B
                    )
                })
    
    def draw(self, surface):
        progress = self.get_progress()
        
        if self.effect_type == "sparkle":
            # Draw card with increasing opacity
            if progress < 0.7:
                # Scale from small to full size
                scale = 0.2 + progress * 1.1  # Start small and grow slightly bigger than 1.0
                if scale > 1.0 and progress > 0.6:  # Then shrink back to 1.0
                    scale = 1.0 + (0.7 - progress) * 2
                
                self.target_object.update_scale(scale)
                
                # Draw with increasing opacity
                alpha = int(min(255, progress * 2 * 255))
                card_texture = self.target_object.texture.copy()
                card_texture.set_alpha(alpha)
                surface.blit(card_texture, self.target_object.rect.topleft)
            else:
                # Card is fully visible
                self.target_object.update_scale(1.0)
                self.target_object.draw(surface)
            
            # Draw particles
            for particle in self.particles:
                # Calculate current position based on progress
                radius = particle['speed'] * progress * 50
                x = self.target_object.rect.centerx + particle['x'] + math.cos(math.radians(particle['angle'])) * radius
                y = self.target_object.rect.centery + particle['y'] + math.sin(math.radians(particle['angle'])) * radius
                
                # Calculate size (grows then shrinks)
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
        
        # Make sure card is fully visible when animation completes
        if completed:
            self.target_object.is_visible = True
            self.target_object.update_scale(1.0)
            
        return completed


class HealthChangeAnimation(Animation):
    """Animation for displaying health changes with effects."""
    
    def __init__(self, is_damage, amount, position, font, duration=0.8, on_complete=None):
        super().__init__(duration, on_complete)
        self.is_damage = is_damage  # True for damage, False for healing
        self.amount = amount
        self.position = position
        self.font = font
        self.particles = []
        
        # Create particles
        num_particles = min(20, max(5, abs(amount) * 2))
        for _ in range(num_particles):
            self.particles.append({
                'x': random.randint(-10, 10),
                'y': random.randint(-5, 5),
                'speed_x': (random.random() - 0.5) * 5,
                'speed_y': -random.random() * 8 - 2,  # Upward bias
                'size': random.randint(3, 7),
                'fade_speed': random.random() * 0.3 + 0.7
            })
    
    def draw(self, surface):
        progress = self.get_progress()
        
        # Early animation: text grows and brightens
        if progress < 0.4:
            scale = 1.0 + progress * 0.5  # Text grows a bit
            alpha = int(255 * min(1.0, progress * 3))
        # Middle animation: text stays steady
        elif progress < 0.7:
            scale = 1.2
            alpha = 255
        # End animation: text fades out
        else:
            fade_progress = (progress - 0.7) / 0.3
            scale = 1.2 - fade_progress * 0.2
            alpha = int(255 * (1 - fade_progress))
        
        # Choose colour based on damage/healing
        if self.is_damage:
            colour = (255, 80, 80)  # Red for damage
            text_prefix = "-"
        else:
            colour = (80, 255, 80)  # Green for healing
            text_prefix = "+"
            
        # Render text with proper prefix
        text = self.font.render(f"{text_prefix}{abs(self.amount)}", True, colour)
        
        # Scale text
        if scale != 1.0:
            orig_size = text.get_size()
            text = pygame.transform.scale(
                text, 
                (int(orig_size[0] * scale), int(orig_size[1] * scale))
            )
        
        # Set alpha if needed
        if alpha < 255:
            text.set_alpha(alpha)
        
        # Draw text
        text_rect = text.get_rect(center=(
            self.position[0],
            self.position[1] - 40 * progress  # Text rises upward
        ))
        surface.blit(text, text_rect)
        
        # Draw particles
        for particle in self.particles:
            # Update particle position based on progress
            particle_x = self.position[0] + particle['x'] + particle['speed_x'] * progress * 60
            particle_y = self.position[1] + particle['y'] + particle['speed_y'] * progress * 60
            
            # Calculate alpha (particles fade out)
            particle_alpha = int(255 * (1 - progress * particle['fade_speed']))
            
            # Calculate size (particles slightly shrink)
            particle_size = max(1, int(particle['size'] * (1 - progress * 0.5)))
            
            # Skip completely faded particles
            if particle_alpha <= 10 or particle_size <= 0:
                continue
                
            # Draw particle
            particle_colour = colour + (particle_alpha,)  # Add alpha as 4th component
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_colour, (particle_size, particle_size), particle_size)
            surface.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))


class AnimationManager:
    """Manager for handling multiple animations."""
    
    def __init__(self):
        self.animations = []
        self.effect_animations = []  # Separate list for visual effects that need to be drawn
        self.ui_animations = []  # Animations for UI effects (health changes, etc.)
    
    def add_animation(self, animation):
        self.animations.append(animation)
        
        # Check what type of animation this is
        if isinstance(animation, (DestructionAnimation, MaterialiseAnimation)):
            self.effect_animations.append(animation)
        elif isinstance(animation, (HealthChangeAnimation)):
            self.ui_animations.append(animation)
    
    def update(self, delta_time):
        # Update all animations and remove completed ones
        self.animations = [anim for anim in self.animations if not anim.update(delta_time)]
        
        # Also update specialised animation lists
        self.effect_animations = [anim for anim in self.effect_animations if not anim.is_completed]
        self.ui_animations = [anim for anim in self.ui_animations if not anim.is_completed]
    
    def draw_effects(self, surface):
        # Draw all visual effect animations
        for animation in self.effect_animations:
            animation.draw(surface)
    
    def draw_ui_effects(self, surface):
        # Draw all UI animations
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
        
        # For inventory cards, determine which part was clicked
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
            
            # Monster will be added to stack or discard
            if self.playing_state.defeated_monsters:
                if self.playing_state.defeated_monsters[-1].value > monster_value:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0
                    
                    # Apply damage with animation
                    if damage > 0:
                        self.playing_state.change_health(-damage)
                    
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1
                    
                    # Add to defeated monster stack
                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:
                    # Apply damage with animation
                    if monster_value > 0:
                        self.playing_state.change_health(-monster_value)
                        
                        # Animate to discard pile
                        self.playing_state.animate_card_to_discard(monster)
            else:
                if monster_value <= weapon_value:
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1
                    # Mark monster as defeated for proper hover behavior
                    monster.is_defeated = True
                    # Add to defeated monster stack
                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
                else:
                    damage = monster_value - weapon_value
                    if damage < 0:
                        damage = 0
                    
                    # Apply damage with animation
                    if damage > 0:
                        self.playing_state.change_health(-damage)
                    
                    monster.z_index = self.playing_state.z_index_counter
                    self.playing_state.z_index_counter += 1
                    # Mark monster as defeated for proper hover behavior
                    monster.is_defeated = True
                    # Add to defeated monster stack
                    self.playing_state.defeated_monsters.append(monster)
                    self.playing_state.position_monster_stack()
        else:
            # No weapon equipped - take full damage
            # Apply damage with animation
            if monster_value > 0:
                self.playing_state.change_health(-monster_value)
            
            # Animate to discard pile
            self.playing_state.animate_card_to_discard(monster)
                
        # After processing the monster, reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            # Add a slight delay before repositioning room cards
            self.playing_state.schedule_delayed_animation(
                0.1,
                lambda: self.playing_state.room.position_cards(
                    animate=True, 
                    animation_manager=self.playing_state.animation_manager
                )
            )
    
    def equip_weapon(self, weapon):
        """Equip a weapon card."""
        
        # First clear previous weapon and monsters
        old_weapon = self.playing_state.equipped_weapon.get("node", None)
        old_monsters = self.playing_state.defeated_monsters.copy()
        
        # Update data structures first
        self.playing_state.room.remove_card(weapon)
        
        # Mark the weapon as equipped (for hover text)
        weapon.is_equipped = True
        
        # Store weapon type in the equipped weapon dictionary
        self.playing_state.equipped_weapon = {
            "suit": weapon.suit, 
            "value": weapon.value,
            "node": weapon,
            "difficulty": weapon.weapon_difficulty,
        }
        self.playing_state.defeated_monsters = []
        
        # Set z-index for new weapon
        weapon.z_index = self.playing_state.z_index_counter
        self.playing_state.z_index_counter += 1
        
        # Animate new weapon equipping first
        self.playing_state.animate_card_movement(weapon, WEAPON_POSITION)
        
        # Show standard equipped message
        self.playing_state.show_message(f"Equipped {weapon.name}")
        
        # Now discard old weapon and monsters
        if old_weapon or old_monsters:
            for i, monster in enumerate(old_monsters):
                # Add a slight delay for each monster
                delay = 0.08 * i
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=monster: self.playing_state.animate_card_to_discard(card)
                )
            
            # Discard old weapon last if it exists
            if old_weapon:
                delay = 0.08 * len(old_monsters)
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda: self.playing_state.animate_card_to_discard(old_weapon)
                )
    
    def use_potion(self, potion):
        """Use a potion card to heal the player."""
        # Apply healing with animation
        self.playing_state.change_health(potion.value)
        
        # First ensure the potion is removed from the room
        self.playing_state.room.remove_card(potion)
        
        # Animate potion moving to discard pile
        self.playing_state.animate_card_to_discard(potion)
        
        # After processing the potion, reposition remaining room cards
        if len(self.playing_state.room.cards) > 0:
            # Add a slight delay before repositioning room cards
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
            # Inventory is full, can't add more cards
            return False
        
        # Mark the card as selected to remove split colours
        card.is_selected = True
        
        # Mark the card as being in inventory to reduce animation
        card.in_inventory = True
        
        # Remove the card from the room
        self.playing_state.room.remove_card(card)
        
        # Add to inventory
        self.playing_state.inventory.append(card)
        
        # Animate the card moving to its inventory position
        self.playing_state.animate_card_to_inventory(card)
        
        # Reposition remaining room cards
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
            # Temporarily mark the card as selected during processing
            card.is_selected = True
            
            # Default action is to use the card (equip weapon or use potion)
            discard_only = False
            
            # If click position is provided, determine which part was clicked
            if event_pos:
                # Calculate position of the card's visual midpoint
                center_x = card.rect.centerx 
                
                # For the Y position, we need to account for the float offset
                total_float_offset = 0
                if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                    total_float_offset = card.idle_float_offset + card.hover_float_offset
                
                # Calculate center Y with float offset
                center_y = card.rect.centery - total_float_offset
                
                # Check which half was clicked
                if event_pos[1] < center_y:
                    # Top half clicked - discard card
                    discard_only = True
                    card.hover_selection = "top"
                else:
                    # Bottom half clicked - use card (equip weapon or use potion)
                    discard_only = False
                    card.hover_selection = "bottom"
            
            # Reset inventory flag since it's being removed
            card.in_inventory = False
            
            # Remove from inventory
            self.playing_state.inventory.remove(card)
            
            # Reposition remaining inventory cards
            self.playing_state.position_inventory_cards()
            
            # Process the card effect based on type and action
            if card.type == "weapon":
                if discard_only:
                    # Show message about discarding
                    self.playing_state.show_message(f"{card.name} discarded")
                    # Discard the card
                    self.playing_state.animate_card_to_discard(card)
                else:
                    # Reset the card's scale back to original size (1.0)
                    card.update_scale(1.0)
                    # Add the card back to the room temporarily
                    self.playing_state.room.add_card(card)
                    # Use the standard equip weapon logic
                    self.equip_weapon(card)
            elif card.type == "potion":
                if discard_only:
                    # Show message about discarding potion
                    self.playing_state.show_message(f"{card.name} discarded")
                    # Discard the potion
                    self.playing_state.animate_card_to_discard(card)
                else:
                    # Use the potion effect directly
                    self.playing_state.change_health(card.value)
                    # Show message about using potion
                    self.playing_state.show_message(f"Used {card.name}. Restored {card.value} health.")
                    # Discard the potion
                    self.playing_state.animate_card_to_discard(card)
            else:
                # For any other card type that doesn't have a specific use
                # Just discard it when clicked
                self.playing_state.show_message(f"{card.name} discarded")
                self.playing_state.animate_card_to_discard(card)
    
    def discard_equipped_weapon(self):
        """Discard the currently equipped weapon."""
        if self.playing_state.equipped_weapon and "node" in self.playing_state.equipped_weapon:
            weapon = self.playing_state.equipped_weapon["node"]
            
            # Clear the equipped weapon
            self.playing_state.equipped_weapon = {}
            
            # Reset equipped flag
            weapon.is_equipped = False
            
            # Show message about discarding weapon
            self.playing_state.show_message(f"{weapon.name} discarded")
            
            # Discard the weapon card
            self.playing_state.animate_card_to_discard(weapon)
            
            # Also discard any defeated monsters
            for monster in self.playing_state.defeated_monsters:
                self.playing_state.animate_card_to_discard(monster)
            
            # Clear the defeated monsters list
            self.playing_state.defeated_monsters = []
            
            return True
        return False

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
        self.name = None
        
        # Card subtype properties
        self.damage_type = None  # "piercing", "slashing", or "bludgeoning" for weapons
        self.weapon_difficulty = None  # Difficulty level for weapons
        self.monster_type = None  # D&D style monster type for monsters
        
        self.sprite_file_path = None if self.suit in ("diamonds", "hearts") else self.determine_monster_sprite_path()
        
        # Set name for potions and weapons using Roman numerals
        if self.type == "potion":
            self.name = f"Potion {self._to_roman(self.value)}"
        elif self.type == "weapon":
            # Weapon type will be set in add_weapon_to_card based on the weapon name
            # Initialise with a generic name that will be overridden later
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
        self.icon_size = 50  # Sise of the selection icons
        
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
            print(f"Error loading weapon image: {e}")
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
            print(f"Error loading potion image: {e}")
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
            base_scale = 1.0
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
                surface.blit(scaled_shadow, (self.rect.x + x_offset + shadow_offset_x, self.rect.y + shadow_offset_y))
            
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
                    full_overlay.set_alpha(120)  # More opacity
                    surface.blit(full_overlay, (pos_x, pos_y))
                
                # Check if this is an inventory card (show split discard/equip or discard/use)
                elif hasattr(self, 'in_inventory') and self.in_inventory:
                    # Create top overlay
                    top_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                    top_overlay.fill((200, 60, 60))  # Bright red color for discard
                    
                    # Create bottom overlay (red for discard)
                    bottom_overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                    
                    # Choose top color based on card type
                    if self.type == "weapon":
                        bottom_overlay.fill((60, 180, 60))  # Bright green for equipping
                    elif self.type == "potion":
                        bottom_overlay.fill((220, 160, 50))  # Bright orange for potion use
                    
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
                        top_alpha = 120
                        bottom_alpha = 120
                        if self.hover_selection == "top":
                            # Make the top overlay more opaque
                            top_alpha = 180
                            bottom_alpha = 120
                        elif self.hover_selection == "bottom":
                            # Make the top overlay more opaque
                            top_alpha = 120
                            bottom_alpha = 180
                        
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
                        top_alpha = 120
                        bottom_alpha = 120
                        if self.hover_selection == "top":
                            # Make the top overlay more opaque
                            top_alpha = 180
                            bottom_alpha = 120
                        elif self.hover_selection == "bottom":
                            # Make the bottom overlay more opaque
                            top_alpha = 120
                            bottom_alpha = 180
                        
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
        """Draw hover action text to the right of the card"""
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
        
        # Load fonts
        header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 32)  # Larger font for card name
        body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)    # Medium font for details
        
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
            
            # Weapon type text
            type_text = f"Weapon - {self.weapon_difficulty.upper()}"
            
            # Damage text
            damage_text = f"Damage: {self.value}"
            
            # Add action text based on card location and selection
            action_text = ""
            action_color = GOLD_COLOR  # Default color
            
            # Check if this is an inventory card
            if hasattr(self, 'in_inventory') and self.in_inventory:
                # all cards are treated the same
                if self.hover_selection == "top":
                    action_text = "DISCARD"
                    action_color = (255, 120, 120)  # Bright red
                elif self.hover_selection == "bottom":
                    if self.type == "weapon":
                        action_text = "EQUIP"
                        action_color = (120, 255, 120)  # Bright green
                    elif self.type == "potion":
                        action_text = "USE"
                        action_color = (255, 220, 100)  # Bright gold/yellow
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
                    action_text = "DISCARD"
                    action_color = (255, 120, 120)  # Bright red
                elif self.hover_selection == "bottom":
                    action_text = "USE"
                    action_color = (255, 220, 100)  # Bright gold/yellow
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
        
        else:
            # Default case for unknown card types
            info_lines = [
                {"text": f"Card {self.suit.capitalize()} {self.value}", "font": header_font, "color": WHITE},
                {"text": f"Type: {self.type.capitalize()}", "font": body_font, "color": GOLD_COLOR}
            ]
        
        # Set minimum info box width - will be adjusted based on text content
        min_info_width = 300
        
        # Calculate necessary width based on content
        max_text_width = min_info_width - 20  # Accounting for padding (10px on each side)
        
        # Pre-render text to determine width needs
        rendered_texts = []
        for line in info_lines:
            text_surface = line["font"].render(line["text"], True, line["color"])
            rendered_texts.append(text_surface)
            # Track the widest text
            max_text_width = max(max_text_width, text_surface.get_width() + 20)  # Add 20px padding
            
        # Determine final panel width (use minimum width or text-based width, whichever is larger)
        info_width = max(min_info_width, max_text_width)
        
        # Calculate total height needed for all lines with spacing
        total_text_height = 0
        line_spacing = 5
        for line in info_lines:
            total_text_height += line["font"].get_height() + line_spacing
        
        # Calculate info panel height
        info_height = 10 + total_text_height + 5  # 10px padding top, 5px padding bottom
        
        # Smart positioning logic
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
        panel_color = (60, 50, 40)  # Default brown color
        
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
        
        # Draw all lines of text using pre-rendered text surfaces
        current_y = info_y + 10  # Start with top padding
        for i, line in enumerate(info_lines):
            # Use the pre-rendered text surface if available
            if i < len(rendered_texts):
                text_surface = rendered_texts[i]
            else:
                # Fallback in case there's a mismatch
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

def crop_center(img_path, output_path, target_width, target_height):
    """
        Crop an image to the specified dimensions, centered on the original image.
    """

    # Open the image
    img = Image.open(img_path)
    width, height = img.size
    
    # Calculate the cropping box (left, upper, right, lower)
    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    # Ensure we don't try to crop outside the image bounds
    if left < 0 or top < 0 or right > width or bottom > height:
        print(f"WARNING: Image {img_path} is smaller than the target dimensions!")
        # Adjust crop dimensions to stay within bounds
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)
    
    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save the cropped image
    cropped_img.save(output_path)
    print(f"Cropped {img_path} to {output_path}")

class Deck:
    """ Represents a deck of cards in the game. """
    
    def __init__(self, floor):
        # Store the floor type for card generation
        self.floor = floor
        self.position = DECK_POSITION
        self.cards = []
        self.card_stack = []
        self.card_spacing = (0, 3)
        self.texture = ResourceLoader.load_image("cards/card_back.png")
        self.texture = pygame.transform.scale(self.texture, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def initialise_deck(self):
        """Initialise the deck for a floor.
        
        This method creates a random deck for each floor, making every run more varied.
        Each floor deck follows these rules:
        - Always 44 cards total
        - Always between 16-24 monster cards (clubs/spades value 2-14)
        - Equal number of weapon (diamonds) and potion (hearts) cards (value 2-10)
        - No more than 4 duplicates of the same card type
        """
        self.cards = []
        
        # Generate a random deck for this floor
        self._generate_random_deck()

        # Shuffle the combined deck
        random.shuffle(self.cards)
        self.initialise_visuals()
    
    def _generate_random_deck(self):
        """Generate a random deck following specific requirements:
        - 44 cards total
        - Weapons: 2-10 value range
        - Potions: 2-10 value range
        - Monsters: 2-14 value range
        - Between 16-24 monster cards
        - No more than 4 duplicates of the same card (suit/value)
        - Equal number of weapon and potion cards
        """
        # Step 1: Decide how many monster cards we'll have
        monster_count = random.randint(DECK_MONSTER_COUNT[0], DECK_MONSTER_COUNT[1])
        
        # Step 2: Calculate how many weapon/potion cards
        weapon_potion_count = DECK_TOTAL_COUNT - monster_count
        # Ensure it's an even number since weapons and potions must be equal
        if weapon_potion_count % 2 != 0:
            weapon_potion_count -= 1
            monster_count += 1
            
        weapon_count = potion_count = weapon_potion_count // 2
        
        # Step 3: Start building the deck with tracking to prevent >4 duplicates
        card_counts = {}  # (suit, value) -> count
        
        # Add monsters (clubs and spades)
        self._add_cards_to_deck(["clubs", "spades"], range(DECK_BLACK_VALUE_RANGE[0], DECK_BLACK_VALUE_RANGE[1] + 1), monster_count, card_counts)
        
        # Add weapons (diamonds)
        self._add_cards_to_deck(["diamonds"], range(DECK_DIAMONDS_VALUE_RANGE[0], DECK_DIAMONDS_VALUE_RANGE[1] + 1), weapon_count, card_counts)
        
        # Add potions (hearts)
        self._add_cards_to_deck(["hearts"], range(DECK_HEARTS_VALUE_RANGE[0], DECK_HEARTS_VALUE_RANGE[1] + 1), potion_count, card_counts)

    def _add_cards_to_deck(self, suits, value_range, count, card_counts):
        """Add cards to the deck while respecting the duplicate limit."""
        cards_added = 0
        
        # Try to add the required number of cards
        while cards_added < count:
            # Pick a random suit and value
            suit = random.choice(suits)
            value = random.choice(list(value_range))
            
            # Check if we've already reached the limit for this card
            card_key = (suit, value)
            current_count = card_counts.get(card_key, 0)
            
            if current_count < 4:  # Maximum 4 duplicates
                # Add this card to the deck
                self.cards.append({"suit": suit, "value": value, "floor_type": self.floor})
                
                # Update the count
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
        # Draw the deck
        if self.card_stack:
            for i, pos in enumerate(self.card_stack):
                surface.blit(self.texture, pos)
        else:
            # Draw an empty deck placeholder
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
            # Draw an empty discard pile placeholder
            pygame.draw.rect(surface, GRAY, self.rect, 2)

def extract_weapons():
    # Create output directory
    output_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/individual"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define colour parameters
    dark_colour = (171, 82, 54)
    light_colour = (214, 123, 86)
    
    # Function to process a weapon
    def process_weapon(source_img, x, y, width, height, index):
        # Crop the weapon from source
        weapon = source_img.crop((x, y, x + width, y + height))
        
        # Create new image with transparent background
        new_weapon = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Get pixel data from weapon
        for py in range(height):
            for px in range(width):
                # Get original pixel
                pixel = weapon.getpixel((px, py))
                
                # Skip processing background pixels (brownish colour)
                # Weapons1.png background
                if (120 < pixel[0] < 160 and 
                    100 < pixel[1] < 140 and 
                    70 < pixel[2] < 110):
                    continue
                
                # Weapons2.jpg background (slightly different due to jpg compression)
                if (130 < pixel[0] < 170 and 
                    110 < pixel[1] < 150 and 
                    80 < pixel[2] < 120):
                    continue
                
                # Skip fully transparent pixels if they exist
                if len(pixel) == 4 and pixel[3] == 0:
                    continue
                
                # Determine if pixel is light or dark
                brightness = sum(pixel[:3]) / 3
                
                if brightness > 180:  # Lighter parts (gold/yellow)
                    new_colour = light_colour
                else:  # Darker parts (brown/black)
                    new_colour = dark_colour
                
                # Set alpha to match original or full opacity
                alpha = pixel[3] if len(pixel) == 4 else 255
                
                # Set the pixel in the new image
                new_weapon.putpixel((px, py), (*new_colour, alpha))
        
        # Save the weapon
        output_path = os.path.join(output_dir, f"weapon{index}.png")
        new_weapon.save(output_path)
        print(f"Saved: {output_path}")
    
    # Process weapons1.png (3x3 grid of 32x32 weapons)
    weapons1_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons1.png"
    weapons1 = Image.open(weapons1_path).convert("RGBA")
    
    # Process each weapon in the grid
    for row in range(3):
        for col in range(3):
            index = row * 3 + col + 1
            process_weapon(weapons1, col * 32, row * 32, 32, 32, index)
    
    # Process weapons2.jpg - manual approach
    weapons2_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons2.jpg"
    weapons2 = Image.open(weapons2_path).convert("RGBA")
    
    # Define weapon positions and sizes in weapons2.jpg
    # Format: (x, y, width, height)
    weapon_positions = [
        (12, 11, 32, 32),    # Weapon 10
        (60, 10, 32, 32),    # Weapon 11
        (114, 10, 32, 32),   # Weapon 12
        (12, 58, 32, 32),    # Weapon 13
        (60, 58, 32, 32),    # Weapon 14
        (114, 58, 32, 32),   # Weapon 15
        (12, 106, 32, 32),   # Weapon 16
        (60, 106, 32, 32),   # Weapon 17
        (114, 106, 32, 32)   # Weapon 18
    ]
    
    # Process each weapon
    for i, (x, y, w, h) in enumerate(weapon_positions):
        index = i + 10
        process_weapon(weapons2, x, y, w, h, index)
    
    print("All weapons processed successfully!")

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
        # Start at room 1
        self.current_room = 1
        return self.get_current_floor()
    
    def get_current_floor(self):
        """Get the current floor type."""
        if not self.floors or self.current_floor_index >= len(self.floors):
            # If floors aren't initialised yet, do it now
            if not self.floors:
                self.initialise_run()
                
            # Check again after initialization
            if not self.floors or self.current_floor_index >= len(self.floors):
                return "dungeon"  # Return a default floor value if still no floors
                
        return self.floors[self.current_floor_index]
    
    def advance_room(self):
        """Move to the next room in the current floor."""
        old_room = self.current_room
        self.current_room += 1
        print(f"FloorManager.advance_room: incremented room number from {old_room} to {self.current_room}")
        
        # Check if we've reached the end of the floor
        if self.current_room > FLOOR_TOTAL:
            return self.advance_floor()
                
        return {
            "floor": self.get_current_floor(),
            "room": self.current_room
        }
    
    def advance_floor(self):
        """Move to the next floor."""
        self.current_floor_index += 1
        # Reset room counter to 1 (not 0) when moving to a new floor
        self.current_room = 1
        
        # Check if run is complete
        if self.current_floor_index >= len(self.floors):
            return {"run_complete": True}
        
        # Reset completion tracking in the playing state if it exists
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
        
        # UI elements
        self.panels = {}
        self.buttons = {}
        self.continue_button = None
    
    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()
        
        # Use the floor image for the current floor type
        floor_image = f"floors/{current_floor_type}_floor.png"
            
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        # Create UI elements
        self.create_ui()
    
    def create_ui(self):
        """Create the UI elements for the floor start state."""
        # Main panel
        self.panels["main"] = Panel(
            (600, 300),
            (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150),
            colour=DARK_GRAY
        )
        
        # Continue button
        continue_rect = pygame.Rect(0, 0, 200, 50)
        continue_rect.centerx = self.panels["main"].rect.centerx
        continue_rect.bottom = self.panels["main"].rect.bottom - 30
        self.continue_button = Button(continue_rect, "Enter Floor", self.body_font)
    
    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            # Check button hover states
            self.continue_button.check_hover(event.pos)
        
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if continue button was clicked
            if self.continue_button.is_clicked(event.pos):
                self.game_manager.change_state("playing")
                return
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Draw panels
        for panel in self.panels.values():
            panel.draw(surface)
        
        # Draw floor title
        floor_type = self.game_manager.floor_manager.get_current_floor()
        floor_index = max(1, self.game_manager.floor_manager.current_floor_index + 1)  # Make sure index is at least 1
        title_text = self.header_font.render(f"Floor {floor_index}: {floor_type.title()}", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panels["main"].rect.centerx, top=self.panels["main"].rect.top + 30)
        surface.blit(title_text, title_rect)
        
        # Add a welcome message
        welcome_text = self.body_font.render(f"Welcome to the {floor_type.title()}", True, WHITE)
        welcome_rect = welcome_text.get_rect(centerx=self.panels["main"].rect.centerx, top=title_rect.bottom + 30)
        surface.blit(welcome_text, welcome_rect)
        
        # Add instructions
        instruct_text = self.normal_font.render("Prepare yourself for the challenges ahead!", True, WHITE)
        instruct_rect = instruct_text.get_rect(centerx=self.panels["main"].rect.centerx, top=welcome_rect.bottom + 20)
        surface.blit(instruct_text, instruct_rect)
        
        # Draw continue button
        self.continue_button.draw(surface)

class GameManager:
    """Manager for game states with roguelike elements."""
    
    def __init__(self):
        # Initialise roguelike managers
        self.floor_manager = FloorManager(self)
                
        # Initialise game states
        self.states = {
            "title": TitleState(self),  # New title state
            "menu": MenuState(self),    # Keep menu state for compatibility
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self),
        }
                
        self.current_state = None
        self.game_data = {
            "life_points": STARTING_ATTRIBUTES["life_points"],
            "max_life": STARTING_ATTRIBUTES["max_life"],
            "victory": False,
            "run_complete": False
        }
        
        # Storage for equipment, defeated monsters, and remaining card when transitioning between states
        self.equipped_weapon = {}
        self.defeated_monsters = []
        self.last_card_data = None
        
        # Start with the new title state
        self.change_state("title")
    
    def change_state(self, state_name):
        current_state_name = "None" if not self.current_state else self.current_state.__class__.__name__
        
        # If we're already in the requested state, don't change states
        if self.current_state and self.current_state == self.states[state_name]:
            print(f"Already in state {state_name}, not changing")
            return
            
        print(f"Changing state from {current_state_name} to {state_name}")
        
        if self.current_state:
            self.current_state.exit()
                    
        # Initialise floors when going to title screen if they're not set
        if state_name == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()
            
        # Set the current state
        self.current_state = self.states[state_name]
        
        print(f"Calling enter() on {state_name}")
        self.current_state.enter()
        print(f"enter() completed for {state_name}")
    
    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)
    
    def update(self, delta_time):
        if self.current_state:
            self.current_state.update(delta_time)
    
    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
    
    def start_new_run(self):
        """Initialise a new roguelike run."""
        # Reset player attributes
        self.game_data["life_points"] = STARTING_ATTRIBUTES["life_points"]
        self.game_data["max_life"] = STARTING_ATTRIBUTES["max_life"]
        self.game_data["victory"] = False
        self.game_data["run_complete"] = False
        
        # Initialise the floor sequence
        self.floor_manager.initialise_run()
        
        # Set a flag to indicate this is a new run
        self.is_new_run = True
        
        # Go directly to the playing state
        self.change_state("playing")
    
    def advance_to_next_room(self):
        """Advance to the next room in the current floor."""
        print(f"GameManager.advance_to_next_room called - current room before: {self.floor_manager.current_room}")
        # Get next room info
        room_info = self.floor_manager.advance_room()
        print(f"After advance_room - room now: {self.floor_manager.current_room}")
        
        # Check if the run is complete
        if "run_complete" in room_info and room_info["run_complete"]:
            # Go to game over
            self.game_data["victory"] = True
            self.game_data["run_complete"] = True
            return
        
        # Check if this is a new floor
        if "is_floor_start" in room_info and room_info["is_floor_start"]:
            return

    def check_game_over(self):
        """Check if the game is over."""
        if self.game_data["life_points"] <= 0:
            self.game_data["victory"] = False
            
            
            self.change_state("game_over")
            return True
        return False
    
    # Helper methods
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
        
        # Initialise particles based on victory/defeat
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
                self.game_manager.states["playing"] = PlayingState(self.game_manager)
                
                # Start a new game
                self.game_manager.start_new_run()
            
            # Check for title button click
            elif self.title_button and self.title_button.is_clicked(event.pos):
                # Reset game data
                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False
                
                # Completely reset the playing state
                self.game_manager.states["playing"] = PlayingState(self.game_manager)
                
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
        
        # Draw buttons
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
        # Save victory state
        self.playing_state.game_manager.game_data["victory"] = victory
        
        # Change to game over state
        self.playing_state.game_manager.change_state("game_over")
    
    def show_message(self, message, duration=1.2):
        """Display a small, non-blocking notification above the room cards."""
        # Use smaller font for less intrusive messages
        message_text = self.playing_state.body_font.render(message, True, self.playing_state.WHITE)
        
        # Position above the room cards (centered horizontally, fixed position vertically)
        room_top = self.playing_state.SCREEN_HEIGHT//2 - 120  # Approximate room cards position
        message_rect = message_text.get_rect(center=(self.playing_state.SCREEN_WIDTH//2, room_top - 25))
        
        # Create a small, semi-transparent background for the text
        padding_x, padding_y = 15, 8
        bg_rect = pygame.Rect(
            message_rect.left - padding_x,
            message_rect.top - padding_y,
            message_rect.width + padding_x * 2,
            message_rect.height + padding_y * 2
        )
        
        # Store the message with fade animation props
        self.playing_state.message = {
            "text": message_text,
            "rect": message_rect,
            "bg_rect": bg_rect,
            "alpha": 0,  # Start fully transparent
            "fade_in": True,  # Initially fading in
            "time_remaining": duration,
            "fade_speed": 510  # How fast to fade in/out (total alpha over X frames)
        }
        
        # No need to block input - these notifications are non-blocking


class HUD:
    """Heads-up display for showing active effects and status."""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        self.small_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)
        
        # Active effects
        self.active_effects = []
        
        # Effect icon positions
        self.effect_icon_size = EFFECT_ICON_SIZE
        self.effect_spacing = EFFECT_ICON_SPACING
        self.effect_start_pos = EFFECT_START_POSITION
        
        # Resource tracking for animations
        self.last_particle_time = 0
        
        # Panel instances for health indicators
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
            'duration': duration,  # None for permanent effects
            'value': value,
            'start_time': pygame.time.get_ticks()
        })
    
    def update(self):
        """Update active effects and resource animations."""
        current_time = pygame.time.get_ticks()
        
        # Filter out expired effects
        self.active_effects = [effect for effect in self.active_effects if (
            effect['duration'] is None) or  # Permanent effects
            ((current_time - effect['start_time']) < effect['duration'])  # Temporary effects
        ]
    
    def draw(self, surface):
        """Draw the HUD elements."""
        # Draw active effects
        self.draw_active_effects(surface)
        
        # Draw health indicator
        self.draw_health_indicator(surface)
    
    def draw_active_effects(self, surface):
        """Draw icons for active effects with dungeon styling."""
        try:
            using_panels = True
        except ImportError:
            using_panels = False
            
        for i, effect in enumerate(self.active_effects):
            # Calculate position
            x = self.effect_start_pos[0] + i * (self.effect_icon_size + self.effect_spacing)
            y = self.effect_start_pos[1]
            
            # Effect rect
            effect_rect = pygame.Rect(x, y, self.effect_icon_size, self.effect_icon_size)
            
            # Choose colour based on effect type
            effect_colour = EFFECT_DEFAULT_COLOR  # Default
            if effect['type'] == 'healing':
                effect_colour = EFFECT_HEALING_COLOR
                panel_colour = EFFECT_HEALING_PANEL
                border_colour = EFFECT_HEALING_BORDER
                icon_symbol = "+"  # Plus/healing symbol
            elif effect['type'] == 'damage':
                effect_colour = EFFECT_DAMAGE_COLOR
                panel_colour = EFFECT_DAMAGE_PANEL
                border_colour = EFFECT_DAMAGE_BORDER
                icon_symbol = "⚔"  # Sword symbol
            else:
                effect_colour = EFFECT_DEFAULT_COLOR
                panel_colour = EFFECT_DEFAULT_PANEL
                border_colour = EFFECT_DEFAULT_BORDER
                icon_symbol = "◆"  # Default diamond symbol
            
            # Draw effect icon with panel if available
            if using_panels:
                # Create a dungeon-styled panel for this effect
                effect_panel = Panel(
                    (self.effect_icon_size, self.effect_icon_size),
                    (x, y),
                    colour=panel_colour,
                    alpha=PANEL_ALPHA,
                    border_radius=PANEL_BORDER_RADIUS - 2,  # Slightly smaller for effect panels
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=border_colour
                )
                effect_panel.draw(surface)
                
                # Calculate time-based pulse effect for active effects
                current_time = pygame.time.get_ticks()
                if effect['duration'] is not None:
                    # Calculate how much time has passed (0.0 to 1.0)
                    elapsed = (current_time - effect['start_time']) / effect['duration']
                    # Create a pulsating effect that gets faster as time runs out
                    base, amplitude, frequency = EFFECT_PULSE_TEMPORARY
                    pulse_factor = base + amplitude * math.sin(elapsed * 10 + current_time / frequency)
                else:
                    # For permanent effects, use a slower, subtler pulse
                    base, amplitude, frequency = EFFECT_PULSE_PERMANENT
                    pulse_factor = base + amplitude * math.sin(current_time / frequency)
                
                # Draw a glowing circle as the effect icon
                glow_radius = int(self.effect_icon_size * 0.3 * pulse_factor)
                center_x = x + self.effect_icon_size // 2
                center_y = y + self.effect_icon_size // 2
                
                # Draw outer glow
                for r in range(glow_radius, 0, -1):
                    alpha = max(0, 150 - (glow_radius - r) * 20)
                    pygame.draw.circle(surface, (*effect_colour, alpha), 
                                     (center_x, center_y), r)
                                     
                # Draw icon symbol in the center
                symbol_font = pygame.font.SysFont(None, int(self.effect_icon_size * 0.6))
                symbol_text = symbol_font.render(icon_symbol, True, WHITE)
                symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
                surface.blit(symbol_text, symbol_rect)
            else:
                # Fallback to simple rectangles if Panel isn't available
                pygame.draw.rect(surface, effect_colour, effect_rect)
                pygame.draw.rect(surface, BLACK, effect_rect, 2)
            
            # Draw value if available
            if effect['value'] is not None:
                value_text = self.normal_font.render(str(effect['value']), True, WHITE)
                value_rect = value_text.get_rect(center=effect_rect.center)
                
                # For panel-style, position below the effect
                if using_panels:
                    value_rect.midtop = (x + self.effect_icon_size // 2, y + self.effect_icon_size + 2)
                
                surface.blit(value_text, value_rect)
            
            # Draw duration if available
            if effect['duration'] is not None:
                remaining = max(0, effect['duration'] - (pygame.time.get_ticks() - effect['start_time']))
                remaining_text = self.small_font.render(f"{remaining//1000}s", True, WHITE)
                
                # Position differently based on whether we have a value displayed
                if effect['value'] is not None and using_panels:
                    # Position below the value
                    remaining_rect = remaining_text.get_rect(
                        midtop=(x + self.effect_icon_size // 2, 
                               y + self.effect_icon_size + value_text.get_height() + 4)
                    )
                else:
                    # Position at the bottom of the effect
                    remaining_rect = remaining_text.get_rect(
                        midbottom=(x + self.effect_icon_size // 2, 
                                  y + self.effect_icon_size + (10 if using_panels else 0))
                    )
                
                # Add urgency visual cues for effects about to expire
                if remaining < EFFECT_EXPIRE_THRESHOLD:  # Effect is about to expire
                    # Use red text for urgency
                    remaining_text = self.small_font.render(f"{remaining//1000}s", True, (255, 100, 100))
                    
                    # Add pulsating effect as time runs out
                    pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 100)
                    scaled_size = int(remaining_text.get_width() * pulse), int(remaining_text.get_height() * pulse)
                    if scaled_size[0] > 0 and scaled_size[1] > 0:  # Ensure valid size
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
        
        # Health bar parameters from constants
        bar_width = HEALTH_BAR_WIDTH
        bar_height = HEALTH_BAR_HEIGHT
        x, y = HEALTH_BAR_POSITION
        
        # Create panel if it doesn't exist
        if not self.health_panel:
            try:
                # Use a blood/potion themed colour scheme
                self.health_panel = Panel(
                    (bar_width, bar_height),
                    (x, y),
                    colour=PANEL_HEALTH,
                    alpha=PANEL_ALPHA + 10,  # Slightly more opaque
                    border_radius=PANEL_BORDER_RADIUS,
                    dungeon_style=True,
                    border_width=PANEL_BORDER_WIDTH,
                    border_colour=PANEL_HEALTH_BORDER
                )
            except ImportError:
                # Fallback if Panel isn't available
                self.health_panel = None
        
        # Calculate health percentage
        health_percent = playing_state.life_points / playing_state.max_life
        health_width = int((bar_width - 10) * health_percent)  # Leave margin for styling
        
        # Choose colour based on health percentage
        if health_percent > 0.7:
            health_colour = HEALTH_COLOR_GOOD
            glow_colour = HEALTH_GLOW_GOOD
        elif health_percent > 0.3:
            health_colour = HEALTH_COLOR_WARNING
            glow_colour = HEALTH_GLOW_WARNING
        else:
            health_colour = HEALTH_COLOR_DANGER
            glow_colour = HEALTH_GLOW_DANGER
            
        # Draw the panel for health bar container
        if self.health_panel:
            self.health_panel.draw(surface)
            
            # Draw health bar with inner glow and margin
            health_rect = pygame.Rect(x + 5, y + 5, health_width, bar_height - 10)
            
            # Draw glow effect for health bar
            glow_surface = pygame.Surface((health_width + 10, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_colour, 
                          (5, 0, health_width, bar_height - 10), border_radius=4)
            surface.blit(glow_surface, (x, y))
            
            # Draw the actual health bar
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=4)
            
            # Add highlight to top of health bar for 3D effect
            if health_width > 4:
                highlight_colour = self._lighten_colour(health_colour, 0.3)
                pygame.draw.rect(surface, highlight_colour, 
                              (x + 5, y + 5, health_width, 2), border_radius=2)
        else:
            # Fallback to simpler rendering
            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, border_radius=5)
            
            health_rect = pygame.Rect(x, y, health_width, bar_height)
            pygame.draw.rect(surface, health_colour, health_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bg_rect, 2, border_radius=5)
        
        # Draw health value with appropriate colour based on health status
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
        # Define inventory panel position - must match playing_state.py
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Use standard card size (no scaling) for inventory cards
        card_scale = 1.0
        
        # Calculate the scaled card dimensions
        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)
        
        # Get number of cards in inventory
        num_cards = len(self.playing_state.inventory)
        
        # Position each card
        for i, card in enumerate(self.playing_state.inventory):
            # Apply scale to card
            card.update_scale(card_scale)
            
            # Make sure card knows it's in inventory to reduce bobbing
            card.in_inventory = True
            
            # Center X position (horizontally centered in panel)
            inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)
            
            # Calculate Y position based on number of cards
            if num_cards == 1:
                # Single card - center vertically in panel
                inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
            elif num_cards == 2:
                # Two cards - one above center, one below center
                if i == 0:
                    # First card positioned in top half
                    inventory_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)
                else:
                    # Second card positioned in bottom half
                    inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)
            
            # Update the card's position
            card.update_position((inventory_x, inventory_y))
    
    def get_inventory_card_at_position(self, position):
        """Check if the position overlaps with any inventory card."""
        for card in self.playing_state.inventory:
            if card.rect.collidepoint(position):
                return card
        return None

class MenuState(GameState):
    """The main menu state of the game."""
    
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None
        self.start_button_rect = None
    
    def enter(self):
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 64)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load floor
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.start_button_rect and self.start_button_rect.collidepoint(event.pos):
                # Initialise a new roguelike run
                self.game_manager.start_new_run()
                
                # This will now go to floor_start state instead of directly to rules
                # The rules screen will be shown first time only
                if not hasattr(self.game_manager, 'has_shown_rules') or not self.game_manager.has_shown_rules:
                    self.game_manager.has_shown_rules = True
                    self.game_manager.change_state("rules")
                else:
                    # Skip rules screen on subsequent runs
                    self.game_manager.change_state("floor_start")
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Create a semi-transparent panel
        panel = Panel((MENU_WIDTH, MENU_HEIGHT), MENU_POSITION, colour=DARK_GRAY)
        panel.draw(surface)
        
        # Draw title
        title_text = self.title_font.render("SCOUNDREL", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, panel.rect.top + 50))
        surface.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.header_font.render("The 52-Card Dungeon Crawler", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, title_rect.bottom + 30))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw start button
        self.start_button_rect = pygame.Rect(0, 0, 225, 50)
        self.start_button_rect.center = (SCREEN_WIDTH//2, panel.rect.bottom + 150)
        pygame.draw.rect(surface, LIGHT_GRAY, self.start_button_rect)
        pygame.draw.rect(surface, BLACK, self.start_button_rect, 2)
        
        button_text = self.body_font.render("START GAME", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        surface.blit(button_text, button_text_rect)

class Panel:
    def __init__(self, width_height, top_left, colour=DARK_GRAY, alpha=None, border_radius=None, 
                 dungeon_style=True, border_width=None, border_colour=None):
        # Use default values from constants if not provided
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
        
        # Create noise texture once for this panel instance
        self.noise_texture = None
        if self.dungeon_style:
            self._create_noise_texture()
            
        # Create the panel surface
        self._create_surface()
    
    def _create_noise_texture(self):
        """Create a subtle noise texture for the panel background"""
        width, height = self.rect.size
        self.noise_texture = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create a more subtle noise pattern with medium grains
        grain_size = 3  # Medium grain size (was 4)
        
        # Create a more subtle noise pattern with less variance
        for x in range(0, width, grain_size):
            for y in range(0, height, grain_size):
                # Lighter random darkening for a more subtle stone-like texture
                darkness = random.randint(0, 25)  # Reduced darkness (was 0-40)
                
                # Use medium rectangles for a balanced look
                pygame.draw.rect(self.noise_texture, (0, 0, 0, darkness), 
                                (x, y, grain_size, grain_size))
                
                # Rarely add lighter spots for subtle texture variation
                if random.random() < 0.05:  # 5% chance (was 10%)
                    lightness = random.randint(5, 15)  # Less pronounced (was 10-30)
                    pygame.draw.rect(self.noise_texture, (255, 255, 255, lightness), 
                                   (x, y, grain_size, grain_size))
    
    def _draw_decorative_border(self, surface, rect, border_radius):
        """Draw a decorative border with corner details for a dungeon feel"""
        # Draw main border
        darker_border = self._darken_colour(self.border_colour, 0.5)
        lighter_border = self._lighten_colour(self.border_colour, 0.3)
        
        # Draw border with slight 3D effect (dark outer, light inner)
        pygame.draw.rect(surface, darker_border, rect, 
                         width=self.border_width+1, border_radius=border_radius)
        
        # Draw inner highlight for 3D effect (thinner)
        inner_rect = rect.inflate(-4, -4)
        pygame.draw.rect(surface, lighter_border, inner_rect, 
                         width=1, border_radius=max(0, border_radius-2))
        
        # Add corner accents for dungeon style
        corner_size = min(10, border_radius)
        if corner_size > 3:
            # Top-left corner
            pygame.draw.line(surface, darker_border, 
                          (rect.left + border_radius//2, rect.top + 3),
                          (rect.left + 3, rect.top + border_radius//2), 2)
            # Top-right corner
            pygame.draw.line(surface, darker_border, 
                          (rect.right - border_radius//2, rect.top + 3),
                          (rect.right - 3, rect.top + border_radius//2), 2)
            # Bottom-left corner
            pygame.draw.line(surface, darker_border, 
                          (rect.left + border_radius//2, rect.bottom - 3),
                          (rect.left + 3, rect.bottom - border_radius//2), 2)
            # Bottom-right corner
            pygame.draw.line(surface, darker_border, 
                          (rect.right - border_radius//2, rect.bottom - 3),
                          (rect.right - 3, rect.bottom - border_radius//2), 2)
    
    def _create_surface(self):
        """Create the panel surface with desired style"""
        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw background rect
        rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(self.surface, self.colour, rect, border_radius=self.border_radius)
        
        # Apply texture if in dungeon style
        if self.dungeon_style and self.noise_texture:
            self.surface.blit(self.noise_texture, (0, 0))
        
        # Add decorative border if in dungeon style
        if self.dungeon_style:
            self._draw_decorative_border(self.surface, rect, self.border_radius)
            
        # Apply alpha
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
        # Update noise texture for new size
        if self.dungeon_style:
            self._create_noise_texture()
        # Recreate the surface
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
        
        # Calculate new health value with limits
        if amount > 0:  # Healing
            # Can't heal beyond max_life
            self.playing_state.life_points = min(self.playing_state.life_points + amount, self.playing_state.max_life)
            actual_change = self.playing_state.life_points - old_health
            # Only animate if there was an actual change
            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(False, actual_change)  # False = healing
        else:  # Damage
            # Can't go below 0
            self.playing_state.life_points = max(0, self.playing_state.life_points + amount)  # amount is negative for damage
            actual_change = old_health - self.playing_state.life_points
            # Only animate if there was an actual change
            if actual_change > 0:
                self.playing_state.animation_controller.animate_health_change(True, actual_change)  # True = damage

class PlayingState(GameState):
    """The main gameplay state of the game with roguelike elements."""
    
    def __init__(self, game_manager):
        """Initialise the playing state."""
        super().__init__(game_manager)
        
        # Initialise managers and controllers
        self._initialise_managers()
        
        # Initialise game state variables
        self._initialise_state_variables()
        
        # Initialise player state
        self._initialise_player_state()
        
        # Initialise game components
        self._initialise_game_components()
        
        # Initialise UI elements
        self._initialise_ui_elements()
    
    def _initialise_managers(self):
        """Initialise all manager and controller classes."""
        # Initialise animation manager
        self.animation_manager = AnimationManager()
        
        # Initialise resource loader
        self.resource_loader = ResourceLoader
        
        # Initialise our modular managers
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
        # Make constants accessible to the class
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_GRAY = LIGHT_GRAY
        
        # Animation and state flags
        self.is_running = False
        self.ran_last_turn = False
        self.show_debug = False
        self.z_index_counter = 0
        
        # Room state tracking
        self.completed_rooms = 0
        self.total_rooms_on_floor = 0
        self.floor_completed = False
        self.room_completion_in_progress = False 
        self.room_started_in_enter = False  # Flag to track if a room was started in enter()
        
        # Message display
        self.message = None
    
    def _initialise_player_state(self):
        """Initialise player stats and inventory."""
        # Player stats
        self.life_points = 20
        self.max_life = 20
        self.equipped_weapon = {}
        self.defeated_monsters = []
        
        # Player inventory
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
        
        # Status UI & HUD
        self.status_ui = StatusUI(self.game_manager)
        self.hud = HUD(self.game_manager)

    def enter(self):
        """Initialise the playing state when entering."""
        print(f"PlayingState.enter() called - current room: {self.game_manager.floor_manager.current_room}")
        
        # Load resources
        self._load_resources()
        
        # Initialise game components 
        self._setup_game_components()
        
        # Handle player state setup
        self._setup_player_state()
        
        # Start initial room
        self._start_initial_room()
        
        # Reset state tracking
        self._reset_state_tracking()
    
    def _load_resources(self):
        """Load fonts, background and floor image."""
        # Load fonts
        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 60)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.caption_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)

        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Get current floor info
        floor_manager = self.game_manager.floor_manager
        current_floor_type = floor_manager.get_current_floor()
        
        floor_image = f"floors/{current_floor_type}_floor.png"
            
        # Try to load the specific floor image, fall back to original if not found
        try:
            self.floor = ResourceLoader.load_image(floor_image)
        except:
            # Fallback to the original floor image
            self.floor = ResourceLoader.load_image("floor.png")
            
        # Scale the floor to the correct dimensions
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def _setup_game_components(self):
        """Initialise deck, discard pile, and room."""
        # Initialise floor information
        floor_manager = self.game_manager.floor_manager
        self.current_floor = floor_manager.get_current_floor()
        
        # Make sure we have a valid floor
        if not self.current_floor:
            print(f"Warning: Floor is not initialised. Using fallback.")
            self.current_floor = "dungeon"  # Fallback to dungeon if floor is None
        
        # Create a new deck and discard pile
        self.deck = Deck(self.current_floor)
        self.discard_pile = DiscardPile()
        self.room = Room(self.animation_manager)
        
        # Initialise the visual representation for deck and discard pile
        if hasattr(self.deck, "initialise_visuals"):
            self.deck.initialise_visuals()
            
        if hasattr(self.discard_pile, "initialise_visuals"):
            self.discard_pile.initialise_visuals()
            
        # Position inventory cards
        if hasattr(self, "inventory_manager") and hasattr(self.inventory_manager, "position_inventory_cards"):
            self.inventory_manager.position_inventory_cards()

        # Create UI buttons
        self.ui_factory.create_run_button()
    
    def _setup_player_state(self):
        """Set up player stats and equipped weapon."""
        # Reset player stats
        self.life_points = self.game_manager.game_data["life_points"]
        self.max_life = self.game_manager.game_data["max_life"]
    
    def _start_initial_room(self):
        """Start the initial room either with a card from fresh."""        
        # Initialise deck with player cards shuffled in
        self.deck.initialise_deck()
        
        if self.discard_pile:
            self.discard_pile.cards = []
            if hasattr(self.discard_pile, 'card_stack'):
                self.discard_pile.card_stack = []
            
        self.room_manager.start_new_room()
        # Set flag that we've started a room in enter
        self.room_started_in_enter = True
        
        # Update status UI fonts
        self.status_ui.update_fonts(self.header_font, self.normal_font)

        # Update HUD fonts
        self.hud.update_fonts(self.normal_font, self.normal_font)
    
    def _reset_state_tracking(self):
        """Reset game state tracking variables."""
        # Reset floor completion tracking
        self.floor_completed = False

        # Reset completed_rooms counter if starting a new floor
        if self.game_manager.floor_manager.current_room == 1:
            self.completed_rooms = 0

    def exit(self):
        """Save state when exiting playing state."""
        # Save player stats to game_data
        self.game_manager.game_data["life_points"] = self.life_points
        self.game_manager.game_data["max_life"] = self.max_life

    def handle_event(self, event):
        """Handle player input events."""
        if self.animation_manager.is_animating():
            return  # Don't handle events while animating
        
        if event.type == MOUSEMOTION:
            self._handle_hover(event)
                    
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self._handle_click(event)
    
    def _handle_hover(self, event):
        """Handle mouse hover events over cards and buttons."""
        # Check hover for cards in the room
        inventory_is_full = len(self.inventory) >= self.MAX_INVENTORY_SIZE
        
        # Prepare all cards for hover detection
        all_hoverable_cards = []
        
        # Setup room cards
        for card in self.room.cards:
            # For monster cards, set the weapon_available flag based on equipped weapon
            if hasattr(card, 'can_show_attack_options') and card.can_show_attack_options:
                card.weapon_available = bool(self.equipped_weapon)
                
                if self.equipped_weapon and self.defeated_monsters:
                    card.weapon_attack_not_viable = card.value >= self.defeated_monsters[-1].value
                else:
                    card.weapon_attack_not_viable = False
            
            # For cards that can be added to inventory, check if inventory is full
            if hasattr(card, 'can_add_to_inventory') and card.can_add_to_inventory:
                card.inventory_available = not inventory_is_full
            
            # Add card to hoverable cards if it collides with mouse
            # Reset hover status first
            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)
        
        # Setup inventory cards
        for card in self.inventory:
            # Reset hover status first
            card.is_hovered = False
            if card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(card)
            
        # Setup equipped weapon
        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]
            # Reset hover status first
            weapon_card.is_hovered = False
            if weapon_card.rect.collidepoint(event.pos):
                all_hoverable_cards.append(weapon_card)
        
        # Setup defeated monsters
        for monster in self.defeated_monsters:
            # Reset hover status first
            monster.is_hovered = False
            if monster.rect.collidepoint(event.pos):
                all_hoverable_cards.append(monster)
        
        # Find the closest card to mouse cursor
        if all_hoverable_cards:
            closest_card = self._find_closest_card(event.pos, all_hoverable_cards)
            # Only set the closest card as hovered
            if closest_card:
                closest_card.check_hover(event.pos)
        
        # Check hover for buttons
        self.run_button.check_hover(event.pos)
    
    def _find_closest_card(self, pos, cards):
        """Find the card closest to the given position."""
        if not cards:
            return None
            
        closest_card = None
        closest_distance = float('inf')
        
        for card in cards:
            # Calculate distance from mouse to card center
            card_center_x = card.rect.centerx
            card_center_y = card.rect.centery
            
            # Calculate total float offset for more accurate hover detection
            total_float_offset = 0
            if hasattr(card, 'idle_float_offset') and hasattr(card, 'hover_float_offset'):
                total_float_offset = card.idle_float_offset + card.hover_float_offset
            
            # Adjust center Y with float offset
            card_center_y -= total_float_offset
            
            # Calculate squared distance (faster than sqrt)
            dist_sq = (pos[0] - card_center_x) ** 2 + (pos[1] - card_center_y) ** 2
            
            if dist_sq < closest_distance:
                closest_distance = dist_sq
                closest_card = card
        
        return closest_card
    
    def _handle_click(self, event):
        """Handle mouse click events."""
        if self.life_points <= 0:
            return  # Don't handle clicks if player is dead
            
        # Check if run button was clicked
        if self.run_button.is_clicked(event.pos) and not self.ran_last_turn and len(self.room.cards) == 4:
            self.room_manager.run_from_room()
            return
                    
        # Check if a card was clicked
        clicked_card = None
        
        # First check room cards
        card = self.room.get_card_at_position(event.pos)
        if card:
            self.card_action_manager.resolve_card(card, event_pos=event.pos)
            return  # Important: Return to prevent checking inventory cards
        
        # If no room card was clicked, check inventory cards
        clicked_inventory_card = self.inventory_manager.get_inventory_card_at_position(event.pos)
        if clicked_inventory_card:
            self.card_action_manager.use_inventory_card(clicked_inventory_card, event.pos)
            return  # Important: Return to prevent checking equipped weapon
        
        # If no room card or inventory card was clicked, check equipped weapon
        if "node" in self.equipped_weapon and self.equipped_weapon["node"].rect.collidepoint(event.pos):
            self.card_action_manager.discard_equipped_weapon()

    def update(self, delta_time):
        """Update game state for this frame."""
        # Update animations
        previous_animating = self.animation_manager.is_animating()
        self.animation_manager.update(delta_time)
        current_animating = self.animation_manager.is_animating()
        
        # Check if animations just finished
        animations_just_finished = previous_animating and not current_animating
        
        # Update message and cards
        self._update_message(delta_time)
        self._update_cards(delta_time)
        
        # Only process game state changes if we're not animating or animations just finished
        if not current_animating:
            self._process_game_state(animations_just_finished)
        
        # Check for game over
        self.game_state_controller.check_game_over()
    
    def _update_message(self, delta_time):
        """Update any active message fade animation."""
        if hasattr(self, 'message') and self.message and 'alpha' in self.message:
            # Update fade-in/fade-out animation
            if self.message['fade_in']:
                # Fading in
                self.message['alpha'] = min(255, self.message['alpha'] + self.message['fade_speed'] * delta_time)
                # Check if fade-in is complete
                if self.message['alpha'] >= 255:
                    self.message['fade_in'] = False
            else:
                # Update timer
                self.message['time_remaining'] -= delta_time
                # If timer expired, start fading out
                if self.message['time_remaining'] <= 0:
                    self.message['alpha'] = max(0, self.message['alpha'] - self.message['fade_speed'] * delta_time)
                    # Clear message when fully transparent
                    if self.message['alpha'] <= 0:
                        self.message = None
    
    def _update_cards(self, delta_time):
        """Update all card animations."""
        # Update room cards
        for card in self.room.cards:
            # Update idle hover and hover animations
            card.update(delta_time)
            
            # Update card flip animations
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # Update inventory card animations
        for card in self.inventory:
            card.update(delta_time)
            if card.is_flipping:
                card.update_flip(delta_time)
        
        # Update weapon and defeated monster animations
        if "node" in self.equipped_weapon:
            self.equipped_weapon["node"].update(delta_time)
            
        for monster in self.defeated_monsters:
            monster.update(delta_time)
    
    def _process_game_state(self, animations_just_finished):
        """Process game state changes after animations."""
        # If we were running and animations finished, complete the run
        if self.is_running:
            self.room_manager.on_run_completed()
            return
        
        # Process room state only when no animations are running
        # If we just started a room in enter, room_started_in_enter will be True
        if self.room_started_in_enter:
            print(f"Skipping room completion in update because room_started_in_enter=True")
            self.room_started_in_enter = False
            return
        
        # Handle empty room - check for room completion
        if len(self.room.cards) == 0:
            self._handle_empty_room()
        
        # If we have only one card left and animations just finished, start a new room
        # But only if we didn't just start one in enter()
        elif len(self.room.cards) == 1 and animations_just_finished and len(self.deck.cards) > 0:
            self._handle_single_card_room()
    
    def _handle_empty_room(self):
        """Handle logic for when the room is empty (all cards processed)."""
        # Only trigger room completion once
        if not self.room_completion_in_progress:
            # Set flag to prevent multiple room completions
            self.room_completion_in_progress = True
            
            # Increment room count when completing a room
            self.completed_rooms += 1
        
        # Go directly to the next room if we have cards
        if len(self.deck.cards) > 0:
            print(f"Room completed with empty room, advancing to next room. Cards in deck: {len(self.deck.cards)}")
            # More cards in deck - advance to next room
            self.game_manager.advance_to_next_room()
            
            # Update UI elements that show room number
            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()
            
            # Check if we're still in the playing state
            if self.game_manager.current_state == self:
                # Start a new room
                self.room_manager.start_new_room()
        else:
            # No more cards in the deck - floor completed
            self._handle_floor_completion()
    
    def _handle_single_card_room(self):
        """Handle logic for rooms with a single card remaining."""
        # Only trigger room completion once
        if not self.room_completion_in_progress:
            # Set flag to prevent multiple room completions
            self.room_completion_in_progress = True
            
            # Increment completed rooms because we're moving to the next room with a card
            self.completed_rooms += 1
            
            # Advance to next room in the floor manager
            self.game_manager.advance_to_next_room()
            
            # Update UI elements that show room number
            if hasattr(self, 'status_ui') and hasattr(self.status_ui, 'update_status'):
                self.status_ui.update_status()
                    
        # Start a new room with the remaining card
        self.room_manager.start_new_room(self.room.cards[0])
    
    def _handle_floor_completion(self):
        """Handle logic for when the floor is completed."""
        if not self.floor_completed:
            self.floor_completed = True
            
            # Check if this is the last floor
            if self.game_manager.floor_manager.current_floor_index >= len(self.game_manager.floor_manager.floors) - 1:
                # Last floor completed - victory!                
                self.game_manager.game_data["victory"] = True
                self.game_manager.game_data["run_complete"] = True
                self.game_manager.change_state("game_over")
            else:
                # Not the last floor, show a brief message and advance to next floor
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
                
                # Schedule transition to next floor after a short delay
                self.animation_controller.schedule_delayed_animation(
                    3.0,  # 3 second delay to show the message
                    lambda: self.room_manager.transition_to_next_floor()
                )

    def draw(self, surface):
        """Draw game elements to the screen."""
        # Draw background and floor
        self._draw_background(surface)
        
        # Draw game components
        self._draw_cards_and_piles(surface)
        
        # Draw inventory panel and cards
        self._draw_inventory(surface)
        
        # Draw UI elements
        self._draw_ui_elements(surface)
    
    def _draw_background(self, surface):
        """Draw background and floor."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
    
    def _draw_cards_and_piles(self, surface):
        """Draw deck, discard pile, equipped weapon, and defeated monsters."""
        # Draw deck first
        self.deck.draw(surface)
        
        # Draw discard pile
        self.discard_pile.draw(surface)
        
        # Draw equipped weapon and defeated monsters
        if "node" in self.equipped_weapon:
            weapon_card = self.equipped_weapon["node"]
            
            # Check for hover over the weapon card
            weapon_is_hovered = weapon_card.is_hovered and weapon_card.face_up
            
            # Draw the weapon card
            weapon_card.draw(surface)
            
            # Process all defeated monsters
            hovered_monsters = []
            non_hovered_monsters = []
            
            # Separate hovered and non-hovered monsters
            for monster in self.defeated_monsters:
                if monster.is_hovered and monster.face_up:
                    hovered_monsters.append(monster)
                else:
                    non_hovered_monsters.append(monster)
            
            # Draw non-hovered monsters first
            for monster in non_hovered_monsters:
                monster.draw(surface)
            
            # Draw hovered monsters and their info
            for monster in hovered_monsters:
                # Draw the monster card
                monster.draw(surface)
    
    def _draw_inventory(self, surface):
        """Draw inventory panel and cards."""
        vertical_center = SCREEN_HEIGHT // 2
        
        # Create an inventory panel - taller and wider to accommodate full-size vertical card stack
        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y
        
        # Create the inventory panel using the Panel class
        if not hasattr(self, 'inventory_panel'):
            # Define a slightly more brown colour for the inventory panel to look more like aged parchment
            parchment_colour = (60, 45, 35)
            self.inventory_panel = Panel(
                (inv_width, inv_height), 
                (inv_x, inv_y),
                colour=parchment_colour,
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)  # Slightly lighter brown for border
            )
        
        # Draw the panel
        self.inventory_panel.draw(surface)
        
        # Get the rect for positioning
        inv_rect = self.inventory_panel.rect
        
        # Draw title with a slight glow effect for a magical appearance
        inv_title = self.body_font.render("Inventory", True, WHITE)
        # Create a subtle glow
        glow_surface = pygame.Surface((inv_title.get_width() + 10, inv_title.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (255, 240, 200, 50)  # Soft golden glow
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        
        # Position the glow and title text
        glow_rect = glow_surface.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 35)
        title_rect = inv_title.get_rect(centerx=inv_rect.centerx, top=inv_rect.top - 30)
        
        # Draw the glow and title
        surface.blit(glow_surface, glow_rect)
        surface.blit(inv_title, title_rect)
        
        # First sort inventory cards so hovered ones are at the end (will be drawn on top)
        # Use a stable sort so if there are multiple cards, their original order is preserved
        sorted_cards = sorted(self.inventory, key=lambda c: 1 if c.is_hovered else 0)
        
        # First pass - draw shadows for all cards
        for card in sorted_cards:
            self.ui_renderer._draw_card_shadow(surface, card)
        
        # Second pass - draw all cards and type information
        for card in sorted_cards:
            # Draw the card
            card.draw(surface)
            
            # Only draw card info if the card is hovered
            if card.face_up and card.is_hovered:
                # Get type text for the card
                type_text = ""
                if card.type == "weapon" and hasattr(card, 'weapon_type') and card.weapon_type:
                    weapon_type = card.weapon_type.upper()
                    # Show damage type for weapons
                    if hasattr(card, 'damage_type') and card.damage_type:
                        damage_type = card.damage_type.upper()
                        type_text = f"{weapon_type} ({damage_type})"
                elif card.type == "potion":
                    type_text = "HEALING"
    
    def _draw_ui_elements(self, surface):
        """Draw room cards, UI elements, and status displays."""
        # Draw room cards LAST always
        self.room.draw(surface)
        
        # Draw any visual effects (destruction/materialise animations)
        self.animation_manager.draw_effects(surface)
        
        # Draw hover text for inventory cards
        for card in self.inventory:
            if card.is_hovered and card.face_up:
                card.draw_hover_text(surface)
        
        # Draw hover text for equipped weapon
        if "node" in self.equipped_weapon and self.equipped_weapon["node"].is_hovered and self.equipped_weapon["node"].face_up:
            self.equipped_weapon["node"].draw_hover_text(surface)
        
        # Ensure all monsters in defeated_monsters have the is_defeated flag set
        for monster in self.defeated_monsters:
            monster.is_defeated = True
            
        # Draw hover text for defeated monsters
        for monster in self.defeated_monsters:
            if monster.is_hovered and monster.face_up:
                monster.draw_hover_text(surface)
        
        # Draw health display
        self.ui_renderer.draw_health_display(surface)

        # Draw deck count display
        self.ui_renderer.draw_deck_count(surface)

        # Draw UI animations (health changes, etc.)
        self.animation_manager.draw_ui_effects(surface)
            
        # Draw run button
        if not self.ran_last_turn and len(self.room.cards) == 4 and not self.animation_manager.is_animating():
            self.run_button.draw(surface)
        else:
            # Draw disabled run button with consistent styling
            button_rect = self.run_button.rect
            
            # Button background
            pygame.draw.rect(surface, LIGHT_GRAY, button_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, button_rect, 2, border_radius=5)
            
            # Render disabled text with the same font as the active button
            button_text = self.body_font.render("RUN", True, (150, 150, 150))  # Greyed out text
            button_text_rect = button_text.get_rect(center=button_rect.center)
            surface.blit(button_text, button_text_rect)
            
        # Draw any active message with fade effect
        self._draw_message(surface)
        
        # Draw status UI
        self.status_ui.draw(surface)
    
    def _draw_message(self, surface):
        """Draw any active message with fade effect."""
        if hasattr(self, 'message') and self.message:
            # Handle new fade-in/fade-out message style
            if "alpha" in self.message:
                # Create a temporary copy of the message for this frame with current alpha value
                current_alpha = self.message["alpha"]
                text_with_alpha = self.message["text"].copy()
                text_with_alpha.set_alpha(current_alpha)
                
                # Create a semi-transparent background
                bg_surface = pygame.Surface((self.message["bg_rect"].width, self.message["bg_rect"].height), pygame.SRCALPHA)
                bg_colour = (0, 0, 0, int(current_alpha * 0.7))  # Background slightly more transparent than text
                pygame.draw.rect(bg_surface, bg_colour, bg_surface.get_rect(), border_radius=8)
                
                # Create a very subtle border
                border_colour = (200, 200, 200, int(current_alpha * 0.5))
                pygame.draw.rect(bg_surface, border_colour, bg_surface.get_rect(), 1, border_radius=8)
                
                # Draw the message
                surface.blit(bg_surface, self.message["bg_rect"])
                surface.blit(text_with_alpha, self.message["rect"])
            else:
                # Fallback for old message format (just in case)
                pygame.draw.rect(surface, BLACK, self.message["bg_rect"], border_radius=8)
                pygame.draw.rect(surface, WHITE, self.message["bg_rect"], 2, border_radius=8)
                surface.blit(self.message["text"], self.message["rect"])
    
    # Forward key methods to our modular components
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
    try:
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
        print(f"Replaced {old_colour} with {new_colour} in {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

class RoomManager:
    """Manages room creation, transitions, and completion."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def start_new_room(self, last_card=None):
        """Start a new room with cards from the deck."""
        print(f"RoomManager.start_new_room called - current room: {self.playing_state.game_manager.floor_manager.current_room}")
        
        if self.playing_state.life_points <= 0:
            print("  Player is dead, not starting room")
            return
        
        if self.playing_state.animation_manager.is_animating():
            print("  Animations running, not starting room")
            return  # Don't start a new room if animations are running
            
        # If we're re-entering the playing state and the flag is already set, we've already started a room
        # in the enter method, so we should avoid starting a new one again in an upcoming update
        if hasattr(self.playing_state, 'room_started_in_enter') and self.playing_state.room_started_in_enter:
            print("  Room already started in enter(), not starting again")
            return
        
        # Reset the room state tracking flags when starting a new room
        self.playing_state.room_completion_in_progress = False
        
        # Clear the room
        self.playing_state.room.clear()
        
        # Keep the last card if provided
        if last_card:
            self.playing_state.room.add_card(last_card)
            last_card.face_up = True
            
            # Position the card correctly in the center of the room
            # Calculate the target position for the first card
            num_cards = min(4, len(self.playing_state.deck.cards) + 1)  # +1 for the last_card
            total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
            start_x = (SCREEN_WIDTH - total_width) // 2
            start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
            
            # The first position is for the last_card
            first_position = (start_x, start_y)
            
            # Position the last_card with animation
            self.playing_state.animate_card_movement(last_card, first_position)
        
        # Calculate how many cards to draw
        cards_to_draw = min(4 - len(self.playing_state.room.cards), len(self.playing_state.deck.cards))
        
        # Calculate final target positions first - this is AFTER adding the last_card if it exists
        num_cards = min(4, len(self.playing_state.deck.cards) + len(self.playing_state.room.cards))  # Always 4 cards in a full room
        total_width = (CARD_WIDTH * num_cards) + (self.playing_state.room.card_spacing * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40
        
        target_positions = []
        for i in range(num_cards):
            target_positions.append((
                int(start_x + i * (CARD_WIDTH + self.playing_state.room.card_spacing)),
                int(start_y)
            ))

        # Draw cards one by one with animations
        for i in range(cards_to_draw):
            if self.playing_state.deck.cards:
                card_data = self.playing_state.deck.draw_card()
                # Check if floor_type is included in card_data, otherwise use self.current_floor
                floor_type = card_data.get("floor_type", self.playing_state.current_floor)
                card = Card(card_data["suit"], card_data["value"], floor_type)
                
                # Cards start face down
                card.face_up = False
                
                # Set the initial position to the top of the deck
                if self.playing_state.deck.card_stack:
                    card.update_position(self.playing_state.deck.card_stack[-1])
                else:
                    card.update_position(self.playing_state.deck.position)
                
                # Add card to room
                self.playing_state.room.add_card(card)
                
                # Calculate which target position to use
                # i is the index of the new card we're drawing (0-based)
                # If we have a last_card, it's already in position 0
                # So new cards should start at position 1 (index 1)
                card_position_index = i + (1 if last_card else 0)
                
                # Ensure we don't go out of bounds
                if card_position_index < len(target_positions):
                    target_pos = target_positions[card_position_index]
                else:
                    # Fallback to last position if somehow we have too many cards
                    target_pos = target_positions[-1]
                
                # Create animation to move card to position with staggered timing
                delay = 0.1 * i  # Stagger the dealing animations
                
                # Create a delayed animation
                self.playing_state.schedule_delayed_animation(
                    delay,
                    lambda card=card, pos=target_pos: self.playing_state.animate_card_movement(
                        card, 
                        pos, 
                        duration=0.3,
                        on_complete=lambda c=card: self.playing_state.start_card_flip(c)
                    )
                )
        
        # Update deck display
        if self.playing_state.deck.card_stack:
            for i in range(cards_to_draw):
                if self.playing_state.deck.card_stack:
                    self.playing_state.deck.card_stack.pop()
        self.playing_state.deck.initialise_visuals()
    
    def run_from_room(self):
        """Run from the current room, moving all cards to the bottom of the deck."""
        if len(self.playing_state.room.cards) != 4 or self.playing_state.animation_manager.is_animating():
            return

        # Only allow running if all cards are face up
        for card in self.playing_state.room.cards:
            if not card.face_up or card.is_flipping:
                return

        self.playing_state.is_running = True

        # Animate cards moving to the bottom of the deck
        for card in list(self.playing_state.room.cards):
            # Calculate target position (bottom of deck)
            if self.playing_state.deck.card_stack:
                target_pos = self.playing_state.deck.card_stack[0]
            else:
                target_pos = self.playing_state.deck.position
            
            # Set z-index and create animation
            card.z_index = -100
            
            # Use standard card movement animation
            self.playing_state.animate_card_movement(
                card,
                target_pos,
                duration=0.3
            )
            
            # Add the card data back to the bottom of the deck
            card_data = {"suit": card.suit, "value": card.value}
            self.playing_state.deck.add_to_bottom(card_data)
        
        # Update the deck visuals
        self.playing_state.deck.initialise_visuals()
    
    def on_run_completed(self):
        """Complete the running action after animations finish."""
        # Clear the room
        self.playing_state.room.clear()
        self.playing_state.is_running = False
        
        # Update the deck visuals again
        self.playing_state.deck.initialise_visuals()
        
        # Set the ran_last_turn flag
        self.playing_state.ran_last_turn = True
        
        # Advance to the next room when running
        self.playing_state.game_manager.advance_to_next_room()
        
        # Update UI elements that show room number
        if hasattr(self.playing_state, 'status_ui') and hasattr(self.playing_state.status_ui, 'update_status'):
            self.playing_state.status_ui.update_status()
        
        # Chance to encounter a hire after running
        if hasattr(self.playing_state, 'hire_manager'):
            # Use a lower chance for hire encounters after running
            original_chance = self.playing_state.hire_manager.hire_encounter_chance
            self.playing_state.hire_manager.hire_encounter_chance = original_chance / 2
            
            hire_encounter_started = self.playing_state.hire_manager.try_start_hire_encounter()
            
            # Restore original chance
            self.playing_state.hire_manager.hire_encounter_chance = original_chance
            
            if hire_encounter_started:
                # We'll start a new room after the hire encounter finishes
                return
        
        # Start a new room if no hire encounter
        self.start_new_room()
    
    def transition_to_next_floor(self):
        """Helper method to transition to the next floor."""
        print("==== TRANSITIONING TO NEXT FLOOR ====")
        
        # Get current floor info for debugging
        current_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        current_floor = self.playing_state.game_manager.floor_manager.get_current_floor()
        print(f"Current floor: {current_floor} (index {current_floor_index})")
        
        # Clear the discard pile as we're moving to a new floor
        if hasattr(self.playing_state, 'discard_pile') and self.playing_state.discard_pile:
            # Reset the discard pile's cards
            self.playing_state.discard_pile.cards = []
            # Reset any visual representations
            if hasattr(self.playing_state.discard_pile, 'card_stack'):
                self.playing_state.discard_pile.card_stack = []

        # Advance to the next floor
        self.playing_state.game_manager.floor_manager.advance_floor()
        next_floor_index = self.playing_state.game_manager.floor_manager.current_floor_index
        next_floor = self.playing_state.game_manager.floor_manager.get_current_floor()
        print(f"Advanced to next floor: {next_floor} (index {next_floor_index})")
        
        # Reset this for playing state checks
        self.playing_state.floor_completed = False
        
        # Important: Update local player state data to be preserved during transition
        self.playing_state.game_manager.game_data["life_points"] = self.playing_state.life_points
        self.playing_state.game_manager.game_data["max_life"] = self.playing_state.max_life
        print(f"Preserved player stats: HP={self.playing_state.life_points}/{self.playing_state.max_life}")
        
        # Reset room count tracking
        self.playing_state.completed_rooms = 0
        print("Reset room completion tracking")

        self.playing_state._start_initial_room()
        print("==== FLOOR TRANSITION COMPLETE ====")
    
    def remove_and_discard(self, card):
        """Remove a card from the room and add it to the discard pile.
        This function should be called only after an animation completes."""
        # First remove from the room if it's still there
        if card in self.playing_state.room.cards:
            self.playing_state.room.remove_card(card)

        if card in self.playing_state.defeated_monsters:
            self.playing_state.defeated_monsters.remove(card)

        if self.playing_state.equipped_weapon and card == self.playing_state.equipped_weapon["node"]:
            self.playing_state.equipped_weapon = {}

        # Add to discard pile
        self.playing_state.discard_pile.add_card(card)

class Room:
    """Represents a room containing cards in the game."""
    
    def __init__(self, animation_manager=None, card_spacing=35):
        self.cards = []
        self.card_spacing = card_spacing
        self.z_index_counter = 0
        self.animation_manager = animation_manager
        # Font for card names
        self.name_font = None
    
    def add_card(self, card):
        self.cards.append(card)
        
        # Set z-index for proper layering
        card.z_index = self.z_index_counter
        self.z_index_counter += 1
    
    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            # Do not immediately animate - let the calling code handle animation timing
            # This prevents cards from disappearing during animations
            if len(self.cards) > 0:
                self.position_cards(animate=True, animation_manager=self.animation_manager)
    
    def clear(self):
        self.cards.clear()
    
    def get_card_count(self):
        return len(self.cards)
    
    def position_cards(self, animate=False, animation_manager=None):
        if not self.cards:
            return

        # Calculate positions with proper centering
        num_cards = len(self.cards)
        total_width = (CARD_WIDTH * num_cards) + (self.card_spacing * (num_cards - 1))
        
        # Center the entire card group on screen
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2 - 40

        # Sort cards by z-index for consistent positioning
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        
        # Get target positions for all cards
        for i, card in enumerate(sorted_cards):
            card_position = (0, 0)
            if num_cards == 1:
                # position final card as if left most side of 4 cards
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
                # Create animation with easing
                animation = MoveAnimation(
                    card,
                    card.rect.topleft,
                    card_position,
                    0.3,  # Smooth animation duration
                    EasingFunctions.ease_out_quad
                )
                animation_manager.add_animation(animation)
            else:
                # Immediate positioning without animation
                card.update_position(card_position)
    
    def get_card_at_position(self, position):
        for card in reversed(sorted(self.cards, key=lambda c: c.z_index)):
            if card.rect.collidepoint(position):
                return card
        return None
    
    def draw(self, surface):
        # Sort cards by z-index for proper layering
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        
        # Draw all cards
        for card in sorted_cards:
            card.draw(surface)
        
        # Draw hover action text for hovered cards (but not the top/bottom text)
        for card in sorted_cards:
            if card.is_hovered and card.face_up:
                # Draw hover text if card can be added to inventory or has attack options
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
        self.alpha_direction = True # true for decrease alpha, false for increase alpha
        self.speed = 40
    
    def enter(self):
        # Load fonts
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 23)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        
        # Load background
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load floor
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1: # left click
            # Go back to title screen instead of starting game
            self.game_manager.change_state("title")
    
    def update(self, delta_time):
        pass
    
    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - self.floor.get_width())/2, (SCREEN_HEIGHT - self.floor.get_height())/2))
        
        # Create a semi-transparent panel
        panel = Panel((800, 610), (SCREEN_WIDTH//2-400, SCREEN_HEIGHT//2-305), colour=DARK_GRAY)
        panel.draw(surface)
        
        # Draw title
        title_text = self.header_font.render("HOW TO PLAY", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, panel.rect.top + 40))
        surface.blit(title_text, title_rect)
        
        # Rules text
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

        # Continue text
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
    """
    Split an image into smaller images.
    
    :param image_path: Path to the input image.
    :param output_dir: Directory to save the split images.
    :param rows: Number of rows to split the image into.
    :param cols: Number of columns to split the image into.
    """
    # Open the image
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Calculate the size of each split image
    split_width = img_width // cols
    split_height = img_height // rows

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Split the image
    for row in range(rows):
        for col in range(cols):
            left = col * split_width
            upper = row * split_height
            right = left + split_width
            lower = upper + split_height

            # Crop the image
            cropped_img = img.crop((left, upper, right, lower))

            # Save the cropped image
            output_path = os.path.join(output_dir, f"{os.path.basename(image_path).split('.')[0]}_{row}_{col}.png")
            cropped_img.save(output_path)
            print(f"Saved {output_path}")

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
        # Get current game state info
        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()  # Now safely returns "unknown" if needed
        # Rename current floor with title case with apostrophe handling
        if "'" in current_floor:
            b = []
            for temp in current_floor.split():
                b.append(temp.capitalize())
            current_floor = " ".join(b)
        else:
            current_floor = current_floor.title()
        current_floor_index = max(1, floor_manager.current_floor_index + 1)  # Ensure index is at least 1
        
        # Use the floor manager's current_room which is now 1-based
        current_room = floor_manager.current_room
            
        total_rooms = FLOOR_TOTAL
        
        floor_text = self.header_font.render(f"Floor {current_floor_index}: {current_floor}", True, WHITE)
        
        panel_width = 650
        
        panel_padding = 60
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH//2 - panel_width//2, 50),
            (650, 90)
        ) 

        # Create dungeon-themed status panel if it doesn't exist yet
        if not hasattr(self, 'styled_panel'):
            # Create a panel with a parchment/scroll appearance
            self.styled_panel = Panel(
                (self.panel_rect.width, self.panel_rect.height),
                (self.panel_rect.left, self.panel_rect.top),
                colour=(70, 60, 45),  # Dark parchment colour
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(110, 90, 50)  # Darker border for scroll-like appearance
            )
        
        # Draw the styled panel
        self.styled_panel.draw(surface)
        
        # Draw floor info with a slight glow effect for emphasis
        floor_rect = floor_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 15)
        
        # Create a subtle glow behind the text (for magical floors)
        glow_surface = pygame.Surface((floor_text.get_width() + 10, floor_text.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (230, 220, 170, 30)  # Warm parchment glow
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        glow_rect = glow_surface.get_rect(center=floor_rect.center)
        
        # Apply the glow and text
        surface.blit(glow_surface, glow_rect)
        surface.blit(floor_text, floor_rect)
    
        # Draw room info with a more subtle appearance
        room_text = self.normal_font.render(f"Room {current_room}", True, (220, 220, 200))  # Slightly off-white
        room_rect = room_text.get_rect(centerx=self.panel_rect.centerx, top=floor_rect.bottom + 10)
        surface.blit(room_text, room_rect)

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
        self.torches = []
        self.torch_anim = None
        self.torch_anim_indexes = (0, 0)
        self.torch_lights = []
        self.title_glow = 0
        self.title_glow_dir = 1
        
        # Cards for visual effect
        self.cards = []
        self.card_images = {}
        self.monster_imgs = []
        self.weapon_imgs = []
        self.potion_imgs = []
        
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

        # Load two torches
        self.torch_anim = [pygame.transform.scale(ResourceLoader.load_image(f"torch_anim/torch_{i}.png"),(128,128)) for i in range(5)]
        # Select two random torches for the title screen (cannot be the same)
        self.torch_anim_indexes = random.sample(range(5), 2)
        self.torches = [self.torch_anim[i] for i in self.torch_anim_indexes]
        
        floor_image = "floor.png"        
        self.floor = ResourceLoader.load_image(floor_image)    
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        # Create title panel
        panel_width = 730
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
        buttons_y = panel_y + panel_height - button_height*2 - button_spacing*1 - 25
        
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
        
        # Rules button
        rules_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + button_height + button_spacing,
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
        
        # Left torch
        self.torch_lights.append({
            'x': SCREEN_WIDTH * 0.1,
            'y': SCREEN_HEIGHT // 2 - 40,
            'radius': 80,
            'flicker': 0,
            'flicker_speed': random.uniform(0.1, 0.2),
            'colour': (255, 150, 50)  # Orange-ish
        })
        
        # Right torch
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
        
        for monster_class in os.listdir("assets/monsters"):
            for monster_name in os.listdir(os.path.join("assets/monsters", monster_class)):
                self.monster_imgs.append(ResourceLoader.load_image(os.path.join("monsters", monster_class, monster_name), cache=False))
        for weapon_name in os.listdir("assets/weapons"):
            self.weapon_imgs.append(ResourceLoader.load_image(os.path.join("weapons", weapon_name), cache=False))
        for potion_name in os.listdir("assets/potions"):
            self.potion_imgs.append(ResourceLoader.load_image(os.path.join("potions", potion_name), cache=False))
        
        # Load a small selection of spades (monsters)
        for value in range(2, 15):
            key = f"spades_{value}"
            black_card_surf = ResourceLoader.load_image(f"cards/spades_{value}.png")
            self.card_images[key] = self.add_monster_card(black_card_surf, value)
        
        # Load a small selection of diamonds (weapons)
        for value in range(2, 11):
            key = f"diamonds_{value}"
            weapon_card_surf = ResourceLoader.load_image(f"cards/diamonds_{value}.png")
            self.card_images[key] = self.add_weapon_card(weapon_card_surf, value)
        
        # Load a small selection of hearts (potions)
        for value in range(2, 11):
            key = f"hearts_{value}"
            potion_card_surf = ResourceLoader.load_image(f"cards/hearts_{value}.png")
            self.card_images[key] = self.add_potion_card(potion_card_surf, value)
        
        # Load the card back
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
        # Clear existing cards only on first initialization
        if len(self.cards) == 0:
            self.cards = []
            card_count = num_cards
        else:
            # Just add a single card when called during updates
            card_count = 1
        
        for _ in range(card_count):
            card_keys = list(self.card_images.keys())
            card_key = random.choice(card_keys)
            
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
                    self.game_manager.start_new_run()
                    self.game_manager.change_state("playing")
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
            self.rules_button.check_hover(mouse_pos)
        else:
            # Force non-hover state for buttons when a card is under cursor
            self.start_button.hovered = False
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

    def _update_torches(self, delta_time):
        """Update the torch animation by cycling through frame indexes at a steady speed"""
        for i, torch in enumerate(self.torches):
            self.torch_anim_indexes[i] += delta_time * 4
            self.torches[i] = self.torch_anim[int(self.torch_anim_indexes[i]) % len(self.torch_anim)]
            
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
        
        # Update torches
        self._update_torches(delta_time)
        
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
        
        for i, torch in enumerate(self.torches):
            torch_rect = torch.get_rect(center=(SCREEN_WIDTH * (0.1 + 0.8*i), SCREEN_HEIGHT // 2))
            surface.blit(torch, torch_rect)
        
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
            "Gambling is illegal, but this is a dungeon!",
            "Flipping you off is a card game term!",
            "Original concept by Kurt Bieg and Zach Gage!",
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
        max_width = 600  # Maximum width for a tagline before wrapping
        
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
            line1_rect = line1_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 15)
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

class UIFactory:
    """Creates and manages UI elements."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def create_run_button(self):
        """Create the run button with dungeon styling."""
        # Increase button size to be more prominent
        run_width = 90  # Wider button
        run_height = 45  # Taller button
        
        # Position below status UI and above room
        run_x = SCREEN_WIDTH // 2
        run_y = 170  # Below status UI, above room
        
        run_button_rect = pygame.Rect(run_x - run_width // 2, run_y - run_height // 2, run_width, run_height)
        
        # Use the Pixel Times font with dungeon styling
        self.playing_state.run_button = Button(
            run_button_rect, 
            "RUN", 
            self.playing_state.body_font,
            text_colour=WHITE,  # White text for better visibility
            dungeon_style=True,  # Enable dungeon styling
            panel_colour=(70, 20, 20),  # Dark red for urgency
            border_colour=(120, 40, 40)  # Red border for danger/action
        )
        
class UIRenderer:
    """Handles rendering of UI elements and game objects."""
    
    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state
    
    def draw_health_display(self, surface):
        """Draw health display with current and max life points."""
        # Health display parameters
        health_display_x = 40
        health_display_y = SCREEN_HEIGHT - self.playing_state.deck.rect.y
        health_bar_width = 140
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

    def draw_deck_count(self, surface):
        """Draw deck card counter display with current and total cards."""
        # Counter display parameters
        count_panel_width = 80
        count_panel_height = 40
        count_panel_x = 87 + CARD_WIDTH//2 - count_panel_width//2
        count_panel_y = 35 + (len(self.playing_state.deck.cards)-1)*3 + CARD_HEIGHT//2 - count_panel_height//2
        
        # Create or update health panel with dungeon style
        if not hasattr(self, 'count_panel'):
            panel_rect = pygame.Rect(
                count_panel_x, 
                count_panel_y,
                count_panel_width,
                count_panel_height
            )
            
            # Create the panel with a dark wooden appearance for the deck count
            self.count_panel = Panel(
                (panel_rect.width, panel_rect.height),
                (panel_rect.left, panel_rect.top),
                colour=(45, 35, 30),  # Very dark brown
                alpha=220,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(90, 60, 35)  # Medium brown border
            )
        else:
            # Update the position of the existing panel
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
    """
    Keeps only the suit and rank in the top-left and bottom-right corners of a playing card image.
    Turns everything else white except for already transparent areas.
    
    :param image_path: Path to the input PNG file.
    :param output_path: Path to save the modified PNG file.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        pixels = img.load()
        width, height = img.size
        
        # Define corner areas (adjust values if needed)
        corner_width = int(width / 4.6)
        corner_height = int(height / 3)
        
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                
                # Keep pixels in the top-left or bottom-right corners, white out the rest
                if not ((x < corner_width and y < corner_height) or (x > width - corner_width - (5 if "10" in image_path else 0) and y > height - corner_height)):
                    if a > 0:  # Only change non-transparent pixels
                        pixels[x, y] = (255, 255, 255, 255)
        
        img.save(output_path, "PNG")
        print(f"Image saved successfully to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

def process_all_cards(input_folder):
    """
    Processes all card images in the given folder that start with clubs, hearts, diamonds, or spades.
    
    :param input_folder: Path to the folder containing card images.
    :param input_folder: Path to save processed images.
    """
    for filename in os.listdir(input_folder):
        if filename.startswith(("clubs", "hearts", "diamonds", "spades")) and filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(input_folder, filename)
            print(f"Processing {filename}...")
            isolate_card_corners(input_path, output_path)

def main():
    """ Main entry point for the game. """
    
    # Initialise pygame
    pygame.init()
    
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scoundrel - The 52-Card Roguelike Dungeon Crawler")
    clock = pygame.time.Clock()
    
    # Create the game manager
    game_manager = GameManager()
    
    # Main game loop
    running = True
    while running:
        # Calculate delta time
        delta_time = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
        
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # Pass the event to the current state
                game_manager.handle_event(event)
        
        # Update
        game_manager.update(delta_time)
        
        # Draw
        game_manager.draw(screen)
        
        # Flip the display
        pygame.display.flip()
    
    # Quit the game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()