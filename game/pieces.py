"""Piece definitions and basic movement vectors."""

from enum import Enum
from typing import List, Tuple

class Color(Enum):
    WHITE = "w"
    BLACK = "b"

class PieceType(Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"

# Unicode chess symbols for fallback rendering
PIECE_SYMBOLS = {
    (Color.WHITE, PieceType.KING): "♔",
    (Color.WHITE, PieceType.QUEEN): "♕",
    (Color.WHITE, PieceType.ROOK): "♖",
    (Color.WHITE, PieceType.BISHOP): "♗",
    (Color.WHITE, PieceType.KNIGHT): "♘",
    (Color.WHITE, PieceType.PAWN): "♙",
    (Color.BLACK, PieceType.KING): "♚",
    (Color.BLACK, PieceType.QUEEN): "♛",
    (Color.BLACK, PieceType.ROOK): "♜",
    (Color.BLACK, PieceType.BISHOP): "♝",
    (Color.BLACK, PieceType.KNIGHT): "♞",
    (Color.BLACK, PieceType.PAWN): "♟",
}

def get_piece_symbol(color: Color, piece_type: PieceType) -> str:
    return PIECE_SYMBOLS.get((color, piece_type), "?")
