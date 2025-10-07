class GameOverState(GameState):
    """The game over state of the game."""

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.title_font = None
        self.header_font = None
        self.body_font = None
        self.background = None
        self.floor = None

        self.restart_button = None
        self.title_button = None

        self.game_over_panel = None

        self.particles = []

        self.playing_state = None

    def enter(self):

        self.playing_state = self.game_manager.states["playing"]

        self.title_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 48)
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 36)
        self.body_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 24)

        panel_width = 580
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        if self.game_manager.game_data["victory"]:
            panel_colour = (40, 60, 40)
            border_colour = (80, 180, 80)
        else:
            panel_colour = (60, 30, 30)
            border_colour = (150, 50, 50)

        self.game_over_panel = Panel(
            (panel_width, panel_height),
            (panel_x, panel_y),
            colour=panel_colour,
            alpha=240,
            border_radius=15,
            dungeon_style=True,
            border_width=3,
            border_colour=border_colour
        )

        button_width = 300
        button_height = 50
        button_spacing = 12
        buttons_y = panel_y + panel_height - button_height*2 - button_spacing - 33

        restart_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y,
            button_width,
            button_height
        )
        self.restart_button = Button(
            restart_button_rect,
            "NEW ADVENTURE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(40, 80, 40) if self.game_manager.game_data["victory"] else (80, 40, 40),
            border_colour=(80, 150, 80) if self.game_manager.game_data["victory"] else (150, 70, 70)
        )

        title_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            buttons_y + button_height + button_spacing,
            button_width,
            button_height
        )
        self.title_button = Button(
            title_button_rect,
            "RETURN TO TITLE",
            self.body_font,
            text_colour=WHITE,
            dungeon_style=True,
            panel_colour=(60, 60, 80),
            border_colour=(100, 100, 160)
        )

        self._create_particles()

    def _create_particles(self):
        """Create particles based on victory/defeat state"""
        self.particles = []

        if self.game_manager.game_data["victory"]:
            num_particles = 40
            colours = [(120, 255, 120), (180, 255, 180), (220, 255, 220)]
        else:
            num_particles = 20
            colours = [(255, 120, 120), (255, 150, 150)]

        for _ in range(num_particles):

            edge = random.randint(0, 3)

            if edge == 0:
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.top - 20, self.game_over_panel.rect.top + 20)
            elif edge == 1:
                x = random.uniform(self.game_over_panel.rect.right - 20, self.game_over_panel.rect.right + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)
            elif edge == 2:
                x = random.uniform(self.game_over_panel.rect.left, self.game_over_panel.rect.right)
                y = random.uniform(self.game_over_panel.rect.bottom - 20, self.game_over_panel.rect.bottom + 20)
            else:
                x = random.uniform(self.game_over_panel.rect.left - 20, self.game_over_panel.rect.left + 20)
                y = random.uniform(self.game_over_panel.rect.top, self.game_over_panel.rect.bottom)

            colour = random.choice(colours)

            self.particles.append({
                'x': x,
                'y': y,
                'colour': colour,
                'size': random.uniform(1.5, 3.5),
                'life': 1.0,
                'decay': random.uniform(0.002, 0.005),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5)
            })

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:

            if self.restart_button and self.restart_button.is_clicked(event.pos):

                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False

                self.game_manager.states["playing"] = PlayingState(self.game_manager)

                self.game_manager.start_new_run()

            elif self.title_button and self.title_button.is_clicked(event.pos):

                self.game_manager.game_data["life_points"] = 20
                self.game_manager.game_data["max_life"] = 20
                self.game_manager.game_data["victory"] = False

                self.game_manager.states["playing"] = PlayingState(self.game_manager)

                self.game_manager.change_state("title")

        mouse_pos = pygame.mouse.get_pos()
        if self.restart_button:
            self.restart_button.check_hover(mouse_pos)
        if self.title_button:
            self.title_button.check_hover(mouse_pos)

    def _update_particles(self, delta_time):
        """Update the particle effects"""

        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= particle['decay']

            if particle['life'] <= 0:
                self.particles.remove(particle)

        if random.random() < 0.1 and len(self.particles) < 60:
            self._create_particles()

    def update(self, delta_time):
        """Update game over state"""
        self._update_particles(delta_time)

    def draw(self, surface):

        if not self.playing_state:

            if not hasattr(self, 'background') or not self.background:
                self.background = ResourceLoader.load_image("bg.png")
                if self.background.get_width() != SCREEN_WIDTH or self.background.get_height() != SCREEN_HEIGHT:
                    self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

            surface.blit(self.background, (0, 0))

            if not hasattr(self, 'floor') or not self.floor:
                random_floor_type = random.choice(FLOOR_TYPES)
                floor_image = f"floors/{random_floor_type}_floor.png"

                try:
                    self.floor = ResourceLoader.load_image(floor_image)
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))
                except:

                    self.floor = ResourceLoader.load_image("floor.png")
                    self.floor = pygame.transform.scale(self.floor, (FLOOR_WIDTH, FLOOR_HEIGHT))

            surface.blit(self.floor, ((SCREEN_WIDTH - FLOOR_WIDTH)/2, (SCREEN_HEIGHT - FLOOR_HEIGHT)/2))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
        else:

            self.playing_state.draw(surface)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

        for particle in self.particles:
            alpha = int(255 * particle['life'])

            r, g, b = particle['colour']
            particle_colour = pygame.Color(r, g, b, alpha)
            pygame.draw.circle(
                surface,
                particle_colour,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'] * (0.5 + 0.5 * particle['life']))
            )

        self.game_over_panel.draw(surface)

        if self.game_manager.game_data["victory"]:
            result_text = self.title_font.render("VICTORY!", True, (180, 255, 180))
            subtitle_text = self.header_font.render("You have conquered the dungeon", True, WHITE)
        else:
            result_text = self.title_font.render("DEFEATED", True, (255, 180, 180))
            subtitle_text = self.header_font.render("Your adventure ends here...", True, WHITE)

        result_rect = result_text.get_rect(centerx=SCREEN_WIDTH//2, top=self.game_over_panel.rect.top + 32)
        surface.blit(result_text, result_rect)

        subtitle_rect = subtitle_text.get_rect(centerx=SCREEN_WIDTH//2, top=result_rect.bottom + 20)
        surface.blit(subtitle_text, subtitle_rect)

        stats_y = subtitle_rect.bottom + 25

        floors_text = self.body_font.render(
            f"Floors Completed: {self.game_manager.floor_manager.current_floor_index}",
            True, WHITE
        )
        floors_rect = floors_text.get_rect(centerx=SCREEN_WIDTH//2, top=stats_y)
        surface.blit(floors_text, floors_rect)

        if self.restart_button:
            self.restart_button.draw(surface)

        if self.title_button:
            self.title_button.draw(surface)