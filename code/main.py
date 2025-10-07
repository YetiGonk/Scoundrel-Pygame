"""
Scoundrel - The 52-Card Roguelike Dungeon Crawler
Entry point for the game
"""

import asyncio
import sys
import pygame
from pygame.locals import QUIT

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from core.game_manager import GameManager


async def main():
    """Main entry point for the game."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scoundrel - The 52-Card Roguelike Dungeon Crawler")
    clock = pygame.time.Clock()

    game_manager = GameManager()

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                game_manager.handle_event(event)
        
        game_manager.update(delta_time)
        game_manager.draw(screen)
        pygame.display.flip()
        
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())