""" Constants for the roguelike elements of Scoundrel. """
import random

# Floor definitions
FLOOR_TYPES = ["dungeon", "forest", "library", "crypt", "volcano"]

# Floor structure
FLOOR_STRUCTURE = {
    "rooms_per_floor": 12,  # Maximum potential rooms (flexible)
    "merchant_rooms": [1, 8],  # Room numbers where merchants appear
    # Boss room functionality removed
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
    "gold": 0,
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

# Boss cards removed

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
    
    "volcano": {
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

# Monster abilities and their effects
MONSTER_ABILITIES = {
    "block_first_attack": "Negates the first weapon attack",
    "reduced_damage": "Takes 50% less damage from weapons",
    "poison": "Deals 1 damage per turn for 3 turns",
    "phase_shift": "50% chance to avoid weapon attacks",
    "life_drain": "Heals for 50% of damage dealt",
    "regeneration": "Regains 2 health each turn",
    "burning_attack": "Deals additional 2 fire damage",
    "magic_attacks": "Ignores weapon defence bonuses",
    "summon_minions": "Summons 1-3 weaker monsters",
    "split": "Creates a copy of itself at 50% health when damaged",
    "confusion": "50% chance player attacks themselves",
    "constriction": "Damage increases each turn",
    "counter_attack": "Deals damage back to player on attack",
    "stun_attack": "50% chance to stun player for 1 turn",
    "fear": "Reduces player's attack strength by 2",
    "spell_reflection": "Reflects magical attacks back to player",
    "holy_resistance": "Immune to holy/light damage types",
    "entangle": "Prevents player from running for 2 turns",
    "web_trap": "Slows player movement, reduced dodge chance",
    "dive_attack": "First attack deals double damage",
    "curse": "Reduces player's max health by 1",
    "root_attack": "Prevents player from running",
    "crushing_blow": "25% chance to break equipped weapon",
    "spawn_spiders": "Spawns 1-4 spider minions",
    "nature_magic": "Heals from potion attacks",
    "charge": "First attack stuns player for 1 turn",
    "toxicity": "All attacks are poisoned",
    "poison_cloud": "Damages all characters in room",
    "bad_joke": "Makes player unable to use items for 1 turn",
    "summon_ghouls": "Summons 1-2 ghouls as allies",
    "royal_command": "Strengthens all other monsters in room",
    "petrify": "25% chance to disable player for 2 turns",
    "deadly_constriction": "Damage doubles each turn",
    "knowledge_drain": "Reduces spell effectiveness",
    "astral_projection": "Can attack from a distance",
    "lunar_magic": "Stronger during night cycles",
    "solar_flare": "Area attack that damages player and all equipment",
    "wail": "50% chance to cause fear effect",
    "judgment": "Damage based on player's actions in run",
    "reality_warp": "Randomizes effects of all items and spells",
    "ranged_attack": "Can attack from a distance",
    "wish_twist": "Grants a random effect (positive or negative)",
    "chain_lightning": "Damages player and destroys one random item",
    "gold_theft": "Steals 5-15 gold from player",
    "entomb": "Traps player for 2 turns",
    "fire_breath": "Area attack with fire damage",
    "lava_pool": "Creates hazard that damages player each turn",
    "devastating_breath": "Massive damage attack with 1 turn charge-up",
    "magma_eruption": "Area attack that persists for 3 turns",
    "ink_spray": "Blinds player, reducing hit chance by 75%",
    "tidal_wave": "Pushes back all characters and applies wet effect"
}

WEAPON_MAPPINGS = {
    2: "arrow",
    3: "arrow",
    4: "shield",
    5: "axe",
    6: "warhammer",
    7: "flail",
    8: "shortsword",
    9: "greatsword",
    10: "shortsword",
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

