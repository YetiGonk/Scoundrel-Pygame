""" Constants for the roguelike elements of Scoundrel. """
import random

# Floor names
# The first part of the name is a descriptor (e.g. "Forgotten"), and the second part is a location (e.g. "Catacombs").
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
        "Oubliette", "Colosseum", "Forge", "Sepulcher", "Haven",
        "Menagerie", "Cathedral", "Cistern", "Repository", "Docks"
    ]
}

# Floor structure
FLOOR_STRUCTURE = {
    "rooms_per_floor": 12,  # Maximum potential rooms (flexible)
    "treasure_rooms": [6, 11],  # Room numbers where treasures appear
    # Boss room functionality removed
}

# Treasure inventory sizes
TREASURE_INVENTORY = {
    "cards": 2,  # Special cards that can be found
}

# Merchant rooms removed

# Floor types (dungeon, forest, library, crypt)
FLOOR_TYPES = ["dungeon", "forest", "library", "crypt", "molten"]

# Starting player attributes
STARTING_ATTRIBUTES = {
    "gold": 0,
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
