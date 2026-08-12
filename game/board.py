"""Core chess board representation with check/castling support."""

from typing import Optional, Dict, Tuple, List, Set
from copy import deepcopy
from .pieces import Color, PieceType, get_piece_symbol

Position = Tuple[int, int]

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
        # Track if kings/rooks have moved for castling rights
        self._moved: Set[Position] = set() 
        self._setup_initial_position()

    def _setup_initial_position(self):
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

    def _find_king(self, color: Color) -> Optional[Position]:
        for pos, piece in self.grid.items():
            if piece and piece.color == color and piece.type == PieceType.KING:
                return pos
        return None

    def is_square_attacked(self, square: Position, by_color: Color) -> bool:
        """Check if any piece of 'by_color' can attack 'square'."""
        for pos, piece in self.grid.items():
            if piece and piece.color == by_color:
                if self._is_pseudo_legal_move(pos, square):
                    return True
        return False

    def is_in_check(self, color: Color) -> bool:
        king_pos = self._find_king(color)
        if king_pos is None:
            return False
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_pos, opponent)

    def _is_pseudo_legal_move(self, start: Position, end: Position) -> bool:
        """Move validation WITHOUT checking if it leaves king in check."""
        piece = self.get_piece(start)
        target = self.get_piece(end)

        if piece is None or target is not None and target.color == piece.color:
            return False
        if start == end:
            return False

        dr = end[0] - start[0]
        dc = end[1] - start[1]

        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            start_row = 6 if piece.color == Color.WHITE else 1
            if dc == 0 and target is None:
                if dr == direction:
                    return True
                if dr == 2 * direction and start[0] == start_row and self.get_piece((start[0] + direction, start[1])) is None:
                    return True
            elif abs(dc) == 1 and dr == direction and target is not None:
                return True
        elif piece.type == PieceType.KNIGHT:
            return sorted([abs(dr), abs(dc)]) == [1, 2]
        elif piece.type == PieceType.KING:
            if abs(dr) <= 1 and abs(dc) <= 1:
                return True
            # Castling (pseudo-legal; full validation in is_valid_move)
            if dr == 0 and abs(dc) == 2 and start not in self._moved:
                rook_col = 0 if dc < 0 else 7
                rook_pos = (start[0], rook_col)
                rook = self.get_piece(rook_pos)
                if rook and rook.type == PieceType.ROOK and rook_pos not in self._moved:
                    step = 1 if dc > 0 else -1
                    path_clear = all(self.get_piece((start[0], start[1] + i)) is None for i in range(step, dc, step))
                    return path_clear
        elif piece.type in (PieceType.ROOK, PieceType.BISHOP, PieceType.QUEEN):
            if piece.type != PieceType.BISHOP and (dr == 0 or dc == 0):
                return self._is_path_clear(start, end)
            if piece.type != PieceType.ROOK and abs(dr) == abs(dc):
                return self._is_path_clear(start, end)

        return False

    def is_valid_move(self, start: Position, end: Position) -> bool:
        """Full legal move validation including check prevention."""
        if not self._is_pseudo_legal_move(start, end):
            return False
        
        # Simulate move to ensure king isn't left in check
        saved_target = self.grid.get(end)
        self.grid[end] = self.grid.pop(start)
        
        in_check = self.is_in_check(self.turn)
        
        # Undo simulation
        self.grid[start] = self.grid[end]
        self.grid[end] = saved_target
        
        return not in_check

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
        
        piece = self.get_piece(start)
        self.grid[end] = self.grid.pop(start)
        self._moved.add(start)
        self._moved.add(end)

        # Handle castling rook movement
        if piece.type == PieceType.KING and abs(end[1] - start[1]) == 2:
            rook_src_col = 0 if end[1] < start[1] else 7
            rook_dst_col = 3 if end[1] < start[1] else 5
            rook_src = (start[0], rook_src_col)
            rook_dst = (start[0], rook_dst_col)
            self.grid[rook_dst] = self.grid.pop(rook_src)
            self._moved.add(rook_src)
            self._moved.add(rook_dst)

        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        return True
