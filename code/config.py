"""
Configuration file for Scoundrel
All game constants and settings
"""

from pathlib import Path

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

# Gold colors
GOLD_COLOUR = (255, 215, 0)
GOLD_HIGHLIGHT = (255, 240, 120)
GOLD_BORDER = (184, 134, 11)
GOLD_TEXT = (255, 230, 150)

# Health colors
HEALTH_COLOUR_GOOD = (50, 180, 50)
HEALTH_COLOUR_WARNING = (220, 160, 40)
HEALTH_COLOUR_DANGER = (200, 50, 50)

HEALTH_GLOW_GOOD = (70, 220, 70, 40)
HEALTH_GLOW_WARNING = (240, 180, 60, 40)
HEALTH_GLOW_DANGER = (240, 90, 90, 40)

# Panel colors
PANEL_DEFAULT_BORDER = (80, 60, 40)
PANEL_WOODEN = (80, 60, 30)
PANEL_WOODEN_BORDER = (130, 100, 40)
PANEL_HEALTH = (60, 30, 30)
PANEL_HEALTH_BORDER = (100, 50, 50)

# Effect colors
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

# Card dimensions
CARD_WIDTH = 99
CARD_HEIGHT = 135

# UI positions and dimensions
MENU_WIDTH = 600
MENU_HEIGHT = 150
MENU_POSITION = (SCREEN_WIDTH//2 - MENU_WIDTH//2, SCREEN_HEIGHT//2 - MENU_HEIGHT)

WEAPON_POSITION = (486, 420)
MONSTER_STACK_OFFSET = (30, 10)
MONSTER_START_OFFSET = (150, 0)

RUN_WIDTH = 76
RUN_HEIGHT = 40
RUN_POSITION = (1050, 283)

DECK_POSITION = (SCREEN_WIDTH//2 - FLOOR_WIDTH//2 - CARD_WIDTH - 50, 
                 SCREEN_HEIGHT//2 - FLOOR_HEIGHT//2)

DISCARD_POSITION = (SCREEN_WIDTH//2 - FLOOR_WIDTH//2 - CARD_WIDTH - 50, 
                    FLOOR_HEIGHT - 145 - CARD_HEIGHT)

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

# Panel styling
PANEL_BORDER_RADIUS = 8
PANEL_ALPHA = 230
PANEL_BORDER_WIDTH = 2

# Button styling
BUTTON_PANEL_COLOUR = (60, 45, 35)
BUTTON_BORDER_WIDTH = 3
BUTTON_BORDER_RADIUS = 8
BUTTON_ALPHA = 250
BUTTON_GLOW_SIZE = 6
BUTTON_HOVER_GLOW_WHITE = (255, 255, 255, 30)
BUTTON_HOVER_GLOW_DARK = (0, 0, 0, 30)
BUTTON_HOVER_LIGHTEN = 0.3
BUTTON_ROUND_CORNER = 5

# Gold particle effects
GOLD_CHANGE_DURATION = 2000
GOLD_PARTICLE_FADE_SPEED = (0.5, 1.5)
GOLD_PARTICLE_SPEED = (0.2, 0.6)
GOLD_PARTICLE_SIZE = (1, 2.5)
GOLD_PARTICLE_SPREAD = 5

# Effect animations
EFFECT_PULSE_PERMANENT = (0.9, 0.1, 800)
EFFECT_PULSE_TEMPORARY = (0.8, 0.2, 200)
EFFECT_EXPIRE_THRESHOLD = 2000

# Player starting stats
STARTING_HEALTH = 20
MAX_HEALTH = 20

# Deck configuration
DECK_TOTAL_COUNT = 52
DECK_MONSTER_COUNT = (18, 25)
DECK_BLACK_VALUE_RANGE = (2, 14)
DECK_HEARTS_VALUE_RANGE = (2, 10)
DECK_DIAMONDS_VALUE_RANGE = (2, 10)

# Asset paths
OUTPUT_PATH = Path(__file__).parent.parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Font sizes
TITLE_FONT_SIZE = 64
HEADER_FONT_SIZE = 36
BODY_FONT_SIZE = 28
NORMAL_FONT_SIZE = 20

# Game constants
SUITS = ["diamonds", "hearts", "spades", "clubs"]
FLOOR_TOTAL = 20

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

# Starting attributes
STARTING_ATTRIBUTES = {
    "life_points": 20,
    "max_life": 20,
}

# Monster definitions
MONSTER_RANKS = {
    2: "easy", 3: "easy", 4: "easy", 5: "easy",
    6: "medium", 7: "medium", 8: "medium", 9: "medium",
    10: "hard", 11: "hard", 12: "hard",
    13: "insane", 14: "insane"
}

MONSTER_CLASSES = ["Animal", "Dragon", "Ghost", "Goblin", "Other", "Slime"]

MONSTER_CLASS_MAP = {
    "Animal": ["Basilisk", "Giant Ant", "Giant Brown Bats", "Giant Centipede", 
               "Giant Fire Ant", "Giant Scorpion", "Giant Tarantula", 
               "Giant Wolf Spider", "Lion", "Rat", "Rat King", "Snake", 
               "Tiger", "Vampire Bats", "Wolf"],
    "Dragon": ["Armoured Dragon", "Black Dragon", "Black Drake", "Blue Dragon", 
               "Blue Drake", "Chromatic Dragon", "Earth Dragon", "Energy Dragon", 
               "Evil Dragon", "Gold Dragon", "Gold Drake", "Green Dragon", 
               "Green Drake", "Magic Dragon", "Orange Dragon", "Orange Drake", 
               "Red Dragon", "Red Drake", "Undead Dragon"],
    "Ghost": ["Banshee", "Ghost Dragon", "Painting Ghost", "Goblin Ghost", 
              "Lantern Ghost", "Little Ghost", "Magic Ghost", 
              "Three-Headed Ghost", "Will-O'-The-Wisp"],
    "Goblin": ["Goblin", "Goblin Archer", "Goblin King", "Goblin Magician", 
               "Goblin Merchant", "Goblin Thief", "Goblin Warrior", 
               "Three-Headed Troll"],
    "Other": ["Blue Myconid", "Centaur", "Cerberus", "Celestial", "Ent", 
              "Fire Elemental", "Hydra", "Mummy", "Pegasus", "Stone Golem", 
              "Unicorn"],
    "Slime": ["Black Slime", "Blue Slime", "Green Slime", "Orange Slime", 
              "Ooze Dragon", "Slime King"]
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

# Weapon definitions
WEAPON_RANKS = {
    2: "novice", 3: "novice", 4: "novice", 5: "novice",
    6: "intermediate", 7: "intermediate", 8: "intermediate", 9: "intermediate",
    10: "adept", 11: "adept", 12: "adept",
    13: "master", 14: "master"
}

WEAPON_RANK_MAP = {
    "novice": ["dagger", "shortsword", "shield", "axe", "mace", "spear"],
    "intermediate": ["spear", "flail", "axe", "pickaxe", "club", "shortsword", "rapier"],
    "adept": ["warhammer", "longbow", "battleaxe", "scythe", "halberd", "greatsword"],
    "master": ["greatsword", "crossbow", "battleaxe", "warhammer"]
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