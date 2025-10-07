"""
Resource loading and caching system
"""

import pygame
from config import relative_to_assets, CARD_WIDTH, CARD_HEIGHT


class ResourceLoader:
    """Class for loading and caching game resources."""

    _image_cache = {}
    _font_cache = {}

    @classmethod
    def load_image(cls, name, scale=1, cache=True):
        """Load an image with optional scaling and caching."""
        cache_key = f"{name}_{scale}"
        if cache and cache_key in cls._image_cache:
            return cls._image_cache[cache_key]

        try:
            image = pygame.image.load(relative_to_assets(name))

            if scale != 1:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)

            if cache:
                cls._image_cache[cache_key] = image

            return image
        except pygame.error as e:
            # Return a placeholder surface if loading fails
            return pygame.Surface((CARD_WIDTH, CARD_HEIGHT))

    @classmethod
    def load_font(cls, name, size):
        """Load a font with caching."""
        cache_key = f"{name}_{size}"
        if cache_key in cls._font_cache:
            return cls._font_cache[cache_key]

        try:
            font = pygame.font.Font(relative_to_assets(name), size)
            cls._font_cache[cache_key] = font
            return font
        except pygame.error as e:
            return pygame.font.SysFont(None, size)

    @classmethod
    def clear_cache(cls):
        """Clear all cached resources."""
        cls._image_cache.clear()
        cls._font_cache.clear()