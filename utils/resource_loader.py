""" Utility functions for loading game resources. """
import os
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, ASSETS_PATH

class ResourceLoader:
    """Class for loading and caching game resources."""
    
    _image_cache = {}  # Class variable to cache loaded images
    _font_cache = {}   # Class variable to cache loaded fonts
    
    @classmethod
    def load_image(cls, name, scale=1, cache=True):
        # Check if the image is already in the cache
        cache_key = f"{name}_{scale}"
        if cache and cache_key in cls._image_cache:
            return cls._image_cache[cache_key]
        
        try:
            # Load the image
            image_path = os.path.join(ASSETS_PATH, name)
            image = pygame.image.load(image_path)
            
            # Scale the image if needed
            if scale != 1:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            
            # Cache the image if requested
            if cache:
                cls._image_cache[cache_key] = image
                
            return image
        except pygame.error as e:
            print(f"Cannot load image: {image_path}")
            print(e)
            # Return a placeholder surface
            return pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    
    @classmethod
    def load_font(cls, name, size):
        # Check if the font is already in the cache
        cache_key = f"{name}_{size}"
        if cache_key in cls._font_cache:
            return cls._font_cache[cache_key]
        
        try:
            # Load the font
            font_path = os.path.join(ASSETS_PATH, name)
            font = pygame.font.Font(font_path, size)
            
            # Cache the font
            cls._font_cache[cache_key] = font
                
            return font
        except pygame.error as e:
            print(f"Cannot load font: {font_path}")
            print(e)
            # Return a system font as fallback
            return pygame.font.SysFont(None, size)
    
    @classmethod
    def clear_cache(cls):
        cls._image_cache.clear()
        cls._font_cache.clear()