class StatusUI:
    """Displays current floor, room, and player stats during gameplay."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.header_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 28)
        self.normal_font = ResourceLoader.load_font("fonts/Pixel Times.ttf", 16)
        self.panel_rect = None

    def update_fonts(self, header_font, normal_font):
        """Update fonts if they are loaded after initialization."""
        self.header_font = header_font
        self.normal_font = normal_font

    def update_status(self):
        """Update the status UI with current room/floor information."""
        pass

    def draw(self, surface):
        """Draw the status UI with a dungeon-themed panel."""

        floor_manager = self.game_manager.floor_manager
        current_floor = floor_manager.get_current_floor()

        if "'" in current_floor:
            b = []
            for temp in current_floor.split():
                b.append(temp.capitalize())
            current_floor = " ".join(b)
        else:
            current_floor = current_floor.title()
        current_floor_index = max(1, floor_manager.current_floor_index + 1)

        current_room = floor_manager.current_room

        total_rooms = FLOOR_TOTAL

        floor_text = self.header_font.render(f"Floor {current_floor_index}: {current_floor}", True, WHITE)

        panel_width = 650

        panel_padding = 60
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH//2 - panel_width//2, 50),
            (650, 90)
        )

        if not hasattr(self, 'styled_panel'):

            self.styled_panel = Panel(
                (self.panel_rect.width, self.panel_rect.height),
                (self.panel_rect.left, self.panel_rect.top),
                colour=(70, 60, 45),
                alpha=230,
                border_radius=8,
                dungeon_style=True,
                border_width=3,
                border_colour=(110, 90, 50)
            )

        self.styled_panel.draw(surface)

        floor_rect = floor_text.get_rect(centerx=self.panel_rect.centerx, top=self.panel_rect.top + 15)

        glow_surface = pygame.Surface((floor_text.get_width() + 10, floor_text.get_height() + 10), pygame.SRCALPHA)
        glow_colour = (230, 220, 170, 30)
        pygame.draw.ellipse(glow_surface, glow_colour, glow_surface.get_rect())
        glow_rect = glow_surface.get_rect(center=floor_rect.center)

        surface.blit(glow_surface, glow_rect)
        surface.blit(floor_text, floor_rect)

        room_text = self.normal_font.render(f"Room {current_room}", True, (220, 220, 200))
        room_rect = room_text.get_rect(centerx=self.panel_rect.centerx, top=floor_rect.bottom + 10)
        surface.blit(room_text, room_rect)