import math
import os
import pygame
from pygame.locals import *
import random

from config import *
from core.game_state import GameState
from core.resource_loader import ResourceLoader

from ui.button import Button
from ui.panel import Panel

class TitleState(GameState):
    """The atmospheric title screen state of the game."""

    def __init__(self, game_manager):
        super().__init__(game_manager)

        self.title_font = None
        self.subtitle_font = None
        self.body_font = None

        self.background = None
        self.floor = None
        self.title_panel = None
        self.start_button = None
        self.tutorial_button = None
        self.rules_button = None

        self.particles = []
        self.torches = []
        self.torch_anim = None
        self.torch_anim_indexes = (0, 0)
        self.torch_lights = []
        self.title_glow = 0
        self.title_glow_dir = 1

        self.cards = []
        self.card_images = {}
        self.monster_imgs = []
        self.weapon_imgs = []
        self.potion_imgs = []

        self.title_clicks = 0
        self.last_click_count = 0
        self.last_tagline_index = -1
        self.seen_taglines = set()

    def enter(self):

        if not self.game_manager.floor_manager.floors:
            self.game_manager.floor_manager.initialise_run()

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 72)
        self.subtitle_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)

        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.torch_anim = [pygame.transform.scale(ResourceLoader.load_image(f"torch_anim/torch_{i}.png"),(128,128)) for i in range(5)]

        self.torch_anim_indexes = random.sample(range(5), 2)
        self.torches = [self.torch_anim[i] for i in self.torch_anim_indexes]

        floor_image = "floor.png"
        self.floor = ResourceLoader.load_image(floor_image)
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

        panel_width = 730
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        self.title_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 30),
            alpha=230,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=(120, 100, 80)
        )

        button_width = 300
        button_height = 60
        button_spacing = 10
        buttons_y = panel_y + panel_height - button_height*3 - button_spacing*2 - 25

        start_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y,
            button_width,
            button_height
        )
        self.start_button = Button(
            start_button_rect,
            "START ADVENTURE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 30, 30),
            border_colour=(150, 70, 70)
        )

        tutorial_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing),
            button_width,
            button_height
        )
        self.tutorial_button = Button(
            tutorial_button_rect,
            "WATCH TUTORIAL",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(30, 60, 30),
            border_colour=(70, 150, 70)
        )

        rules_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + (button_height + button_spacing)*2,
            button_width,
            button_height
        )
        self.rules_button = Button(
            rules_button_rect,
            "GAME RULES",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(30, 30, 60),
            border_colour=(70, 70, 150)
        )

        self._create_torch_lights()

        self._load_card_images()
        self._create_animated_cards()

    def _create_torch_lights(self):
        """Create torch light effects around the title screen"""
        self.torch_lights = []

        self.torch_lights.append({
            'x': SCREEN_WIDTH * 0.1,
            'y': SCREEN_HEIGHT // 2 - 40,
            'radius': 80,
            'flicker': 0,
            'flicker_speed': random.uniform(0.1, 0.2),
            'colour': (255, 150, 50)
        })

        self.torch_lights.append({
            'x': SCREEN_WIDTH * 0.9,
            'y': SCREEN_HEIGHT // 2 - 40,
            'radius': 80,
            'flicker': random.uniform(0, 2 * math.pi),
            'flicker_speed': random.uniform(0.1, 0.2),
            'colour': (255, 150, 50)
        })

    def _load_card_images(self):
        """Load a selection of card images for visual effect"""
        self.card_images = {}

        for monster_class in os.listdir(relative_to_assets("monsters")):
            for monster_name in os.listdir(os.path.join(relative_to_assets("monsters"), monster_class)):
                self.monster_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("monsters"), monster_class, monster_name), cache=False))
        for weapon_name in os.listdir(relative_to_assets("weapons")):
            self.weapon_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("weapons"), weapon_name), cache=False))
        for potion_name in os.listdir(relative_to_assets("potions")):
            self.potion_imgs.append(ResourceLoader.load_image(os.path.join(relative_to_assets("potions"), potion_name), cache=False))

        for value in range(2, 15):
            key = f"spades_{value}"
            black_card_surf = ResourceLoader.load_image(f"cards/spades_{value}.png")
            self.card_images[key] = self.add_monster_card(black_card_surf, value)

        for value in range(2, 11):
            key = f"diamonds_{value}"
            weapon_card_surf = ResourceLoader.load_image(f"cards/diamonds_{value}.png")
            self.card_images[key] = self.add_weapon_card(weapon_card_surf, value)

        for value in range(2, 11):
            key = f"hearts_{value}"
            potion_card_surf = ResourceLoader.load_image(f"cards/hearts_{value}.png")
            self.card_images[key] = self.add_potion_card(potion_card_surf, value)

        self.card_images["card_back"] = ResourceLoader.load_image("cards/card_back.png")

    def add_monster_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        monster_img = random.choice(self.monster_imgs)
        monster_size = 96
        monster_img = pygame.transform.scale(monster_img, (monster_size, monster_size))
        monster_surface = pygame.Surface((monster_size, monster_size), pygame.SRCALPHA)
        monster_surface.blit(monster_img, (0, 0))

        monster_pos = ((card_width - monster_size) // 2, (card_height - monster_size) // 2)
        new_surface.blit(monster_surface, monster_pos)

        return new_surface

    def add_weapon_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        weapon_img = random.choice(self.weapon_imgs)
        weapon_size = 96
        weapon_img = pygame.transform.scale(weapon_img, (weapon_size, weapon_size))
        weapon_surface = pygame.Surface((weapon_size, weapon_size), pygame.SRCALPHA)
        weapon_surface.blit(weapon_img, (0, 0))

        weapon_pos = ((card_width - weapon_size) // 2, (card_height - weapon_size) // 2)
        new_surface.blit(weapon_surface, weapon_pos)

        return new_surface

    def add_potion_card(self, card_surf, value):
        card_width, card_height = card_surf.get_width(), card_surf.get_height()
        new_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        new_surface.blit(card_surf, (0, 0))

        potion_img = random.choice(self.potion_imgs)
        potion_size = 96
        potion_img = pygame.transform.scale(potion_img, (potion_size, potion_size))
        potion_surface = pygame.Surface((potion_size, potion_size), pygame.SRCALPHA)
        potion_surface.blit(potion_img, (0, 0))

        potion_pos = ((card_width - potion_size) // 2, (card_height - potion_size) // 2)
        new_surface.blit(potion_surface, potion_pos)

        return new_surface

    def _create_animated_cards(self, num_cards=8):
        """Create animated cards that float around the title screen"""

        if len(self.cards) == 0:
            self.cards = []
            card_count = num_cards
        else:

            card_count = 1

        for _ in range(card_count):
            card_keys = list(self.card_images.keys())
            card_key = random.choice(card_keys)

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.2, 0.5)

            if random.random() < 0.5:

                x = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                y = random.uniform(100, SCREEN_HEIGHT - 100)
            else:

                x = random.uniform(100, SCREEN_WIDTH - 100)
                y = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100

            self.cards.append({
                'image': self.card_images[card_key],
                'x': x,
                'y': y,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-0.5, 0.5),
                'scale': random.uniform(0.7, 1.0),
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'shown': False,
                'flip_progress': 0,
                'flip_speed': random.uniform(0.02, 0.04),
                'flip_direction': 1,
                'front_image': self.card_images[card_key],
                'back_image': self.card_images["card_back"],
                'dragging': False,
                'drag_offset_x': 0,
                'drag_offset_y': 0,
                'z_index': random.random(),
                'hover': False
            })

    def _add_particle(self, x, y, colour=(255, 215, 0)):
        """Add a particle effect at the specified position"""
        self.particles.append({
            'x': x,
            'y': y,
            'colour': colour,
            'size': random.uniform(1, 3),
            'life': 1.0,
            'decay': random.uniform(0.005, 0.02),
            'dx': random.uniform(-0.7, 0.7),
            'dy': random.uniform(-0.7, 0.7)
        })

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.start_button.check_hover(mouse_pos)
            self.rules_button.check_hover(mouse_pos)

            card_clicked = False

            sorted_cards = sorted(self.cards, key=lambda card: card['z_index'], reverse=True)

            for card in sorted_cards:

                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )

                expanded_rect = card_rect.inflate(20, 20)

                if expanded_rect.collidepoint(mouse_pos):

                    card['dragging'] = True
                    card['drag_offset_x'] = card['x'] - mouse_pos[0]
                    card['drag_offset_y'] = card['y'] - mouse_pos[1]

                    card['z_index'] = max([c['z_index'] for c in self.cards]) + 0.1

                    if not card['shown']:
                        card['flip_direction'] = 1

                    card_clicked = True
                    break

            if not card_clicked:
                if self.start_button.is_clicked(mouse_pos):
                    if not hasattr(self.game_manager, 'has_shown_tutorial') or not self.game_manager.has_shown_tutorial:
                        self.game_manager.has_shown_tutorial = True
                        self.game_manager.change_state("tutorial")
                    else:
                        self.game_manager.change_state("playing")
                elif self.tutorial_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("tutorial_watch")
                elif self.rules_button.is_clicked(mouse_pos):
                    self.game_manager.change_state("rules")

                title_rect = pygame.Rect(
                    (SCREEN_WIDTH - 600) // 2,
                    self.title_panel.rect.top + 40,
                    600,
                    150
                )
                if title_rect.collidepoint(mouse_pos):
                    self.title_clicks += 1

                    for _ in range(10):
                        self._add_particle(mouse_pos[0], mouse_pos[1], (255, 200, 50))

        elif event.type == MOUSEBUTTONUP and event.button == 1:

            for card in self.cards:
                if card['dragging']:
                    card['dragging'] = False

                    speed_factor = 0.2
                    card['dx'] = random.uniform(-0.5, 0.5) * speed_factor
                    card['dy'] = random.uniform(-0.5, 0.5) * speed_factor

        elif event.type == MOUSEMOTION:

            for card in self.cards:
                if card['dragging']:
                    card['x'] = mouse_pos[0] + card['drag_offset_x']
                    card['y'] = mouse_pos[1] + card['drag_offset_y']

                    card['dx'] = 0
                    card['dy'] = 0

            for card in self.cards:

                card_width = card['image'].get_width() * card['scale']
                card_height = card['image'].get_height() * card['scale']
                card_rect = pygame.Rect(
                    card['x'] - card_width//2,
                    card['y'] - card_height//2,
                    card_width,
                    card_height
                )

                expanded_rect = card_rect.inflate(20, 20)
                card['hover'] = expanded_rect.collidepoint(mouse_pos)

        card_under_cursor = any(card['hover'] for card in self.cards)
        if not card_under_cursor:
            self.start_button.check_hover(mouse_pos)
            self.tutorial_button.check_hover(mouse_pos)
            self.rules_button.check_hover(mouse_pos)
        else:
            self.start_button.hovered = False
            self.tutorial_button.hovered = False
            self.rules_button.hovered = False

    def _update_particles(self, delta_time):
        """Update the particle effects"""

        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= particle['decay']

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def _update_torches(self, delta_time):
        """Update the torch animation by cycling through frame indexes at a steady speed"""
        for i, torch in enumerate(self.torches):
            self.torch_anim_indexes[i] += delta_time * 4
            self.torches[i] = self.torch_anim[int(self.torch_anim_indexes[i]) % len(self.torch_anim)]

    def _update_torch_lights(self, delta_time):
        """Update the torch light effects"""
        for torch in self.torch_lights:
            torch['flicker'] += torch['flicker_speed']

            if random.random() < 0.1:
                ember_x = torch['x'] + random.uniform(-5, 5)
                ember_y = torch['y'] + random.uniform(-5, 5)
                ember_colour = (
                    min(255, torch['colour'][0] + random.randint(-20, 20)),
                    min(255, torch['colour'][1] + random.randint(-30, 10)),
                    min(255, torch['colour'][2] + random.randint(-20, 10))
                )
                self._add_particle(ember_x, ember_y, ember_colour)

    def _update_cards(self, delta_time):
        """Update the animated cards"""

        for card in self.cards:

            if card['dragging']:
                continue

            card['x'] += card['dx']
            card['y'] += card['dy']

            if card['hover']:
                card['rotation'] += card['rot_speed'] * 0.3
            else:
                card['rotation'] += card['rot_speed']

            if card['flip_progress'] < 1 and card['flip_direction'] > 0:
                card['flip_progress'] += card['flip_speed']
                if card['flip_progress'] >= 1:
                    card['flip_progress'] = 1
                    card['shown'] = True
            elif card['flip_progress'] > 0 and card['flip_direction'] < 0:
                card['flip_progress'] -= card['flip_speed']
                if card['flip_progress'] <= 0:
                    card['flip_progress'] = 0
                    card['shown'] = False

            if (card['x'] < -150 or card['x'] > SCREEN_WIDTH + 150 or
                card['y'] < -150 or card['y'] > SCREEN_HEIGHT + 150):

                if random.random() < 0.5:

                    card['x'] = -100 if random.random() < 0.5 else SCREEN_WIDTH + 100
                    card['y'] = random.uniform(100, SCREEN_HEIGHT - 100)
                else:

                    card['x'] = random.uniform(100, SCREEN_WIDTH - 100)
                    card['y'] = -100 if random.random() < 0.5 else SCREEN_HEIGHT + 100

                card['shown'] = False
                card['flip_progress'] = 0

                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 0.5)
                card['dx'] = math.cos(angle) * speed
                card['dy'] = math.sin(angle) * speed

                card['rot_speed'] = random.uniform(-0.5, 0.5)

                card_keys = list(self.card_images.keys())
                card_key = random.choice(card_keys[:-1])
                card['front_image'] = self.card_images[card_key]

            if (100 < card['x'] < SCREEN_WIDTH - 100 and
                100 < card['y'] < SCREEN_HEIGHT - 100 and
                not card['shown'] and card['flip_progress'] == 0):
                card['flip_direction'] = 1

        if len(self.cards) < 8 and random.random() < 0.01:
            self._create_animated_cards()

    def update(self, delta_time):

        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.tutorial_button.check_hover(mouse_pos)
        self.rules_button.check_hover(mouse_pos)

        glow_speed = 0.5
        self.title_glow += glow_speed * self.title_glow_dir * delta_time
        if self.title_glow >= 1.0:
            self.title_glow = 1.0
            self.title_glow_dir = -1
        elif self.title_glow <= 0.0:
            self.title_glow = 0.0
            self.title_glow_dir = 1

        self._update_particles(delta_time)

        self._update_torches(delta_time)

        self._update_torch_lights(delta_time)

        self._update_cards(delta_time)

        if random.random() < 0.05:
            x = random.uniform(self.title_panel.rect.left + 50, self.title_panel.rect.right - 50)
            y = random.uniform(self.title_panel.rect.top + 50, self.title_panel.rect.bottom - 50)
            self._add_particle(x, y)

    def draw(self, surface):

        surface.blit(self.background, (0, 0))

        for i, torch in enumerate(self.torches):
            torch_rect = torch.get_rect(center=(SCREEN_WIDTH * (0.1 + 0.8*i), SCREEN_HEIGHT // 2))
            surface.blit(torch, torch_rect)

        for torch in self.torch_lights:

            glow_size = int(torch['radius'] * 2 * (1 + 0.1 * math.sin(torch['flicker'])))
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            for r in range(glow_size//2, 0, -1):
                alpha = max(0, int(90 * r / (glow_size//2) * (0.8 + 0.2 * math.sin(torch['flicker']))))
                pygame.draw.circle(
                    glow_surface,
                    (*torch['colour'], alpha),
                    (glow_size//2, glow_size//2),
                    r
                )

            glow_rect = glow_surface.get_rect(center=(torch['x'], torch['y']))
            surface.blit(glow_surface, glow_rect)

        floor_x = (SCREEN_WIDTH - self.floor.get_width()) // 2
        floor_y = (SCREEN_HEIGHT - self.floor.get_height()) // 2
        surface.blit(self.floor, (floor_x, floor_y))

        sorted_cards = sorted(self.cards, key=lambda card: card['z_index'])

        for card in sorted_cards:

            flip_width = int(card['image'].get_width() * card['scale'] * abs(math.cos(card['flip_progress'] * math.pi)))
            if flip_width < 1:
                flip_width = 1

            card_height = int(card['image'].get_height() * card['scale'])
            card_surface = pygame.Surface((flip_width, card_height), pygame.SRCALPHA)

            if card['flip_progress'] < 0.5:

                image = pygame.transform.scale(
                    card['back_image'],
                    (flip_width, card_height)
                )
            else:

                image = pygame.transform.scale(
                    card['front_image'],
                    (flip_width, card_height)
                )

            card_surface.blit(image, (0, 0))

            if card['hover'] or card['dragging']:

                highlight_rect = pygame.Rect(0, 0, flip_width, card_height)
                pygame.draw.rect(
                    card_surface,
                    (255, 215, 0) if card['dragging'] else (180, 180, 255),
                    highlight_rect,
                    width=3,
                    border_radius=3
                )

                if card['dragging'] and random.random() < 0.05:
                    self._add_particle(card['x'] + random.uniform(-20, 20),
                        card['y'] + random.uniform(-30, 30),
                        (255, 215, 0))

            rotated_card = pygame.transform.rotate(card_surface, card['rotation'])

            card_rect = rotated_card.get_rect(center=(card['x'], card['y']))
            surface.blit(rotated_card, card_rect)

        self.title_panel.draw(surface)

        glow_intensity = int(40 + 30 * self.title_glow)
        glow_colour = (255, 200, 50, glow_intensity)

        title_text = self.title_font.render("SCOUNDREL", True, WHITE)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.title_panel.rect.top + 50)

        glow_size = 15
        glow_surface = pygame.Surface((title_text.get_width() + glow_size*2, title_text.get_height() + glow_size*2), pygame.SRCALPHA)

        for r in range(glow_size, 0, -1):
            alpha = int(glow_colour[3] * r / glow_size)
            pygame.draw.rect(
                glow_surface,
                (*glow_colour[:3], alpha),
                pygame.Rect(glow_size-r, glow_size-r, title_text.get_width()+r*2, title_text.get_height()+r*2),
                border_radius=10
            )

        glow_rect = glow_surface.get_rect(center=title_rect.center)
        surface.blit(glow_surface, glow_rect)
        surface.blit(title_text, title_rect)

        subtitle_text = self.subtitle_font.render("The 52-Card Dungeon Crawler", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=title_rect.bottom + 40)
        surface.blit(subtitle_text, subtitle_rect)

        taglines = [
            "Navigate with cunning, defeat with paper cuts",
            "In darkened halls where cards may fall...",
            "Fortune favours the card counters",
            "Excitement!",
            "It's just a flesh wound!",
            "One more room couldn't hurt...",
            "What's in the cards for you, adventurer?",
            "Rooms of whimsy and peril!",
            "Dungeons and dragons and cards and counting!",
            "Kill it with a fire card!",
            "Crossbows are useless without bolts!",
            "Better lucky than good, better prepared than lucky",
            "Don't give up! Gambate! Fighto!",
            "[Insert sponsor here]",
            "The dungeon is a cruel mistress",
            "Insanity is expecting a different result from the same card",
            "Exodia!!!",
            "Read the rules if you're a chump!",
            "The real scoundrel was the friends we made along the way!",
            "r/scoundrelthegame",
            "Some treasures are worth the papercuts...",
            "52 card pickup!",
            "Another day, another dungeon...",
            "Shuffle up and deal with it!",
            "Gambling is illegal, but this is a dungeon!",
            "Flipping you off is a card game term!",
            "Original rules by Kurt Bieg and Zach Gage!",
            "You are not allowed a calculator on this exam",
            "Scoundrel this, scoundrel that",
            "You can drag the title cards around!",
            "Trust in the heart of the cards...",
            "When in doubt, run away!",
            "If only I were a scoundrel...",
            "This dungeon is definitely not up to code",
            "Terms and conditions apply to all card effects",
            "Don't bring a card to a sword fight!",
            "You fell for the classic blunder!",
            "You can't cheat death, but you can shuffle the deck",
            "A wise scoundrel knows when to hold 'em and when to fold 'em",
            "I believe in you... sort of",
            "I feel like we are connecting on a deeper level through this title screen...",
            "PyGame is a cruel mistress",
            "Scoundrel, shmoundrel!",
            "Scoundrel 2: Electric Boogaloo",
            "Sconedrel: Argue about how to pronounce it.",
            "SCOUNDRELLLLL!",
            "The sequel will be a dating sim.",
            "I slipped you a red 10 in there somewhere, thank me later <3",
            "Adventurer hires, merchants and gold coming soon!"
        ]

        if not hasattr(self, 'last_tagline_index'):
            self.last_tagline_index = -1

        if self.title_clicks > 0 and hasattr(self, 'last_click_count') and self.title_clicks > self.last_click_count:

            available_indices = [i for i in range(len(taglines)) if i != self.last_tagline_index]

            if len(self.seen_taglines) >= len(taglines) - 1:
                self.seen_taglines = {self.last_tagline_index}

            unseen_indices = [i for i in available_indices if i not in self.seen_taglines]
            seen_indices = [i for i in available_indices if i in self.seen_taglines]

            if unseen_indices and (not seen_indices or random.random() < 0.8):
                self.last_tagline_index = random.choice(unseen_indices)
            else:
                self.last_tagline_index = random.choice(seen_indices or available_indices)

            self.seen_taglines.add(self.last_tagline_index)

        self.last_click_count = self.title_clicks

        if self.title_clicks == 0:

            tagline = taglines[0]
        else:
            tagline = taglines[self.last_tagline_index]

        max_width = 600

        test_text = self.body_font.render(tagline, True, (200, 200, 200))

        if test_text.get_width() > max_width:

            words = tagline.split()
            total_words = len(words)
            middle_point = total_words // 2

            break_point = middle_point

            line1 = " ".join(words[:break_point])

            line2 = " ".join(words[break_point:])

            line1_text = self.body_font.render(line1, True, (200, 200, 200))
            line2_text = self.body_font.render(line2, True, (200, 200, 200))

            line1_rect = line1_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 15)
            line2_rect = line2_text.get_rect(centerx=SCREEN_WIDTH//2, top=line1_rect.bottom + 5)

            surface.blit(line1_text, line1_rect)
            surface.blit(line2_text, line2_rect)
        else:

            tagline_text = self.body_font.render(tagline, True, (200, 200, 200))
            tagline_rect = tagline_text.get_rect(centerx=SCREEN_WIDTH//2, top=subtitle_rect.bottom + 25)
            surface.blit(tagline_text, tagline_rect)

        self.start_button.draw(surface)
        self.tutorial_button.draw(surface)
        self.rules_button.draw(surface)

        for particle in self.particles:
            alpha = int(255 * particle['life'])
            particle_colour = (*particle['colour'], alpha)
            pygame.draw.circle(
                surface,
                particle_colour,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )