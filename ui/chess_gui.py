"""Tkinter-based chess GUI with check indication."""

import tkinter as tk
from typing import Optional, Tuple
from game.board import Board, Position
from game.pieces import Color, get_piece_symbol

SQUARE_SIZE = 70
LIGHT_COLOR = "#EEEBD0"
DARK_COLOR = "#B58863"
HIGHLIGHT_COLOR = "#BBC94C"
CHECK_COLOR = "#FF6B6B"  # Red highlight for king in check

class ChessGUI:
    def __init__(self, root: tk.Tk, board: Board):
        self.root = root
        self.board = board
        self.selected: Optional[Position] = None

        self.root.title("PyChess v0.0.1a")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=SQUARE_SIZE * 8, height=SQUARE_SIZE * 8)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)

        self.status_var = tk.StringVar(value="White to move")
        tk.Label(root, textvariable=self.status_var, font=("Arial", 12)).pack(pady=(0, 10))

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        in_check = self.board.is_in_check(self.board.turn)
        king_pos = self.board._find_king(self.board.turn) if in_check else None

        for row in range(8):
            for col in range(8):
                x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                
                # Determine square color
                if (row, col) == king_pos and in_check:
                    color = CHECK_COLOR
                elif self.selected == (row, col):
                    color = HIGHLIGHT_COLOR
                else:
                    color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                    
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board.get_piece((row, col))
                if piece:
                    symbol = get_piece_symbol(piece.color, piece.type)
                    font_size = int(SQUARE_SIZE * 0.75)
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE // 2, y1 + SQUARE_SIZE // 2,
                        text=symbol, font=("Segoe UI Symbol", font_size),
                        fill="black" if piece.color == Color.BLACK else "white"
                    )

        # Update status bar
        turn_name = "White" if self.board.turn == Color.WHITE else "Black"
        status = f"{turn_name} to move"
        if in_check:
            status += " | CHECK!"
        self.status_var.set(status)

    def _on_click(self, event: tk.Event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        pos: Position = (row, col)

        if self.selected is None:
            piece = self.board.get_piece(pos)
            if piece and piece.color == self.board.turn:
                self.selected = pos
        else:
            if self.board.make_move(self.selected, pos):
                self.selected = None
            else:
                piece = self.board.get_piece(pos)
                self.selected = pos if (piece and piece.color == self.board.turn) else None

        self.draw_board()
