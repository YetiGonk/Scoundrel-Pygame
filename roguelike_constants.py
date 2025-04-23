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

# Monster definitions based on suit and value for each floor type
FLOOR_MONSTERS = {
    "dungeon": {
        "spades": {
            # Lower values (2-5): Easy monsters
            2: {"name": "Goblin", "image": "monsters/goblin.png", "ability": None},
            3: {"name": "Skeleton", "image": "monsters/skeleton.png", "ability": None},
            4: {"name": "Ghoul", "image": "monsters/ghoul.png", "ability": None},
            5: {"name": "Giant Snail", "image": "monsters/giant_snail.png", "ability": None},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Animated Armour", "image": "monsters/animated_armour.png", "ability": "block_first_attack"},
            7: {"name": "Stone Golem", "image": "monsters/stone_golem.png", "ability": "reduced_damage"},
            8: {"name": "Zombie", "image": "monsters/zombie.png", "ability": "poison"},
            9: {"name": "Ghost", "image": "monsters/ghost.png", "ability": "phase_shift"},
            10: {"name": "Skull Sentinel", "image": "monsters/skull_sentinel.png", "ability": None},
            # Face cards (11-14): Hard monsters
            11: {"name": "Wraith", "image": "monsters/wraith.png", "ability": "life_drain"},
            12: {"name": "Troll", "image": "monsters/troll.png", "ability": "regeneration"},
            13: {"name": "Fire Knight", "image": "monsters/fire_knight.png", "ability": "burning_attack"},
            14: {"name": "Beholder", "image": "monsters/beholder.png", "ability": "magic_attacks"},
        },
        "clubs": {
            # Lower values (2-5): Easy monsters
            2: {"name": "Crab", "image": "monsters/crab.png", "ability": None},
            3: {"name": "Evil Ooze", "image": "monsters/evil_ooze.png", "ability": "split"},
            4: {"name": "Floating Eyes", "image": "monsters/floating_eyes.png", "ability": "confusion"},
            5: {"name": "Ghoul", "image": "monsters/ghoul.png", "ability": None},
            # Mid values (6-10): Medium difficulty 
            6: {"name": "Giant Hornet", "image": "monsters/giant_hornet.png", "ability": "poison"},
            7: {"name": "Adder", "image": "monsters/adder.png", "ability": "poison"},
            8: {"name": "Python", "image": "monsters/python.png", "ability": "constriction"},
            9: {"name": "Lizard Soldier", "image": "monsters/lizard_soldier.png", "ability": None},
            10: {"name": "Crucible Knight", "image": "monsters/crucible_knight.png", "ability": "counter_attack"},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Cyclops", "image": "monsters/cyclops.png", "ability": "stun_attack"},
            12: {"name": "Reaper", "image": "monsters/reaper.png", "ability": "fear"},
            13: {"name": "Mad Mage", "image": "monsters/mad_mage.png", "ability": "spell_reflection"},
            14: {"name": "Fallen Angel", "image": "monsters/fallen_angel.png", "ability": "holy_resistance"},
        },
    },
    
    "forest": {
        "spades": {
            # Lower values (2-5): Easy monsters
            2: {"name": "Giant Snail", "image": "monsters/giant_snail.png", "ability": None},
            3: {"name": "Gecko", "image": "monsters/gecko.png", "ability": None},
            4: {"name": "Snatching Vine", "image": "monsters/snatching_vine.png", "ability": "entangle"},
            5: {"name": "Giant Tarantula", "image": "monsters/giant_tarantula.png", "ability": "web_trap"},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Razor Crow", "image": "monsters/razor_crow.png", "ability": "dive_attack"},
            7: {"name": "Adder", "image": "monsters/adder.png", "ability": "poison"},
            8: {"name": "Python", "image": "monsters/python.png", "ability": "constriction"},
            9: {"name": "Drunk Spirit", "image": "monsters/drunk_spirit.png", "ability": "confusion"},
            10: {"name": "Fire Spirit", "image": "monsters/fire_spirit.png", "ability": "burning_attack"},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Hag", "image": "monsters/hag.png", "ability": "curse"},
            12: {"name": "Haunted Tree", "image": "monsters/haunted_tree.png", "ability": "root_attack"},
            13: {"name": "Ent Warrior", "image": "monsters/ent_warrior.png", "ability": "crushing_blow"},
            14: {"name": "Brood Mother", "image": "monsters/brood_mother.png", "ability": "spawn_spiders"},
        },
        "clubs": {
            # Lower values (2-5): Easy monsters
            2: {"name": "Evil Ooze", "image": "monsters/evil_ooze.png", "ability": "split"},
            3: {"name": "Elephant", "image": "monsters/elephant.png", "ability": "charge"},
            4: {"name": "Bird Knight", "image": "monsters/bird_knight.png", "ability": None},
            5: {"name": "Lizard Soldier", "image": "monsters/lizard_soldier.png", "ability": None},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Giant Hornet", "image": "monsters/giant_hornet.png", "ability": "poison"},
            7: {"name": "Swamp Abomination", "image": "monsters/swamp_abomination.png", "ability": "poison_cloud"},
            8: {"name": "Noxious Gas", "image": "monsters/noxious_gas.png", "ability": "toxicity"},
            9: {"name": "Ghoul", "image": "monsters/ghoul.png", "ability": None},
            10: {"name": "Undead Jester", "image": "monsters/undead_jester.png", "ability": "bad_joke"},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Ghoul Leader", "image": "monsters/ghoul_leader.png", "ability": "summon_ghouls"},
            12: {"name": "Lizard King", "image": "monsters/lizard_king.png", "ability": "royal_command"},
            13: {"name": "Medusa", "image": "monsters/medusa.png", "ability": "petrify"},
            14: {"name": "World Snake", "image": "monsters/world_snake.png", "ability": "deadly_constriction"},
        },
    },
    
    "library": {
        "spades": {
            # Lower values (2-5): Easy monsters
            3: {"name": "Sentient Totem", "image": "monsters/sentient_totem.png", "ability": "knowledge_drain"},
            4: {"name": "Celestial", "image": "monsters/star_man.png", "ability": "astral_projection"},
            5: {"name": "Evil Moon", "image": "monsters/evil_moon.png", "ability": "lunar_magic"},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Evil Sun", "image": "monsters/evil_sun.png", "ability": "solar_flare"},
            7: {"name": "Ghost", "image": "monsters/ghost.png", "ability": "phase_shift"},
            8: {"name": "Undead Jester", "image": "monsters/undead_jester.png", "ability": "bad_joke"},
            9: {"name": "Animated Armour", "image": "monsters/animated_armour.png", "ability": "block_first_attack"},
            10: {"name": "Skull Sentinel", "image": "monsters/skull_sentinel.png", "ability": None},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Banshee", "image": "monsters/banshee.png", "ability": "wail"},
            12: {"name": "Mad Mage", "image": "monsters/mad_mage.png", "ability": "spell_reflection"},
            13: {"name": "Crucible Knight", "image": "monsters/crucible_knight.png", "ability": "counter_attack"},
            14: {"name": "Anubis", "image": "monsters/anubis.png", "ability": "judgment"},
        },
        "clubs": {
            # Lower values (3-5): Easy monsters
            3: {"name": "Floating Eyes", "image": "monsters/floating_eyes.png", "ability": "confusion"},
            4: {"name": "Mr Gun", "image": "monsters/dave_the_gun_thing.png", "ability": "ranged_attack"},
            5: {"name": "Wraith", "image": "monsters/wraith.png", "ability": "life_drain"},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Genie", "image": "monsters/genie.png", "ability": "wish_twist"},
            7: {"name": "Fire Spirit", "image": "monsters/fire_spirit.png", "ability": "burning_attack"},
            8: {"name": "Chaos Demon", "image": "monsters/chaos_demon.png", "ability": "randomize"},
            9: {"name": "Demon Shaman", "image": "monsters/demon_shaman.png", "ability": "curse"},
            10: {"name": "Hag", "image": "monsters/hag.png", "ability": "curse"},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Beholder", "image": "monsters/beholder.png", "ability": "magic_attacks"},
            12: {"name": "Fallen Angel", "image": "monsters/fallen_angel.png", "ability": "holy_resistance"},
            13: {"name": "Mad Mage", "image": "monsters/mad_mage.png", "ability": "spell_reflection"},
            14: {"name": "Lightning God", "image": "monsters/lightning_god.png", "ability": "chain_lightning"},
        },
    },
    
    "crypt": {
        "spades": {
            # Lower values (3-5): Easy monsters
            3: {"name": "Skeleton", "image": "monsters/skeleton.png", "ability": None},
            4: {"name": "Zombie", "image": "monsters/zombie.png", "ability": "poison"},
            5: {"name": "Ghost", "image": "monsters/ghost.png", "ability": "phase_shift"},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Ghoul", "image": "monsters/ghoul.png", "ability": None},
            7: {"name": "Ghoul Leader", "image": "monsters/ghoul_leader.png", "ability": "summon_ghouls"},
            8: {"name": "Merchant Ghoul", "image": "monsters/merchant_ghoul.png", "ability": "gold_theft"},
            9: {"name": "Wraith", "image": "monsters/wraith.png", "ability": "life_drain"},
            10: {"name": "Skull Sentinel", "image": "monsters/skull_sentinel.png", "ability": None},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Banshee", "image": "monsters/banshee.png", "ability": "wail"},
            12: {"name": "Reaper", "image": "monsters/reaper.png", "ability": "fear"},
            13: {"name": "Demon Shaman", "image": "monsters/demon_shaman.png", "ability": "curse"},
            14: {"name": "Chaos Demon", "image": "monsters/chaos_demon.png", "ability": "randomize"},
        },
        "clubs": {
            # Lower values (3-5): Easy monsters
            3: {"name": "Skeleton", "image": "monsters/skeleton.png", "ability": None},
            4: {"name": "Zombie", "image": "monsters/zombie.png", "ability": "poison"},
            5: {"name": "Ghost", "image": "monsters/ghost.png", "ability": "phase_shift"},
            # Mid values (6-10): Medium difficulty 
            6: {"name": "Evil Ooze", "image": "monsters/evil_ooze.png", "ability": "split"},
            7: {"name": "Undead Jester", "image": "monsters/undead_jester.png", "ability": "bad_joke"},
            8: {"name": "Crucible Knight", "image": "monsters/crucible_knight.png", "ability": "counter_attack"},
            9: {"name": "Animated Armour", "image": "monsters/animated_armour.png", "ability": "block_first_attack"},
            10: {"name": "Amenite", "image": "monsters/amenite.png", "ability": "entomb"},
            # Face cards and Aces (11-14): Hard monsters
            11: {"name": "Hag", "image": "monsters/hag.png", "ability": "curse"},
            12: {"name": "Stone Golem", "image": "monsters/stone_golem.png", "ability": "reduced_damage"},
            13: {"name": "Fire Knight", "image": "monsters/fire_knight.png", "ability": "burning_attack"},
            14: {"name": "Mad Mage", "image": "monsters/mad_mage.png", "ability": "spell_reflection"},
        },
    },
    
    "MOLTEN": {
        "spades": {
            # Lower values (4-5): Easy monsters
            4: {"name": "Fire Spirit", "image": "monsters/fire_spirit.png", "ability": "burning_attack"},
            5: {"name": "Floating Eyes", "image": "monsters/floating_eyes.png", "ability": "confusion"},
            # Mid values (6-10): Medium difficulty
            6: {"name": "Evil Sun", "image": "monsters/evil_sun.png", "ability": "solar_flare"},
            7: {"name": "Giant Hornet", "image": "monsters/giant_hornet.png", "ability": "poison"},
            8: {"name": "Lizard Soldier", "image": "monsters/lizard_soldier.png", "ability": None},
            9: {"name": "Fire Knight", "image": "monsters/fire_knight.png", "ability": "burning_attack"},
            10: {"name": "Crucible Knight", "image": "monsters/crucible_knight.png", "ability": "counter_attack"},
            # Face cards (11-13): Hard monsters
            11: {"name": "Lizard King", "image": "monsters/lizard_king.png", "ability": "royal_command"},
            12: {"name": "Wyrm", "image": "monsters/wyrm.png", "ability": "fire_breath"},
            13: {"name": "Ancient Wyrm", "image": "monsters/ancient_wyrm.png", "ability": "lava_pool"},
            # Face cards and Aces (14): Hard monsters
            14: {"name": "Demon King", "image": "monsters/demon_king.png", "ability": "summon_minions"},
        },
        "clubs": {
            # Lower values (4-5): Easy monsters
            4: {"name": "Chaos Demon", "image": "monsters/chaos_demon.png", "ability": "randomize"},
            5: {"name": "Demon Shaman", "image": "monsters/demon_shaman.png", "ability": "curse"},
            # Mid values (6-10): Medium difficulty 
            6: {"name": "Dark Squid", "image": "monsters/dark_squid.png", "ability": "ink_spray"},
            7: {"name": "Python", "image": "monsters/python.png", "ability": "constriction"},
            8: {"name": "Sea Serpent", "image": "monsters/sea_serpent.png", "ability": "tidal_wave"},
            9: {"name": "Stone Golem", "image": "monsters/stone_golem.png", "ability": "reduced_damage"},
            10: {"name": "Troll", "image": "monsters/troll.png", "ability": "regeneration"},
            # Face cards (11-14): Hard monsters
            11: {"name": "Cyclops", "image": "monsters/cyclops.png", "ability": "stun_attack"},
            12: {"name": "Fallen Angel", "image": "monsters/fallen_angel.png", "ability": "holy_resistance"},
            13: {"name": "Beholder", "image": "monsters/beholder.png", "ability": "magic_attacks"},
            14: {"name": "Reaper", "image": "monsters/reaper.png", "ability": "fear"},
        },
    },
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

