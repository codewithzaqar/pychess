"""Core chess board representation and move handling."""

from typing import Optional, Dict, Tuple
from .pieces import Color, PieceType, get_piece_symbol

Position = Tuple[int, int]  # (row, col) 0-7

class Piece:
    def __init__(self, color: Color, piece_type: PieceType):
        self.color = color
        self.type = piece_type

    def __repr__(self):
        return get_piece_symbol(self.color, self.type)

class Board:
    def __init__(self):
        self.grid: Dict[Position, Optional[Piece]] = {}
        self.turn: Color = Color.WHITE
        self._setup_initial_position()

    def _setup_initial_position(self):
        """Set up standard chess starting position."""
        back_rank = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
            PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
            PieceType.KNIGHT, PieceType.ROOK
        ]
        for col, ptype in enumerate(back_rank):
            self.grid[(0, col)] = Piece(Color.BLACK, ptype)
            self.grid[(7, col)] = Piece(Color.WHITE, ptype)
        for col in range(8):
            self.grid[(1, col)] = Piece(Color.BLACK, PieceType.PAWN)
            self.grid[(6, col)] = Piece(Color.WHITE, PieceType.PAWN)

    def get_piece(self, pos: Position) -> Optional[Piece]:
        return self.grid.get(pos)

    def is_valid_move(self, start: Position, end: Position) -> bool:
        """Basic move validation (v0.0.1a01 - simplified)."""
        piece = self.get_piece(start)
        target = self.get_piece(end)

        if piece is None or piece.color != self.turn:
            return False
        if target is not None and target.color == self.turn:
            return False
        if start == end:
            return False

        dr = end[0] - start[0]
        dc = end[1] - start[1]

        # Simplified movement rules for alpha
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            start_row = 6 if piece.color == Color.WHITE else 1
            if dc == 0 and target is None:
                if dr == direction or (dr == 2 * direction and start[0] == start_row and self.get_piece((start[0] + direction, start[1])) is None):
                    return True
            elif abs(dc) == 1 and dr == direction and target is not None:
                return True
        elif piece.type == PieceType.KNIGHT:
            if sorted([abs(dr), abs(dc)]) == [1, 2]:
                return True
        elif piece.type == PieceType.KING:
            if abs(dr) <= 1 and abs(dc) <= 1:
                return True
        elif piece.type in (PieceType.ROOK, PieceType.BISHOP, PieceType.QUEEN):
            if piece.type != PieceType.BISHOP and (dr == 0 or dc == 0):
                return self._is_path_clear(start, end)
            if piece.type != PieceType.ROOK and abs(dr) == abs(dc):
                return self._is_path_clear(start, end)

        return False

    def _is_path_clear(self, start: Position, end: Position) -> bool:
        dr = end[0] - start[0]
        dc = end[1] - start[1]
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
        r, c = start[0] + step_r, start[1] + step_c
        while (r, c) != end:
            if self.get_piece((r, c)) is not None:
                return False
            r += step_r
            c += step_c
        return True

    def make_move(self, start: Position, end: Position) -> bool:
        if not self.is_valid_move(start, end):
            return False
        self.grid[end] = self.grid.pop(start)
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        return True
