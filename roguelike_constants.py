""" Constants for the roguelike elements of Scoundrel. """

# Floor definitions
FLOOR_TYPES = ["dungeon", "forest", "library", "crypt", "volcano"]

# Floor structure
FLOOR_STRUCTURE = {
    "rooms_per_floor": 12,
    "merchant_rooms": [4, 8],  # Room numbers where merchants appear
    "boss_room": 12,  # Last room is always the boss
}

# Item and spell rarity
RARITY_TYPES = ["common", "uncommon", "rare", "legendary"]

# Item types
ITEM_TYPES = ["passive", "active"]

# Generic item template
ITEM_TEMPLATE = {
    "name": "",
    "description": "",
    "type": "",  # passive or active
    "rarity": "",
    "durability": 0,  # How many uses before breaking (0 = infinite)
    "effect": "",  # Function name to call for effect
    "icon": "",  # Path to icon image
}

# Spell template
SPELL_TEMPLATE = {
    "name": "",
    "description": "",
    "rarity": "",
    "memory_points": 0,  # How many rooms before forgetting
    "effect": "",  # Function name to call for effect
    "icon": "",  # Path to icon image
}

# Merchant inventory sizes
MERCHANT_INVENTORY = {
    "items": 3,
    "spells": 3,
    "cards": 2,  # Special cards that can be purchased
}

# Starting player attributes
STARTING_ATTRIBUTES = {
    "gold": 50,
    "item_slots": 3,
    "spell_slots": 2,
    "life_points": 20,
    "max_life": 20,
}

# Item and spell selection at floor start
FLOOR_START_SELECTION = {
    "items": 5,  # Show 5 items
    "spells": 5,  # Show 5 spells
    "picks": 2,  # Player can pick 2 total (any combination)
}

# Custom deck variations
# These modify the standard deck for each floor
DECK_VARIATIONS = {
    "dungeon": {
        "description": "Standard dungeon cards",
        # No modifications to base deck
    },
    "forest": {
        "description": "Nature-themed cards with stronger healing",
        "hearts": {"modifier": 1.5},  # Hearts heal 50% more
    },
    "library": {
        "description": "Magical tomes and scrolls",
        "special_cards": ["tome", "scroll"],  # Special card types
    },
    "crypt": {
        "description": "Undead monsters and cursed treasures",
        "clubs": {"modifier": 1.2},  # Clubs 20% stronger
        "diamonds": {"modifier": 1.2},  # Diamonds 20% stronger
    },
    "volcano": {
        "description": "Fire monsters and molten weapons",
        "spades": {"modifier": 1.5},  # Spades 50% stronger
        "diamonds": {"modifier": 1.5},  # Diamonds 50% stronger
    },
}

# Boss cards - one per floor
BOSS_CARDS = {
    "dungeon": {"suit": "spades", "value": 15, "name": "Dungeon Keeper"},
    "forest": {"suit": "clubs", "value": 15, "name": "Ancient Treant"},
    "library": {"suit": "clubs", "value": 16, "name": "Forbidden Grimoire"},
    "crypt": {"suit": "spades", "value": 16, "name": "Lich King"},
    "volcano": {"suit": "spades", "value": 17, "name": "Fire Elemental"},
}