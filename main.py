"""Entry point for Legends of the Cursed Realm."""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

# Set mixer quality before pygame.init() — channel count left at default (stereo)
# so SDL doesn't have to fall back and we get clean audio on all systems.
import pygame
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
