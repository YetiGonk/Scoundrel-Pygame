"""
Card Library for Scoundrel game.
Contains information about all cards, their unlock status, quantities, rarities, and special abilities.
"""

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
#   "value": value of the card (11=J, 12=Q, 13=K)
#   "hireable_type": what type of hire (archer, bard, etc.)
#   "description": card description text
# }

HIRES_CARD_LIBRARY = {
    # Jack Hires
    "diamond_11_archer": {
        "suit": "hires",
        "value": 11,
        "hireable_type": ARCHER,
        "description": "When activated, strikes a monster in the room reducing its value by 3."
    },
    "diamond_11_berserker": {
        "suit": "hires",
        "value": 11,
        "hireable_type": BERSERKER,
        "description": "When activated, doubles your current weapon's value up to ace (14) for your next monster battle, but you must attack a monster immediately after using this hire. If the next card you interact with isn't a monster card, the weapon reverts back to its original value. If it is a monster card, the card will remain doubled until discarded."
    },
    "diamond_11_prisoner": {
        "suit": "hires",
        "value": 11,
        "hireable_type": PRISONER,
        "description": "When activated, sacrifices 2 health to discard a selected monster card from the current room and place it at the bottom of the floor deck."
    },
    "heart_11_bard": {
        "suit": "hires",
        "value": 11,
        "hireable_type": BARD,
        "description": "When activated, reveals one random room in the dungeon (4 cards) and allows you to swap one card from your current room with any card from the revealed room."
    },
    "heart_11_miner": {
        "suit": "hires",
        "value": 11,
        "hireable_type": MINER,
        "description": "When activated, searches the dungeon deck and retrieves one diamond weapon card with value 5 or lower to add to your inventory."
    },
    "hires_11_thief": {
        "suit": "hires",
        "value": 11,
        "hireable_type": THIEF,
        "description": "When activated, scouts out the dungeon and shows the player the next 3 cards in the deck."
    },
    
    # EPIC CARDS (8)
    # Wildcard Jack
    "wildcard_11": {
        "suit": "wildcard",
        "value": 11,
        "hireable_type": None,
        "description": "Can be used as a diamond weapon or heart potion card of value 11."
    },
    # Queen Hires
    "hires_12_blacksmith": {
        "suit": "hires",
        "value": 12,
        "hireable_type": BLACKSMITH,
        "description": "When activated, enhances your currently equipped weapon by +5 value up to ace (14). If you have no weapon equipped, crafts and equips a diamond 7 weapon for you."
    },
    "hires_12_magician": {
        "suit": "hires",
        "value": 12,
        "hireable_type": MAGICIAN,
        "description": "When activated, the magician lets you choose one card from the room to duplicate. The duplicate is added to your inventory if it's a diamond or heart. If it's a monster card, it is added to the room. If the room is already at full capacity (4) or your inventory is full, then the duplicate is discarded."
    },
    "hires_12_tamer": {
        "suit": "hires",
        "value": 12,
        "hireable_type": TAMER,
        "description": "When activated, tames one monster in the room, adding it to your inventory as a special weapon with value equal to the monster's value -2."
    },
    "hires_12_clown": {
        "suit": "hires",
        "value": 12,
        "hireable_type": CLOWN,
        "description": "When activated, shuffles all cards in the current room back into the dungeon deck and draws 4 new cards to replace them. You cannot run from the new room. You can run from the next room after this one."
    },
    "hires_12_druid": {
        "suit": "hires",
        "value": 12,
        "hireable_type": DRUID,
        "description": "When activated, transforms all heart cards in the room, increasing their value by 2 up to ace (14). If there are no heart cards, transforms the lowest value monster card in the room into a heart card of equal value."
    },
    "hires_12_nun": {
        "suit": "hires",
        "value": 12,
        "hireable_type": NUN,
        "description": "When activated, heals you for 5 health and cleanses your weapon, removing all monster cards stacked on it so you can defeat monsters of any value again."
    },
    # King Hires
    "hires_13_fighter": {
        "suit": "hires",
        "value": 13,
        "hireable_type": FIGHTER,
        "description": "When activated, advances into the dungeon and destroys the next two monsters in the deck, regardless of their value."
    },
    "hires_13_samurai": {
        "suit": "hires",
        "value": 13,
        "hireable_type": SAMURAI,
        "description": "When activated, instantly defeats all monsters currently in the room without taking any damage, regardless of your weapon or their values."
    },
    "hires_13_shooter": {
        "suit": "hires",
        "value": 13,
        "hireable_type": SHOOTER,
        "description": "When activated, snipes the highest value monster card from each of the next 2 rooms and discards them."
    },
    "hires_13_merchant": {
        "suit": "hires",
        "value": 13,
        "hireable_type": MERCHANT,
        "description": "When activated, shuffles the discard pile and draws the top four red cards. The player can then purchase one card of the four. Hearts are free but heal only 3 health. Diamonds cost 3 health to purchase."
    },
    "hires_13_necromancer": {
        "suit": "hires",
        "value": 13,
        "hireable_type": NECROMANCER,
        "description": "When activated, necromancer uses undead magic to convert all monsters in the room into diamond cards of equal value."
    },
    "hires_13_warrior": {
        "suit": "hires",
        "value": 13,
        "hireable_type": WARRIOR,
        "description": "When activated, grants you temporary invulnerability, allowing you to defeat the next 4 monsters you encounter without taking any damage, regardless of their value or your weapon."
    }
}