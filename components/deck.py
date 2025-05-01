"""
Deck component for the Scoundrel game.
"""
import random
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_WIDTH, FLOOR_HEIGHT, GRAY, SUITS, DECK_POSITION
from utils.resource_loader import ResourceLoader

class Deck:
    """ Represents a deck of cards in the game. """
    
    def __init__(self, floor):
        # Default to dungeon if floor is None or not in DECK_DICT
        self.floor = None
        self.position = DECK_POSITION
        self.cards = []
        self.card_stack = []
        self.card_spacing = (0, 3)
        self.texture = ResourceLoader.load_image("cards/card_back.png")
        self.texture = pygame.transform.scale(self.texture, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = pygame.Rect(self.position[0], self.position[1], CARD_WIDTH, CARD_HEIGHT)

    def initialise_deck(self, player_deck=None):
        """Initialize the deck for a floor.
        
        This method creates a random deck for each floor, making every run more varied.
        Each floor deck follows these rules:
        - Always 44 cards total
        - Always between 16-24 monster cards (clubs/spades value 2-14)
        - Equal number of weapon (diamonds) and potion (hearts) cards (value 2-10)
        - No more than 4 duplicates of the same card type
        """
        self.cards = []
        
        # Generate a random deck for this floor
        self._generate_random_deck()
        
        # Add player's delving deck cards if provided
        if player_deck:
            for card_data in player_deck:
                self.cards.append(card_data)
                
        # Shuffle the combined deck
        random.shuffle(self.cards)
        self.initialise_visuals()
    
    def _generate_random_deck(self):
        """Generate a random deck following specific requirements:
        - 44 cards total
        - Weapons: 2-10 value range
        - Potions: 2-10 value range
        - Monsters: 2-14 value range
        - Between 16-24 monster cards
        - No more than 4 duplicates of the same card (suit/value)
        - Equal number of weapon and potion cards
        """
        # Step 1: Decide how many monster cards we'll have (16-24)
        monster_count = random.randint(16, 24)
        
        # Step 2: Calculate how many weapon/potion cards
        weapon_potion_count = 44 - monster_count
        # Ensure it's an even number since weapons and potions must be equal
        if weapon_potion_count % 2 != 0:
            weapon_potion_count -= 1
            monster_count += 1
            
        weapon_count = potion_count = weapon_potion_count // 2
        
        # Step 3: Start building the deck with tracking to prevent >4 duplicates
        card_counts = {}  # (suit, value) -> count
        
        # Add monsters (clubs and spades)
        self._add_cards_to_deck(["clubs", "spades"], range(2, 15), monster_count, card_counts)
        
        # Add weapons (diamonds)
        self._add_cards_to_deck(["diamonds"], range(2, 11), weapon_count, card_counts)
        
        # Add potions (hearts)
        self._add_cards_to_deck(["hearts"], range(2, 11), potion_count, card_counts)
    
    def _add_cards_to_deck(self, suits, value_range, count, card_counts):
        """Add cards to the deck while respecting the duplicate limit."""
        cards_added = 0
        
        # Try to add the required number of cards
        while cards_added < count:
            # Pick a random suit and value
            suit = random.choice(suits)
            value = random.choice(list(value_range))
            
            # Check if we've already reached the limit for this card
            card_key = (suit, value)
            current_count = card_counts.get(card_key, 0)
            
            if current_count < 4:  # Maximum 4 duplicates
                # Add this card to the deck
                self.cards.append({"suit": suit, "value": value, "floor_type": self.floor})
                
                # Update the count
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
        # Draw the deck
        if self.card_stack:
            for i, pos in enumerate(self.card_stack):
                surface.blit(self.texture, pos)
        else:
            # Draw an empty deck placeholder
            pygame.draw.rect(surface, GRAY, self.rect, 2)