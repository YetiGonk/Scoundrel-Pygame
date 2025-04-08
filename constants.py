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
        "lower": 2
    },
    "clubs": {
        "upper": 14,
        "lower": 2
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