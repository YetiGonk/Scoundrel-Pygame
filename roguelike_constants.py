""" Constants for the roguelike elements of Scoundrel. """
import random

# Floor definitions
FLOOR_TYPES = ["dungeon", "forest", "library", "crypt", "MOLTEN"]

# Floor structure
FLOOR_STRUCTURE = {
    "rooms_per_floor": 12,  # Maximum potential rooms (flexible)
    "treasure_rooms": [1, 10],  # Room numbers where treasures appear
    # Boss room functionality removed
}

# Treasure inventory sizes
TREASURE_INVENTORY = {
    "cards": 2,  # Special cards that can be found
}

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
    9: "hard",
    10: "hard",
    11: "hard",
    12: "insane",
    13: "insane",
    14: "insane"
}

MONSTER_DIFFICULTY_MAP = {
    "easy": [
        "monsters/Animal/Giant Brown Bats.png",
        "monsters/Animal/Giant Fruit Bats.png",
        "monsters/Animal/Rat.png",
        "monsters/Animal/Snake.png",
        "monsters/Class/Clown .png",
        "monsters/Class/Merchant.png",
        "monsters/Dragon/Dragon Egg.png",
        "monsters/Ghost/Little ghost.png",
        "monsters/Ghost/Will-o'-the-wisp.png",
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
        "monsters/Class/Archer.png",
        "monsters/Class/Bard.png",
        "monsters/Class/Blacksmith.png",
        "monsters/Class/Fighter.png",
        "monsters/Class/Miner.png",
        "monsters/Class/Nun.png",
        "monsters/Class/Prisoner.png",
        "monsters/Class/Shooter.png",
        "monsters/Class/Thief.png",
        "monsters/Dragon/Black Drake.png",
        "monsters/Dragon/Blue Drake.png",
        "monsters/Dragon/Gold Drake.png",
        "monsters/Dragon/Green Drake.png",
        "monsters/Dragon/Orange Drake.png",
        "monsters/Dragon/Red Drake.png",
        "monsters/Ghost/Female ghost.png",
        "monsters/Ghost/Ghost.png",
        "monsters/Ghost/Ghost in painting.png",
        "monsters/Ghost/Lantern ghost.png",
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
        "monsters/Class/Berserker.png",
        "monsters/Class/Druid.png",
        "monsters/Class/Magician.png",
        "monsters/Class/Samurai .png",
        "monsters/Class/Tamer.png",
        "monsters/Class/Warrior.png",
        "monsters/Dragon/Black Dragon.png",
        "monsters/Dragon/Blue Dragon.png",
        "monsters/Dragon/Earth Dragon.png",
        "monsters/Dragon/Green Dragon.png",
        "monsters/Dragon/Orange Dragon.png",
        "monsters/Dragon/Red Dragon.png",
        "monsters/Ghost/Ghost dragon.png",
        "monsters/Ghost/Goblin Ghost.png",
        "monsters/Ghost/Magic ghost.png",
        "monsters/Ghost/Three headed ghost.png",
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

WEAPON_MAPPINGS = {
    0: "arrow",  # Non-valued card for arrow
    2: "shortsword",
    3: "shortsword",
    4: "shield",
    5: "axe",
    6: "warhammer",
    7: "flail",
    8: "axe",
    9: "greatsword",
    10: "greatsword",
    11: "longbow",
    12: "warhammer",
    13: "crossbow",
    14: "greatsword"
}

WEAPON_DAMAGE_TYPES = {
    "arrow": "piercing",
    "shortsword": "slashing",
    "shield": "bludgeoning",
    "axe": "slashing",
    "warhammer": "bludgeoning",
    "flail": "bludgeoning",
    "greatsword": "slashing",
    "crossbow": "piercing",
    "longbow": "piercing"
}

