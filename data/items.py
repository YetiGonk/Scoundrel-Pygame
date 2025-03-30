# Item data for scoundrel: Items must represent non-consumable passive effects that do not provide instantaneous benefits or effects but instead either modify an existing effect or provide a new effect that is always active while the item is equipped. Some items may also have a durability value which indicates the number of times that item's passive effect can be triggered by the game before it is destroyed. Items must also have an icon associated with them, which is the image that represents the item in the game. Items without durability are listed as having a value of None.

[
    {
        "name": "Ring of Rejuvenation",
        "description": "Restores 2 extra health points when healing",
        "type": "active",
        "rarity": "common",
        "durability": 10,
        "effect": "heal_player",
        "icon": "red_ring.png"
    },
    {
        "name": "Bronze Greatshield",
        "description": "Absorbs up to 2 damage whenever you take damage.",
        "type": "active",
        "rarity": "common",
        "durability": 10,
        "effect": "protect_from_damage",
        "icon": "greatshield_bronze.png"
    },
    {
        "name": "Dragon Scalemail",
        "description": "While equipped, increases max health by 5",
        "type": "active",
        "rarity": "rare",
        "durability": None,
        "effect": "increase_max_health",
        "icon": "scale_red.png"
    },
    {
        "name": "Gold Skull",
        "description": "Gain 1 gold whenever you defeat a monster.",
        "type": "active",
        "rarity": "common",
        "durability": None,
        "effect": "add_gold",
        "icon": "gold_skull.png"
    }
]