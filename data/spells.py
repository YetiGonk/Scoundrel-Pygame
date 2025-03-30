# Spell data for scoundrel: Spells must be instantaneous effects that provide immediate benefits or effects but do not modify existing effects or provide new effects that are always active while the spell is in effect. Spells must also have a memory point cost associated with them, which is the number of rooms that spell can remain in memory before it is forgotten.

[
    {
        "name": "Healing Word",
        "description": "Restores 3 health points when cast",
        "rarity": "common",
        "memory_points": 5,
        "effect": "heal_player",
        "icon": "spell_green.png"
    },
    {
        "name": "Scrying",
        "description": "Reveals the contents of the next room",
        "rarity": "uncommon",
        "memory_points": 5,
        "effect": "reveal_next_room",
        "icon": "spell_blue.png"
    },
    {
        "name": "Mending",
        "description": "Removes all defeated monsters from your current weapon",
        "rarity": "uncommon",
        "memory_points": 5,
        "effect": "remove_defeated_monsters",
        "icon": "spell_yellow.png"
    },
    {
        "name": "Polymorph",
        "description": "Lowers a monster's value to 2",
        "rarity": "uncommon",
        "memory_points": 5,
        "effect": "protect_from_damage",
        "icon": "spell_purple.png"
    },
    {
        "name": "Fireball",
        "description": "Destroy 3 random cards in the room",
        "rarity": "rare",
        "memory_points": 5,
        "effect": "destroy_cards",
        "icon": "spell_fire.png"
    },
    {
        "name": "Transmutation",
        "description": "Sacrifice 5 health and turn it into 15 gold",
        "rarity": "rare",
        "memory_points": 5,
        "effect": "add_gold",
        "icon": "spell_yellow.png"
    }
]