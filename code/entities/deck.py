import pygame
import random


from config import *

from core.resource_loader import ResourceLoader

class Deck:
    """ Represents a deck of cards in the game. """

    def __init__(self, floor):

        self.floor = floor
        self.position = DECK_POSITION
        self.cards = []
        self.card_stack = []
        self.card_spacing = (0, 3)
        self.texture = ResourceLoader.load_image("cards/card_back.png")
        self.texture = pygame.transform.scale(self.texture, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def initialise_deck(self):
        """Initialise the deck for a floor."""
        self.cards = []

        self._generate_random_deck()

        random.shuffle(self.cards)
        self.initialise_visuals()

    def _generate_random_deck(self):
        """Generate a random deck"""
        monster_count = random.randint(DECK_MONSTER_COUNT[0], DECK_MONSTER_COUNT[1])

        weapon_potion_count = DECK_TOTAL_COUNT - monster_count

        if weapon_potion_count % 2 != 0:
            weapon_potion_count -= 1
            monster_count += 1

        weapon_count = potion_count = weapon_potion_count // 2

        card_counts = {}

        self._add_cards_to_deck(["clubs", "spades"], range(DECK_BLACK_VALUE_RANGE[0], DECK_BLACK_VALUE_RANGE[1] + 1), monster_count, card_counts)

        self._add_cards_to_deck(["diamonds"], range(DECK_DIAMONDS_VALUE_RANGE[0], DECK_DIAMONDS_VALUE_RANGE[1] + 1), weapon_count, card_counts)

        self._add_cards_to_deck(["hearts"], range(DECK_HEARTS_VALUE_RANGE[0], DECK_HEARTS_VALUE_RANGE[1] + 1), potion_count, card_counts)

    def _add_cards_to_deck(self, suits, value_range, count, card_counts):
        """Add cards to the deck while respecting the duplicate limit."""
        cards_added = 0

        while cards_added < count:

            suit = random.choice(suits)
            value = random.choice(list(value_range))

            card_key = (suit, value)
            current_count = card_counts.get(card_key, 0)

            if current_count < 4:

                self.cards.append({"suit": suit, "value": value, "floor_type": self.floor})

                card_counts[card_key] = current_count + 1
                cards_added += 1

    def initialise_visuals(self):
        self.card_stack = []
        for i in range(len(self.cards)):
            card_pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
            self.card_stack.append(card_pos)

    def draw_card(self):
        if self.cards:
            return self.cards.pop(0)
        return None

    def add_to_bottom(self, card_data):
        self.cards.append(card_data)

    def draw(self, surface):

        if self.card_stack:
            for i, pos in enumerate(self.card_stack):
                surface.blit(self.texture, pos)
        else:

            pygame.draw.rect(surface, GRAY, self.rect, 2)

class DiscardPile:
    """Represents a discard pile in the game."""

    def __init__(self):
        self.position = DISCARD_POSITION
        self.cards = []
        self.card_spacing = (0, -3)
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def add_card(self, card):
        self.cards.append(card)

    def get_card_count(self):
        return len(self.cards)

    def draw(self, surface):
        if self.cards:
            for i, card in enumerate(self.cards):
                pos = (self.position[0], self.position[1] + i * self.card_spacing[1])
                surface.blit(card.texture, pos)
        else:

            pygame.draw.rect(surface, GRAY, self.rect, 2)

def extract_weapons():

    output_dir = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/individual"
    os.makedirs(output_dir, exist_ok=True)

    dark_colour = (171, 82, 54)
    light_colour = (214, 123, 86)

    def process_weapon(source_img, x, y, width, height, index):

        weapon = source_img.crop((x, y, x + width, y + height))

        new_weapon = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for py in range(height):
            for px in range(width):

                pixel = weapon.getpixel((px, py))

                if (120 < pixel[0] < 160 and
                    100 < pixel[1] < 140 and
                    70 < pixel[2] < 110):
                    continue

                if (130 < pixel[0] < 170 and
                    110 < pixel[1] < 150 and
                    80 < pixel[2] < 120):
                    continue

                if len(pixel) == 4 and pixel[3] == 0:
                    continue

                brightness = sum(pixel[:3]) / 3

                if brightness > 180:
                    new_colour = light_colour
                else:
                    new_colour = dark_colour

                alpha = pixel[3] if len(pixel) == 4 else 255

                new_weapon.putpixel((px, py), (*new_colour, alpha))

        output_path = os.path.join(output_dir, f"weapon{index}.png")
        new_weapon.save(output_path)

    weapons1_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons1.png"
    weapons1 = Image.open(weapons1_path).convert("RGBA")

    for row in range(3):
        for col in range(3):
            index = row * 3 + col + 1
            process_weapon(weapons1, col * 32, row * 32, 32, 32, index)

    weapons2_path = "/Users/maximolopez/scoundrel/PyGame/assets/weapons/weapons2.jpg"
    weapons2 = Image.open(weapons2_path).convert("RGBA")

    weapon_positions = [
        (12, 11, 32, 32),
        (60, 10, 32, 32),
        (114, 10, 32, 32),
        (12, 58, 32, 32),
        (60, 58, 32, 32),
        (114, 58, 32, 32),
        (12, 106, 32, 32),
        (60, 106, 32, 32),
        (114, 106, 32, 32)
    ]

    for i, (x, y, w, h) in enumerate(weapon_positions):
        index = i + 10
        process_weapon(weapons2, x, y, w, h, index)
