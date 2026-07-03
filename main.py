#!/usr/bin/env python3
"""
Eclipse Depths – main entry point
Run with: python main.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from src.core.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
