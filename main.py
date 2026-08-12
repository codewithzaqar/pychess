#!/usr/bin/env python3
"""PyChess v0.0.1a - Desktop Chess Client for Linux/Windows"""

import sys
import os

# Ensure package imports work when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from game.board import Board
from ui.chess_gui import ChessGUI

VERSION = "0.0.1a"

def main():
    print(f"PyChess {VERSION} starting...")
    root = tk.Tk()

    # Set icon/title based on platform
    if sys.platform == "win32":
        root.iconbitmap(default="")  # Windows users can add .ico path
    else:
        root.wm_title(f"PyChess {VERSION}")

    board = Board()
    app = ChessGUI(root, board)

    root.mainloop()

if __name__ == "__main__":
    main()
