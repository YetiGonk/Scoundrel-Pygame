""" Constants used throughout the Scoundrel game. """

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

SHIELD_COLOR = (100, 180, 255, 120)
SHIELD_GLOW = (100, 150, 255, 50)
SHIELD_INNER = (50, 120, 230, 20)
SHIELD_TEXT = (180, 220, 255)

# UI Panel Colors
PANEL_DEFAULT_BORDER = (80, 60, 40)
PANEL_WOODEN = (80, 60, 30)
PANEL_WOODEN_BORDER = (130, 100, 40)
PANEL_HEALTH = (60, 30, 30)
PANEL_HEALTH_BORDER = (100, 50, 50)
PANEL_SHIELD = (40, 60, 120)
PANEL_SHIELD_BORDER = (80, 130, 200)

# Effect Colors
EFFECT_SHIELD_COLOR = (60, 120, 200)
EFFECT_SHIELD_PANEL = (40, 70, 120)
EFFECT_SHIELD_BORDER = (80, 140, 220)
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

# Item and spell panel dimensions
SPACING = 40
ITEM_PANEL_WIDTH = 160
ITEM_PANEL_HEIGHT = 200
ITEM_PANEL_POSITION = (SCREEN_WIDTH - ITEM_PANEL_WIDTH - SPACING, SCREEN_HEIGHT - ITEM_PANEL_HEIGHT - SPACING)

SPELL_PANEL_WIDTH = 160
SPELL_PANEL_HEIGHT = 200
SPELL_PANEL_POSITION = (SCREEN_WIDTH - ITEM_PANEL_WIDTH - SPACING, SPACING)

# UI HUD dimensions
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 24
HEALTH_BAR_POSITION = (20, SCREEN_HEIGHT - 30)

GOLD_BAR_WIDTH = 120
GOLD_BAR_HEIGHT = 24
GOLD_BAR_POSITION = (HEALTH_BAR_POSITION[0], HEALTH_BAR_POSITION[1] - GOLD_BAR_HEIGHT - 10)

EFFECT_ICON_SIZE = 40
EFFECT_ICON_SPACING = 10
EFFECT_START_POSITION = (SCREEN_WIDTH//2 - 100, 20)

SHIELD_RADIUS = 150
SHIELD_PANEL_WIDTH = 120
SHIELD_PANEL_HEIGHT = 30

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

SHIELD_PULSE_FREQUENCY = 500  # ms
SHIELD_PULSE_AMPLITUDE = 0.15
SHIELD_EDGE_WIDTH = 5
SHIELD_DASH_LENGTH = 15
SHIELD_DASH_COUNT = 16
SHIELD_SPARK_CHANCE = 0.1

EFFECT_PULSE_PERMANENT = (0.9, 0.1, 800)  # base, amplitude, frequency
EFFECT_PULSE_TEMPORARY = (0.8, 0.2, 200)  # base, amplitude, frequency
EFFECT_EXPIRE_THRESHOLD = 2000  # ms

# Game settings
STARTING_HEALTH = 20
MAX_HEALTH = 20

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

STANDARD_DECK = {
    "diamonds": {
        "upper": 10,
        "lower": 2
    },
    "hearts": {
        "upper": 10,
        "lower": 2
    },
    "spades": {
        "upper": 14,
        "lower": 2
    },
    "clubs": {
        "upper": 14,
        "lower": 2
    },
}

EASY_DECK = {
    "diamonds": {
        "upper": 14,
        "lower": 2
    },
    "hearts": {
        "upper": 14,
        "lower": 2
    },
    "spades": {
        "upper": 10,
        "lower": 2
    },
    "clubs": {
        "upper": 10,
        "lower": 2
    },
}

HARD_DECK = {
    "diamonds": {
        "upper": 10,
        "lower": 4
    },
    "hearts": {
        "upper": 10,
        "lower": 4
    },
    "spades": {
        "upper": 14,
        "lower": 2
    },
    "clubs": {
        "upper": 14,
        "lower": 2
    },
}

DUNGEON_DECK = {
    "diamonds": {
        "upper": 12,
        "lower": 2
    },
    "hearts": {
        "upper": 12,
        "lower": 2
    },
    "spades": {
        "upper": 12,
        "lower": 2
    },
    "clubs": {
        "upper": 12,
        "lower": 2
    },
}

FOREST_DECK = {
    "diamonds": {
        "upper": 11,
        "lower": 3
    },
    "hearts": {
        "upper": 14,  # More healing in forest
        "lower": 4
    },
    "spades": {
        "upper": 11,
        "lower": 2
    },
    "clubs": {
        "upper": 11,
        "lower": 2
    },
}

LIBRARY_DECK = {
    "diamonds": {
        "upper": 14,  # More powerful weapons
        "lower": 2
    },
    "hearts": {
        "upper": 10,
        "lower": 2
    },
    "spades": {
        "upper": 12,
        "lower": 3
    },
    "clubs": {
        "upper": 12,
        "lower": 3
    },
}

CRYPT_DECK = {
    "diamonds": {
        "upper": 14,
        "lower": 3
    },
    "hearts": {
        "upper": 10,  # Less healing
        "lower": 2
    },
    "spades": {
        "upper": 14,  # Stronger monsters
        "lower": 3
    },
    "clubs": {
        "upper": 14,  # Stronger monsters
        "lower": 3
    },
}

VOLCANO_DECK = {
    "diamonds": {
        "upper": 14,  # Strong weapons
        "lower": 2
    },
    "hearts": {
        "upper": 14,  # Less healing
        "lower": 2
    },
    "spades": {
        "upper": 14,  # Very strong monsters
        "lower": 4
    },
    "clubs": {
        "upper": 14,
        "lower": 4
    },
}

# Debug mode settings
DEBUG_MODE = True  # Set to True to enable debug features

# Update DECK_DICT to include floor-specific decks
DECK_DICT = {
    "standard": STANDARD_DECK,
    "easy": EASY_DECK,
    "hard": HARD_DECK,
    "dungeon": DUNGEON_DECK,
    "forest": FOREST_DECK,
    "library": LIBRARY_DECK,
    "crypt": CRYPT_DECK,
    "volcano": VOLCANO_DECK,
}

DECK_DESC_DICT = {
    "standard": "The standard deck. The original game.",
    "easy": "For the shmucks with no 'cojones'. No face or ace monster cards, all weapons and potions.",
    "hard": "For the crazies with too many 'cojones'. All monsters, no face or ace weapons or potions.",
    "dungeon": "Standard dungeon cards with balanced challenges.",
    "forest": "Nature-themed cards with enhanced healing potions.",
    "library": "Magical tomes and scrolls with powerful weapons.",
    "crypt": "Undead monsters and cursed treasures with fewer healing options.",
    "volcano": "Fire monsters and molten weapons with extreme challenges.",
}