class Panel:
    def __init__(self, width_height, top_left, colour=DARK_GRAY, alpha=None, border_radius=None,
            dungeon_style=True, border_width=None, border_colour=None):

        if alpha is None:
            alpha = PANEL_ALPHA
        if border_radius is None:
            border_radius = PANEL_BORDER_RADIUS
        if border_width is None:
            border_width = PANEL_BORDER_WIDTH
        if border_colour is None:
            border_colour = PANEL_DEFAULT_BORDER
        self.width_height = width_height
        self.top_left = top_left
        self.rect = pygame.Rect(self.top_left, self.width_height)
        self.colour = colour
        self.alpha = alpha
        self.border_radius = border_radius
        self.dungeon_style = dungeon_style
        self.border_width = border_width
        self.border_colour = border_colour

        self.noise_texture = None
        if self.dungeon_style:
            self._create_noise_texture()

        self._create_surface()

    def _create_noise_texture(self):
        """Create a subtle noise texture for the panel background"""
        width, height = self.rect.size
        self.noise_texture = pygame.Surface((width, height), pygame.SRCALPHA)

        grain_size = 3

        for x in range(0, width, grain_size):
            for y in range(0, height, grain_size):

                darkness = random.randint(0, 25)

                pygame.draw.rect(self.noise_texture, (0, 0, 0, darkness),
                                (x, y, grain_size, grain_size))

                if random.random() < 0.05:
                    lightness = random.randint(5, 15)
                    pygame.draw.rect(
                        self.noise_texture, (255, 255, 255, lightness),
                        (x, y, grain_size, grain_size)
                    )

    def _draw_decorative_border(self, surface, rect, border_radius):
        """Draw a decorative border with corner details for a dungeon feel"""

        darker_border = self._darken_colour(self.border_colour, 0.5)
        lighter_border = self._lighten_colour(self.border_colour, 0.3)

        pygame.draw.rect(surface, darker_border, rect,
            width=self.border_width+1, border_radius=border_radius
        )

        inner_rect = rect.inflate(-4, -4)
        pygame.draw.rect(surface, lighter_border, inner_rect,
            width=1, border_radius=max(0, border_radius-2)
        )

        corner_size = min(10, border_radius)
        if corner_size > 3:

            pygame.draw.line(surface, darker_border,
                (rect.left + border_radius//2, rect.top + 3),
                (rect.left + 3, rect.top + border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.right - border_radius//2, rect.top + 3),
                (rect.right - 3, rect.top + border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.left + border_radius//2, rect.bottom - 3),
                (rect.left + 3, rect.bottom - border_radius//2), 2)

            pygame.draw.line(surface, darker_border,
                (rect.right - border_radius//2, rect.bottom - 3),
                (rect.right - 3, rect.bottom - border_radius//2), 2)

    def _create_surface(self):
        """Create the panel surface with desired style"""

        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(self.surface, self.colour, rect, border_radius=self.border_radius)

        if self.dungeon_style and self.noise_texture:
            self.surface.blit(self.noise_texture, (0, 0))

        if self.dungeon_style:
            self._draw_decorative_border(self.surface, rect, self.border_radius)

        self.surface.set_alpha(self.alpha)

    def _darken_colour(self, colour, factor=0.7):
        """Create a darker version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (int(r * factor), int(g * factor), int(b * factor))

    def _lighten_colour(self, colour, factor=0.3):
        """Create a lighter version of the colour"""
        r, g, b = colour[0], colour[1], colour[2]
        return (min(255, int(r + (255-r) * factor)),
                min(255, int(g + (255-g) * factor)),
                min(255, int(b + (255-b) * factor)))

    def _draw_rounded_rect(self, surface, rect, colour, border_radius):
        """Draw a rectangle with rounded corners"""
        rect_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, colour, rect_surf.get_rect(), border_radius=border_radius)
        surface.blit(rect_surf, rect.topleft)

    def update_position(self, pos):
        self.rect.topleft = pos

    def update_size(self, size):
        self.rect.size = size

        if self.dungeon_style:
            self._create_noise_texture()

        self._create_surface()

    def update_colour(self, colour):
        self.colour = colour
        self._create_surface()

    def update_alpha(self, alpha):
        self.alpha = alpha
        self.surface.set_alpha(alpha)

    def update_border_radius(self, border_radius):
        self.border_radius = border_radius
        self._create_surface()

    def update_style(self, dungeon_style, border_width=None, border_colour=None):
        """Update the styling options"""
        self.dungeon_style = dungeon_style
        if border_width is not None:
            self.border_width = border_width
        if border_colour is not None:
            self.border_colour = border_colour
        self._create_surface()

    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)