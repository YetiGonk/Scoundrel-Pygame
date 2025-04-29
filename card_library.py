"""
Card Library for Scoundrel game.
Contains information about all cards, their unlock status, quantities, rarities, and special abilities.
"""

# Rarity levels
COMMON = "common"
RARE = "rare"
EPIC = "epic"
RELIC = "relic"

# Hireable types
ARCHER = "archer"
BARD = "bard"
BERSERKER = "berserker"
MINER = "miner"
PRISONER = "prisoner"
THIEF = "thief"
BLACKSMITH = "blacksmith"
CLOWN = "clown"
DRUID = "druid"
MAGICIAN = "magician"
NUN = "nun"
TAMER = "tamer"
FIGHTER = "fighter"
MERCHANT = "merchant"
NECROMANCER = "necromancer"
SAMURAI = "samurai"
SHOOTER = "shooter"
WARRIOR = "warrior"

# Card structure in dictionary:
# {
#   "suit": suit of the card (diamonds, hearts, spades, clubs, or wildcard)
#   "value": value of the card (2-14, where 11=J, 12=Q, 13=K, 14=A)
#   "unlocked": whether the card is unlocked by the player
#   "owned": how many the player owns
#   "rarity": rarity level (common, rare, epic, relic)
#   "hireable": whether it's a hireable face card
#   "hireable_type": if hireable, what type of hire (archer, bard, etc.)
#   "description": card description text
# }

CARD_LIBRARY = {
    # COMMON CARDS (18)
    # Diamonds 2-10
    "diamonds_2": {
        "suit": "diamonds",
        "value": 2,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 2"
    },
    "diamonds_3": {
        "suit": "diamonds",
        "value": 3,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 3"
    },
    "diamonds_4": {
        "suit": "diamonds",
        "value": 4,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 4"
    },
    "diamonds_5": {
        "suit": "diamonds",
        "value": 5,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 5"
    },
    "diamonds_6": {
        "suit": "diamonds",
        "value": 6,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 6"
    },
    "diamonds_7": {
        "suit": "diamonds",
        "value": 7,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 7"
    },
    "diamonds_8": {
        "suit": "diamonds",
        "value": 8,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 8"
    },
    "diamonds_9": {
        "suit": "diamonds",
        "value": 9,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 9"
    },
    "diamonds_10": {
        "suit": "diamonds",
        "value": 10,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Weapon value 10"
    },
    
    # Hearts 2-10
    "hearts_2": {
        "suit": "hearts",
        "value": 2,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 2 health"
    },
    "hearts_3": {
        "suit": "hearts",
        "value": 3,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 3 health"
    },
    "hearts_4": {
        "suit": "hearts",
        "value": 4,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 4 health"
    },
    "hearts_5": {
        "suit": "hearts",
        "value": 5,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 5 health"
    },
    "hearts_6": {
        "suit": "hearts",
        "value": 6,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 6 health"
    },
    "hearts_7": {
        "suit": "hearts",
        "value": 7,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 7 health"
    },
    "hearts_8": {
        "suit": "hearts",
        "value": 8,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 8 health"
    },
    "hearts_9": {
        "suit": "hearts",
        "value": 9,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 9 health"
    },
    "hearts_10": {
        "suit": "hearts",
        "value": 10,
        "unlocked": True,
        "owned": 1,
        "rarity": COMMON,
        "hireable": False,
        "hireable_type": None,
        "description": "Heals 10 health"
    },
    
    # RARE CARDS (15)
    # Wildcards 2-10
    "wildcard_2": {
        "suit": "wildcard",
        "value": 2,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 2"
    },
    "wildcard_3": {
        "suit": "wildcard",
        "value": 3,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 3"
    },
    "wildcard_4": {
        "suit": "wildcard",
        "value": 4,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 4"
    },
    "wildcard_5": {
        "suit": "wildcard",
        "value": 5,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 5"
    },
    "wildcard_6": {
        "suit": "wildcard",
        "value": 6,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 6"
    },
    "wildcard_7": {
        "suit": "wildcard",
        "value": 7,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 7"
    },
    "wildcard_8": {
        "suit": "wildcard",
        "value": 8,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 8"
    },
    "wildcard_9": {
        "suit": "wildcard",
        "value": 9,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 9"
    },
    "wildcard_10": {
        "suit": "wildcard",
        "value": 10,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond or heart card of value 10"
    },
    
    # Jack Hires
    "hires_11_archer": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": ARCHER,
        "description": "When activated, strikes a monster in the room reducing its value by 3."
    },
    "hires_11_berserker": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": BERSERKER,
        "description": "When activated, doubles your current weapon's value up to ace (14) for your next monster battle, but you must attack a monster immediately after using this hire. If the next card you interact with isn't a monster card, the weapon reverts back to its original value. If it is a monster card, the card will remain doubled until discarded."
    },
    "hires_11_prisoner": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": PRISONER,
        "description": "When activated, sacrifices 2 health to discard a selected monster card from the current room and place it at the bottom of the floor deck."
    },
    "hires_11_bard": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": BARD,
        "description": "When activated, reveals one random room in the dungeon (4 cards) and allows you to swap one card from your current room with any card from the revealed room."
    },
    "hires_11_miner": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": MINER,
        "description": "When activated, searches the dungeon deck and retrieves one diamond weapon card with value 5 or lower to add to your inventory."
    },
    "hires_11_thief": {
        "suit": "hires",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": RARE,
        "hireable": True,
        "hireable_type": THIEF,
        "description": "When activated, scouts out the dungeon and shows the player the next 3 cards in the deck."
    },
    
    # EPIC CARDS (8)
    # Wildcard Jack
    "wildcard_11": {
        "suit": "wildcard",
        "value": 11,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond weapon or heart potion card of value 11."
    },
    
    # Wildcard Queen
    "wildcard_12": {
        "suit": "wildcard",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as a diamond weapon or heart potion card of value 12."
    },
    
    # Queen Hires
    "hires_12_blacksmith": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": BLACKSMITH,
        "description": "When activated, enhances your currently equipped weapon by +5 value up to ace (14). If you have no weapon equipped, crafts and equips a diamond 7 weapon for you."
    },
    "hires_12_magician": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": MAGICIAN,
        "description": "When activated, the magician lets you choose one card from the room to duplicate. The duplicate is added to your inventory if it's a diamond or heart. If it's a monster card, it is added to the room. If the room is already at full capacity (4) or your inventory is full, then the duplicate is discarded."
    },
    "hires_12_tamer": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": TAMER,
        "description": "When activated, tames one monster in the room, adding it to your inventory as a special weapon with value equal to the monster's value -2."
    },
    "hires_12_clown": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": CLOWN,
        "description": "When activated, shuffles all cards in the current room back into the dungeon deck and draws 4 new cards to replace them. You cannot run from the new room. You can run from the next room after this one."
    },
    "hires_12_druid": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": DRUID,
        "description": "When activated, transforms all heart cards in the room, increasing their value by 2 up to ace (14). If there are no heart cards, transforms the lowest value monster card in the room into a heart card of equal value."
    },
    "hires_12_nun": {
        "suit": "hires",
        "value": 12,
        "unlocked": False,
        "owned": 0,
        "rarity": EPIC,
        "hireable": True,
        "hireable_type": NUN,
        "description": "When activated, heals you for 5 health and cleanses your weapon, removing all monster cards stacked on it so you can defeat monsters of any value again."
    },
    
    # RELIC CARDS (7)
    # Wildcard King
    "wildcard_13": {
        "suit": "wildcard",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as any King hireable card"
    },
    
    # Wildcard Ace
    "wildcard_14": {
        "suit": "wildcard",
        "value": 14,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": False,
        "hireable_type": None,
        "description": "Can be used as any diamond or heart card of any value"
    },
    
    # King Hires
    "hires_13_fighter": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": FIGHTER,
        "description": "When activated, advances into the dungeon and destroys the next two monsters in the deck, regardless of their value."
    },
    "hires_13_samurai": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": SAMURAI,
        "description": "When activated, instantly defeats all monsters currently in the room without taking any damage, regardless of your weapon or their values."
    },
    "hires_13_shooter": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": SHOOTER,
        "description": "When activated, snipes the highest value monster card from each of the next 2 rooms and discards them."
    },
    "hires_13_merchant": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": MERCHANT,
        "description": "When activated, shuffles the discard pile and draws the top four red cards. The player can then purchase one card of the four. Hearts are free but heal only 3 health. Diamonds cost 3 health to purchase."
    },
    "hires_13_necromancer": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": NECROMANCER,
        "description": "When activated, necromancer uses undead magic to convert all monsters in the room into diamond cards of equal value."
    },
    "hires_13_warrior": {
        "suit": "hires",
        "value": 13,
        "unlocked": False,
        "owned": 0,
        "rarity": RELIC,
        "hireable": True,
        "hireable_type": WARRIOR,
        "description": "When activated, grants you temporary invulnerability, allowing you to defeat the next 4 monsters you encounter without taking any damage, regardless of their value or your weapon."
    }
}