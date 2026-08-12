"""Core chess board with full rule compliance."""

from typing import Optional, Dict, Tuple, Set, List
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
        self._moved: Set[Position] = set()
        self.en_passant_target: Optional[Position] = None  # Square behind pawn that double-pushed
        self.halfmove_clock: int = 0  # For future 50-move rule
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
        for pos, piece in self.grid.items():
            if piece and piece.color == by_color:
                if self._is_pseudo_legal_move(pos, square, check_attack=True):
                    return True
        return False

    def is_in_check(self, color: Color) -> bool:
        king_pos = self._find_king(color)
        if king_pos is None:
            return False
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_pos, opponent)

    def _is_pseudo_legal_move(self, start: Position, end: Position, check_attack: bool = False) -> bool:
        """Validate move geometry. check_attack=True treats pawns as attackers only diagonally."""
        piece = self.get_piece(start)
        target = self.get_piece(end)
        if piece is None or start == end:
            return False
        if not check_attack and target is not None and target.color == piece.color:
            return False

        dr = end[0] - start[0]
        dc = end[1] - start[1]

        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            start_row = 6 if piece.color == Color.WHITE else 1
            
            if check_attack:
                # Pawns attack diagonally only when checking attacks
                return dr == direction and abs(dc) == 1
            
            # Normal pawn moves
            if dc == 0 and target is None:
                if dr == direction:
                    return True
                if dr == 2 * direction and start[0] == start_row and self.get_piece((start[0] + direction, start[1])) is None:
                    return True
            elif abs(dc) == 1 and dr == direction:
                # Capture or en passant
                if target is not None and target.color != piece.color:
                    return True
                if end == self.en_passant_target:
                    return True
        elif piece.type == PieceType.KNIGHT:
            return sorted([abs(dr), abs(dc)]) == [1, 2]
        elif piece.type == PieceType.KING:
            if abs(dr) <= 1 and abs(dc) <= 1:
                return True
            # Castling
            if not check_attack and dr == 0 and abs(dc) == 2 and start not in self._moved:
                rook_col = 0 if dc < 0 else 7
                rook_pos = (start[0], rook_col)
                rook = self.get_piece(rook_pos)
                if rook and rook.type == PieceType.ROOK and rook_pos not in self._moved:
                    step = 1 if dc > 0 else -1
                    path_clear = all(self.get_piece((start[0], start[1] + i)) is None for i in range(step, dc + step, step))
                    # King cannot pass through check
                    opponent = Color.BLACK if piece.color == Color.WHITE else Color.WHITE
                    no_check_path = all(not self.is_square_attacked((start[0], start[1] + i), opponent) for i in range(0, dc + step, step))
                    return path_clear and no_check_path
        elif piece.type in (PieceType.ROOK, PieceType.BISHOP, PieceType.QUEEN):
            if piece.type != PieceType.BISHOP and (dr == 0 or dc == 0):
                return self._is_path_clear(start, end)
            if piece.type != PieceType.ROOK and abs(dr) == abs(dc):
                return self._is_path_clear(start, end)
        return False

    def is_valid_move(self, start: Position, end: Position) -> bool:
        if not self._is_pseudo_legal_move(start, end):
            return False
        # Simulate to verify king safety
        saved_target = self.grid.get(end)
        saved_ep = self.en_passant_target
        
        self.grid[end] = self.grid.pop(start)
        # Handle en passant capture simulation
        ep_captured_pos = None
        if self.get_piece(end).type == PieceType.PAWN and end == saved_ep:
            ep_captured_pos = (start[0], end[1])
            saved_ep_piece = self.grid.pop(ep_captured_pos)
        
        in_check = self.is_in_check(self.turn)
        
        # Undo
        self.grid[start] = self.grid[end]
        self.grid[end] = saved_target
        if ep_captured_pos:
            self.grid[ep_captured_pos] = saved_ep_piece
        self.en_passant_target = saved_ep
        
        return not in_check

    def has_legal_moves(self, color: Color) -> bool:
        """Check if the given color has any legal move available."""
        for start, piece in list(self.grid.items()):
            if piece and piece.color == color:
                for r in range(8):
                    for c in range(8):
                        if self.is_valid_move(start, (r, c)):
                            return True
        return False

    def is_promotion(self, start: Position, end: Position) -> bool:
        piece = self.get_piece(start)
        if piece and piece.type == PieceType.PAWN:
            promo_row = 0 if piece.color == Color.WHITE else 7
            return end[0] == promo_row
        return False

    def make_move(self, start: Position, end: Position, promotion: PieceType = PieceType.QUEEN) -> bool:
        if not self.is_valid_move(start, end):
            return False
        
        piece = self.get_piece(start)
        captured = self.get_piece(end)
        
        # En passant capture
        if piece.type == PieceType.PAWN and end == self.en_passant_target:
            ep_capture_pos = (start[0], end[1])
            del self.grid[ep_capture_pos]
        
        # Update en passant target
        if piece.type == PieceType.PAWN and abs(end[0] - start[0]) == 2:
            ep_row = (start[0] + end[0]) // 2
            self.en_passant_target = (ep_row, start[1])
        else:
            self.en_passant_target = None
        
        # Move piece
        self.grid[end] = self.grid.pop(start)
        self._moved.add(start)
        self._moved.add(end)
        
        # Promotion
        if piece.type == PieceType.PAWN and end[0] in (0, 7):
            self.grid[end] = Piece(piece.color, promotion)
        
        # Castling rook
        if piece.type == PieceType.KING and abs(end[1] - start[1]) == 2:
            rook_src_col = 0 if end[1] < start[1] else 7
            rook_dst_col = 3 if end[1] < start[1] else 5
            rook_src = (start[0], rook_src_col)
            rook_dst = (start[0], rook_dst_col)
            self.grid[rook_dst] = self.grid.pop(rook_src)
            self._moved.add(rook_src)
            self._moved.add(rook_dst)
        
        # Halfmove clock (reset on pawn move or capture)
        if piece.type == PieceType.PAWN or captured:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        return True

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
