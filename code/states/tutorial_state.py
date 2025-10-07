class TutorialState(GameState):
    """Tutorial state with typing text, animated merchant, and demo UI."""
    
    def __init__(self, game_manager, watch=False):
        super().__init__(game_manager)
        self.header_font = None
        self.body_font = None
        self.name_font = None
        self.background = None
        self.floor = None
        
        self.watch = watch
        
        self.current_dialogue_index = 0
        self.dialogue_complete = False
        self.typing_complete = False
        
        self.current_text = ""
        self.target_text = ""
        self.char_index = 0
        self.typing_speed = 0.03  # seconds per character
        self.typing_timer = 0
        
        self.merchant_image = None
        self.merchant_shake_amount = 0
        self.merchant_base_pos = None
        
        self.dialogue_panel = None
        self.name_panel = None
        self.next_button = None
        self.skip_button = None
        
        self.dialogues = [
            {
                "speaker": "Mysterious Merchant",
                "graphic": None,
                "text": "Well, well, well... Another brave soul ventures into the depths of the dungeon!"
            },
            {
                "speaker": "Mysterious Merchant",
                "graphic": None,
                "text": "Welcome to the dungeon, adventurer! I am the Bartholomew, a merchant who trades in these dark halls."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "But you don't care about me, do you? You want to know how to survive in this place!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Very well then, let me explain the rules of this cruel mistress."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show 4 card room",
                "text": "Each floor is a deck of 52 cards. You'll face them in ROOMS OF 4 at a time."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the 2 monster cards",
                "text": "MONSTERS lurk in the Clubs and Spades. They'll damage you based on their value!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the weapon card",
                "text": "WEAPONS are found in Diamonds. Equip them to reduce damage from monsters."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "highlight the potion card",
                "text": "POTIONS hide in Hearts. They'll restore your precious health."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show weapon durability",
                "text": "But beware! Weapons lose DURABILITY with each use. They can only defeat weaker monsters after each battle."
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show 4 cards and run button",
                "text": "Sometimes when you enter a new room, RUNNING is wise... but you can't run twice in a row!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Each floor's deck is UNIQUE, with some having more high cards than others, so don't try to card-count!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": "show inventory panel",
                "text": "Your inventory holds up to 2 red cards, either WEAPONS or POTIONS. Save them for when you need them most!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "Now GO FORTH, brave adventurer! May fortune favor your draws!"
            },
            {
                "speaker": "Bartholomew The Merchant",
                "graphic": None,
                "text": "I might even see you again if you survive long enough!"
            }
        ]
        
        self.text_line_num = 1
        self.line_height = 30
        self.final_line_str = ""
        
        self.demo_cards = []
        self.demo_weapon = None
        self.demo_monsters = []
        self.demo_run_button = None
        self.demo_inventory_panel = None
        self.demo_position = None
        
        self.highlight_indices = []
        
    def enter(self):
        """Initialize tutorial state."""
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)
        self.name_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 20)
        
        self.background = ResourceLoader.load_image("bg.png")
        if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.floor = ResourceLoader.load_image("floor.png")
        self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
        
        self.merchant_image = ResourceLoader.load_image("hires/Merchant.png")
        merchant_scale = 14
        self.merchant_image = pygame.transform.scale(self.merchant_image, (int(self.merchant_image.get_width()*merchant_scale), int(self.merchant_image.get_height()*merchant_scale)))
        
        self.merchant_base_pos = (SCREEN_WIDTH - self.merchant_image.get_width() - 50, SCREEN_HEIGHT - self.merchant_image.get_height() - 40)
        
        self._create_ui()
        
        self._start_dialogue(0)

    def _create_demo_cards(self):
        """Create demonstration cards for the tutorial."""
        self.demo_cards = []
        
        for suit, value in [("clubs", 10), ("spades", 7), ("diamonds", 8), ("hearts", 5)]:
            card = Card(suit, value, "dungoen")
            card.face_up = True
            card.is_flipping = False
            self.demo_cards.append(card)

        self._position_demo_cards()
        
    def _create_weapon_durability_demo(self):
        """Create weapon and monster stack for durability demonstration."""
        self.demo_weapon = Card("diamonds", 12, "dungeon")
        self.demo_weapon.face_up = True
        self.demo_weapon.is_flipping = False
        
        self.demo_monsters = []
        monster_values = [12, 10, 8, 5]
        
        for value in monster_values:
            monster = Card("spades", value, "dungeon")
            monster.face_up = True
            monster.is_flipping = False
            self.demo_monsters.append(monster)
            
        weapon_x = self.demo_position[0] - 150
        weapon_y = self.demo_position[1]
        self.demo_weapon.update_position((weapon_x, weapon_y))
        
        start_x = weapon_x + 150
        for i, monster in enumerate(self.demo_monsters):
            monster_x = start_x + i * 30
            monster_y = weapon_y + i * 10
            monster.update_position((monster_x, monster_y))
            
    def _position_demo_cards(self):
        """Position the 4 demo cards centered on screen."""
        if not self.demo_cards:
            return
            
        card_spacing = 35
        total_width = (CARD_WIDTH * 4) + (card_spacing * 3)
        start_x = self.demo_position[0] - total_width // 2
        start_y = self.demo_position[1]
        
        for i, card in enumerate(self.demo_cards):
            card_x = start_x + i * (CARD_WIDTH + card_spacing)
            card.update_position((card_x, start_y))

    def _create_ui(self):
        """Create the UI panels and buttons."""
        panel_width = 700
        panel_height = 200
        panel_x = 50
        panel_y = SCREEN_HEIGHT - panel_height - 50
        
        self.dialogue_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=(40, 30, 25),
            alpha=240,
            border_radius=10,
            dungeon_style=True,
            border_width=3,
            border_colour=(80, 60, 40)
        )
        self.demo_position = (self.dialogue_panel.rect.center[0], SCREEN_HEIGHT // 2 - 160)
        
        name_width = 300
        name_height = 40
        name_x = panel_x + 25
        name_y = panel_y - name_height + 10
        
        self.name_panel = Panel(
            (name_width, name_height),
            (name_x, name_y),
            colour=(50, 40, 35),
            alpha=240,
            border_radius=8,
            dungeon_style=True,
            border_width=2,
            border_colour=(90, 70, 50)
        )
        
        button_width = 140
        button_height = 50
        button_y = panel_y + panel_height - button_height - 15
        button_spacing = 20
        
        total_button_width = button_width * 2 + button_spacing
        button_start_x = panel_x + (panel_width - total_button_width) // 2
        
        next_button_rect = pygame.Rect(
            button_start_x,
            button_y,
            button_width,
            button_height
        )
        self.next_button = Button(
            next_button_rect,
            "NEXT",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 60, 40),
            border_colour=(70, 100, 70)
        )
        
        skip_button_rect = pygame.Rect(
            button_start_x + button_width + button_spacing,
            button_y,
            button_width,
            button_height
        )
        self.skip_button = Button(
            skip_button_rect,
            "SKIP ALL",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 40, 40),
            border_colour=(100, 70, 70)
        )
        
    def _start_dialogue(self, index):
        """Start displaying a new dialogue."""
        if index < len(self.dialogues):
            self.current_dialogue_index = index
            self.target_text = self.dialogues[index]["text"]
            self.current_text = ""
            self.char_index = 0
            self.typing_timer = 0
            self.typing_complete = False
            
            graphic_type = self.dialogues[index]["graphic"]
            self._setup_graphic(graphic_type)
            
    def _setup_graphic(self, graphic_type):
        """Set up the demonstration graphic for the current dialogue."""
        self.demo_cards = []
        self.demo_weapon = None
        self.demo_monsters = []
        self.demo_run_button = None
        self.demo_inventory_panel = None
        self.highlight_indices = []
        
        if graphic_type == "show 4 card room":
            self._create_demo_cards()
            
        elif graphic_type == "highlight the 2 monster cards":
            self._create_demo_cards()
            self.highlight_indices = [0, 1]  # first two cards are monsters
            
        elif graphic_type == "highlight the weapon card":
            self._create_demo_cards()
            self.highlight_indices = [2]  # third card is weapon
            
        elif graphic_type == "highlight the potion card":
            self._create_demo_cards()
            self.highlight_indices = [3]  # fourth card is potion
            
        elif graphic_type == "show weapon durability":
            self._create_weapon_durability_demo()
            
        elif graphic_type == "show 4 cards and run button":
            self._create_demo_cards()
            run_rect = pygame.Rect(
                self.demo_position[0] - 45,
                self.demo_position[1] - 90,
                90, 45
            )
            self.demo_run_button = Button(
                run_rect,
                "RUN",
                self.body_font,
                text_colour=WHITE,
                dungeon_style=True,
                panel_colour=(70, 20, 20),
                border_colour=(120, 40, 40)
            )
            
        elif graphic_type == "show inventory panel":
            inv_width = INVENTORY_PANEL_WIDTH
            inv_height = INVENTORY_PANEL_HEIGHT // 2  # just show top portion
            inv_x = self.demo_position[0] - inv_width // 2
            inv_y = self.demo_position[1] - 40
            
            self.demo_inventory_panel = Panel(
                (inv_width, inv_height),
                (inv_x, inv_y),
                colour=(60, 45, 35),
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(95, 75, 45)
            )
            
    def _complete_typing(self):
        """Instantly complete the current typing animation."""
        self.current_text = self.target_text
        self.char_index = len(self.target_text)
        self.typing_complete = True
        
    def handle_event(self, event):
        """Handle tutorial input events."""
        if event.type == MOUSEMOTION:
            self.next_button.check_hover(event.pos)
            self.skip_button.check_hover(event.pos)
            
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if not self.typing_complete and self.dialogue_panel.rect.collidepoint(event.pos):
                self._complete_typing()
                return
                
            if self.typing_complete:
                if self.next_button.is_clicked(event.pos):
                    if self.current_dialogue_index < len(self.dialogues) - 1:
                        self._start_dialogue(self.current_dialogue_index + 1)
                    else:
                        if self.watch:
                            self.game_manager.change_state("title")
                        else:
                            self.game_manager.change_state("playing")
                        
                elif self.skip_button.is_clicked(event.pos):
                    if self.watch:
                        self.game_manager.change_state("title")
                    else:
                        self.game_manager.change_state("playing")
                    
    def update(self, delta_time):
        """Update tutorial animations and typing effect."""
        if not self.typing_complete and self.char_index < len(self.target_text):
            self.typing_timer += delta_time
            
            while self.typing_timer >= self.typing_speed and self.char_index < len(self.target_text):
                self.current_text += self.target_text[self.char_index]
                self.char_index += 1
                self.typing_timer -= self.typing_speed
                
                self.merchant_shake_amount = 2.0
                
            if self.char_index >= len(self.target_text):
                self.typing_complete = True
                
        if self.merchant_shake_amount > 0:
            self.merchant_shake_amount = max(0, self.merchant_shake_amount - delta_time * 10)
            
    def draw(self, surface):
        """Draw the tutorial screen."""
        surface.blit(self.background, (0, 0))
        surface.blit(self.floor, ((SCREEN_WIDTH - FLOOR_WIDTH)//2, (SCREEN_HEIGHT - FLOOR_HEIGHT)//2))
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        self._draw_demonstration_graphics(surface)
        
        if self.merchant_image:
            shake_x = 0
            shake_y = 0
            if self.merchant_shake_amount > 0:
                shake_x = random.uniform(-self.merchant_shake_amount, self.merchant_shake_amount)
                shake_y = random.uniform(-self.merchant_shake_amount * 0.5, self.merchant_shake_amount * 0.5)
                
            merchant_pos = (
                self.merchant_base_pos[0] + shake_x,
                self.merchant_base_pos[1] + shake_y
            )
            surface.blit(self.merchant_image, merchant_pos)
            
        self.dialogue_panel.draw(surface)
        
        self.name_panel.draw(surface)
        
        speaker_name = self.dialogues[self.current_dialogue_index]["speaker"]
        name_text = self.name_font.render(speaker_name, True, WHITE)
        name_rect = name_text.get_rect(center=self.name_panel.rect.center)
        surface.blit(name_text, name_rect)
        
        self._draw_wrapped_text(surface, self.current_text)
        
        if not self.typing_complete:
            cursor_x, cursor_y = self._get_cursor_position()
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
                cursor_rect = pygame.Rect(cursor_x, cursor_y, 2, 20)
                pygame.draw.rect(surface, WHITE, cursor_rect)
                
        if self.typing_complete:
            self.next_button.draw(surface)
            self.skip_button.draw(surface)
            
            if self.current_dialogue_index == len(self.dialogues) - 1:
                self.next_button.update_text("BEGIN")
                
    def _draw_demonstration_graphics(self, surface):
        """Draw the demonstration graphics for the current dialogue."""
        if self.demo_cards:
            for i, card in enumerate(self.demo_cards):
                if self.highlight_indices and i not in self.highlight_indices:
                    dark_overlay = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 150))
                    card.draw(surface)
                    surface.blit(dark_overlay, card.rect.topleft)
                else:
                    card.draw(surface)
                    
            if self.highlight_indices:
                highlighted_cards = [self.demo_cards[i] for i in self.highlight_indices]
                if highlighted_cards:
                    min_x = min(card.rect.left for card in highlighted_cards)
                    max_x = max(card.rect.right for card in highlighted_cards)
                    min_y = min(card.rect.top for card in highlighted_cards)
                    max_y = max(card.rect.bottom for card in highlighted_cards)
                    
                    padding = 10
                    highlight_rect = pygame.Rect(
                        min_x - padding,
                        min_y - padding,
                        max_x - min_x + padding * 2,
                        max_y - min_y + padding * 2
                    )
                    pygame.draw.rect(surface, (255, 215, 0), highlight_rect, 3, border_radius=5)
                    
        if self.demo_weapon:
            self.demo_weapon.draw(surface)
            
        if self.demo_monsters:
            for monster in self.demo_monsters:
                monster.draw(surface)
                
        if self.demo_run_button:
            highlight_padding = 8
            highlight_rect = self.demo_run_button.rect.inflate(highlight_padding * 2, highlight_padding * 2)
            pygame.draw.rect(surface, (255, 215, 0), highlight_rect, 3, border_radius=8)
            
            self.demo_run_button.draw(surface)
            
        if self.demo_inventory_panel:
            self.demo_inventory_panel.draw(surface)
            
            inv_title = self.body_font.render("Inventory", True, WHITE)
            title_rect = inv_title.get_rect(
                centerx=self.demo_inventory_panel.rect.centerx,
                centery=self.demo_inventory_panel.rect.centery - 70
            )
            surface.blit(inv_title, title_rect)
                
    def _draw_wrapped_text(self, surface, text):
        """Draw text with word wrapping inside the dialogue panel."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        max_width = self.dialogue_panel.rect.width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = self.body_font.render(test_line, True, WHITE)
            
            if text_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        y_offset = self.dialogue_panel.rect.top + 30
        
        for line in lines:
            text_surface = self.body_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(
                left=self.dialogue_panel.rect.left + 20,
                top=y_offset
            )
            surface.blit(text_surface, text_rect)
            y_offset += self.line_height
        
        if self.text_line_num != len(lines):
            self.text_line_num = len(lines)
        
        self.final_line_str = lines[-1]

    def _get_cursor_position(self):
        """Calculate cursor position for typing effect."""
        text_start_x = self.dialogue_panel.rect.left + 20
        text_start_y = self.dialogue_panel.rect.top + 30
        
        x = self.body_font.render(self.final_line_str, True, WHITE).get_width() + text_start_x if self.current_text else text_start_x
        y = self.line_height * (self.text_line_num - 1) + text_start_y if self.current_text else text_start_y
        
        return (x, y)