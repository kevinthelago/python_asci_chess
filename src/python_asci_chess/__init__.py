#
# FEN = forsyth_edwards_notation
#
import os
from util import can_cast, safe_cast

KING = 1    # 0001
QUEEN = 2   # 0010
ROOK = 3    # 0011
BISHOP = 4  # 0100
KNIGHT = 5  # 0101
PAWN = 6    # 0110

BLACK = 8   # 01 0000
WHITE = 16  # 10 0000

CLEAR_COMMAND = 'cls' if os.name in ('nt', 'dos') else 'clear'

EMPTY_SPACE = " "
SPACE = " "

BLACK_AND_WHITE_COLOR_SCHEME = {
    # square_color + piece_color_offset (0=white piece, 2=black piece)
    0: "\033[48;2;200;200;200;38;2;255;255;255m",   # light sq, white piece
    1: "\033[48;2;50;50;50;38;2;255;255;255m",      # dark sq, white piece
    2: "\033[48;2;200;200;200;38;2;0;0;0m",         # light sq, black piece
    3: "\033[48;2;50;50;50;38;2;0;0;0m",            # dark sq, black piece
    # +4 offset for highlighted squares (legal move targets)
    4: "\033[48;2;130;210;130;38;2;255;255;255m",   # highlighted light sq, white piece
    5: "\033[48;2;80;160;80;38;2;255;255;255m",     # highlighted dark sq, white piece
    6: "\033[48;2;130;210;130;38;2;0;0;0m",         # highlighted light sq, black piece
    7: "\033[48;2;80;160;80;38;2;0;0;0m",           # highlighted dark sq, black piece
    None: "\033[0m"                                  # reset
}


class Chess:
    starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    fen_map = {
        'k': 1,
        'q': 2,
        'r': 3,
        'b': 4,
        'n': 5,
        'p': 6
    }

    def __init__(self, color_scheme=None):
        if color_scheme is None:
            color_scheme = BLACK_AND_WHITE_COLOR_SCHEME
        self.color_scheme = color_scheme
        self.board = [[Square(j, i) for j in range(8)] for i in range(8)]
        self.files = [column.get_file() for column in self.board[0]]
        self.ranks = [i + 1 for i in range(len(self.board))]
        self.player = WHITE
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_target = None  # (row, col) of the capturable square
        self.move_history = []
        self.error = ""

    # ── low-level board helpers ──────────────────────────────────────────────

    def _sq(self, row, col):
        """Piece integer at (row, col), or None."""
        p = self.board[row][col].piece
        return p.piece if p is not None else None

    def _set_sq(self, row, col, piece_int):
        self.board[row][col].piece = Piece(piece_int) if piece_int is not None else None

    @staticmethod
    def _color(piece_int):
        return WHITE if piece_int & WHITE == WHITE else BLACK

    @staticmethod
    def _type(piece_int):
        """Extract piece type (KING..PAWN) from encoded integer."""
        return piece_int & 7

    def _is_enemy(self, piece_int, color):
        return piece_int is not None and self._color(piece_int) != color

    def _is_empty(self, row, col):
        return self._sq(row, col) is None

    @staticmethod
    def _in_bounds(row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def _find_king(self, color):
        target = KING | color
        for r in range(8):
            for c in range(8):
                if self._sq(r, c) == target:
                    return r, c
        return None, None

    # ── pseudo-legal move generators ─────────────────────────────────────────

    def _pseudo_legal_moves(self, row, col):
        """All moves for the piece at (row, col), ignoring check. Excludes castling."""
        piece_int = self._sq(row, col)
        if piece_int is None:
            return []
        color = self._color(piece_int)
        pt = self._type(piece_int)
        if pt == PAWN:
            return self._pawn_moves(row, col, color)
        if pt == KNIGHT:
            return self._knight_moves(row, col, color)
        if pt == BISHOP:
            return self._sliding_moves(row, col, color, ((-1,-1),(-1,1),(1,-1),(1,1)))
        if pt == ROOK:
            return self._sliding_moves(row, col, color, ((-1,0),(1,0),(0,-1),(0,1)))
        if pt == QUEEN:
            return (self._sliding_moves(row, col, color, ((-1,-1),(-1,1),(1,-1),(1,1))) +
                    self._sliding_moves(row, col, color, ((-1,0),(1,0),(0,-1),(0,1))))
        if pt == KING:
            return self._king_moves(row, col, color)
        return []

    def _pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        fwd = row + direction

        if not self._in_bounds(fwd, col):
            return moves

        if self._is_empty(fwd, col):
            moves.append((fwd, col))
            fwd2 = row + 2 * direction
            if row == start_row and self._in_bounds(fwd2, col) and self._is_empty(fwd2, col):
                moves.append((fwd2, col))

        for dc in (-1, 1):
            nc = col + dc
            if self._in_bounds(fwd, nc):
                target = self._sq(fwd, nc)
                if target is not None and self._is_enemy(target, color):
                    moves.append((fwd, nc))
                elif self.en_passant_target == (fwd, nc):
                    moves.append((fwd, nc))
        return moves

    def _knight_moves(self, row, col, color):
        moves = []
        for dr, dc in ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)):
            nr, nc = row + dr, col + dc
            if self._in_bounds(nr, nc):
                target = self._sq(nr, nc)
                if target is None or self._is_enemy(target, color):
                    moves.append((nr, nc))
        return moves

    def _sliding_moves(self, row, col, color, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while self._in_bounds(nr, nc):
                target = self._sq(nr, nc)
                if target is None:
                    moves.append((nr, nc))
                elif self._is_enemy(target, color):
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, row, col, color):
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if self._in_bounds(nr, nc):
                    target = self._sq(nr, nc)
                    if target is None or self._is_enemy(target, color):
                        moves.append((nr, nc))
        return moves

    # ── legal move filtering ──────────────────────────────────────────────────

    def _would_be_in_check(self, from_r, from_c, to_r, to_c):
        """Return True if making this move would leave own king in check."""
        piece_int = self._sq(from_r, from_c)
        color = self._color(piece_int)

        orig_dst = self._sq(to_r, to_c)
        ep_pos = None
        ep_piece = None

        # En passant: the captured pawn is not on the destination square
        if self._type(piece_int) == PAWN and to_c != from_c and orig_dst is None:
            ep_pos = (from_r, to_c)
            ep_piece = self._sq(from_r, to_c)
            self._set_sq(from_r, to_c, None)

        self._set_sq(to_r, to_c, piece_int)
        self._set_sq(from_r, from_c, None)
        in_check = self.is_in_check(color)
        self._set_sq(from_r, from_c, piece_int)
        self._set_sq(to_r, to_c, orig_dst)
        if ep_pos:
            self._set_sq(ep_pos[0], ep_pos[1], ep_piece)

        return in_check

    def is_in_check(self, color):
        king_r, king_c = self._find_king(color)
        if king_r is None:
            return False
        opponent = BLACK if color == WHITE else WHITE
        for r in range(8):
            for c in range(8):
                p = self._sq(r, c)
                if p is not None and self._color(p) == opponent:
                    if (king_r, king_c) in self._pseudo_legal_moves(r, c):
                        return True
        return False

    def get_legal_moves(self, row, col):
        """All fully legal moves for the piece at (row, col)."""
        legal = []
        for move in self._pseudo_legal_moves(row, col):
            if not self._would_be_in_check(row, col, *move):
                legal.append(move)
        return legal

    def _has_legal_moves(self, color):
        for r in range(8):
            for c in range(8):
                p = self._sq(r, c)
                if p is not None and self._color(p) == color:
                    if self.get_legal_moves(r, c):
                        return True
        return False

    # ── coordinate helpers ────────────────────────────────────────────────────

    def _parse_square(self, text):
        """Convert 'e2' to (row, col), or None if invalid."""
        if len(text) < 2:
            return None
        file_char = text[0].lower()
        rank_num = safe_cast.to_int(text[1])
        if file_char not in self.files or rank_num not in self.ranks:
            return None
        return 8 - rank_num, self.files.index(file_char)

    def _to_notation(self, row, col):
        return f"{self.files[col]}{8 - row}"

    # ── move application ──────────────────────────────────────────────────────

    def apply_move(self, from_r, from_c, to_r, to_c, promotion_type=None):
        """Apply a move, update castling rights, en passant target, and turn."""
        piece_int = self._sq(from_r, from_c)
        pt = self._type(piece_int)
        color = self._color(piece_int)

        # En passant capture: remove the pawn that is not on destination square
        if pt == PAWN and to_c != from_c and self._is_empty(to_r, to_c):
            self._set_sq(from_r, to_c, None)

        self._set_sq(to_r, to_c, piece_int)
        self._set_sq(from_r, from_c, None)

        # Castling: also move the rook
        if pt == KING and abs(to_c - from_c) == 2:
            if to_c == 6:   # kingside
                self._set_sq(to_r, 5, self._sq(to_r, 7))
                self._set_sq(to_r, 7, None)
            else:           # queenside
                self._set_sq(to_r, 3, self._sq(to_r, 0))
                self._set_sq(to_r, 0, None)

        # Update en passant target
        if pt == PAWN and abs(to_r - from_r) == 2:
            self.en_passant_target = ((from_r + to_r) // 2, to_c)
        else:
            self.en_passant_target = None

        # Revoke castling rights
        if pt == KING:
            if color == WHITE:
                self.castling_rights['K'] = self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = self.castling_rights['q'] = False
        elif pt == ROOK:
            revoke = {(7, 7): 'K', (7, 0): 'Q', (0, 7): 'k', (0, 0): 'q'}
            key = revoke.get((from_r, from_c))
            if key:
                self.castling_rights[key] = False

        # Pawn promotion
        if pt == PAWN:
            if color == WHITE and to_r == 0:
                self._set_sq(to_r, to_c, (promotion_type or QUEEN) | WHITE)
            elif color == BLACK and to_r == 7:
                self._set_sq(to_r, to_c, (promotion_type or QUEEN) | BLACK)

        self.move_history.append((from_r, from_c, to_r, to_c))
        self.player = BLACK if self.player == WHITE else WHITE

    # ── game loop ─────────────────────────────────────────────────────────────

    def play(self):
        while True:
            os.system(CLEAR_COMMAND)
            print(self.to_string())
            if self.error:
                print(self.error)
                self.error = ""

            turn_label = "White" if self.player == WHITE else "Black"
            from_input = input(f"{turn_label} — select a piece (e.g. e2): ").strip().lower()

            if from_input == "resign":
                winner = "Black" if self.player == WHITE else "White"
                print(f"{turn_label} resigns. {winner} wins!")
                return

            pos = self._parse_square(from_input)
            if pos is None:
                self.error = "Invalid square — enter like 'e2'."
                continue

            from_r, from_c = pos
            piece_int = self._sq(from_r, from_c)

            if piece_int is None:
                self.error = "No piece on that square."
                continue
            if self._color(piece_int) != self.player:
                self.error = "That piece belongs to your opponent."
                continue

            legal = self.get_legal_moves(from_r, from_c)
            if not legal:
                self.error = "That piece has no legal moves."
                continue

            os.system(CLEAR_COMMAND)
            print(self.to_string(highlighted=legal))
            hints = ", ".join(self._to_notation(r, c) for r, c in sorted(legal))
            print(f"Legal moves: {hints}  (type 'ca' to cancel)")
            to_input = input("Select destination: ").strip().lower()

            if to_input == "ca":
                continue

            dest = self._parse_square(to_input)
            if dest is None or dest not in legal:
                self.error = "Invalid or illegal destination."
                continue

            to_r, to_c = dest
            promotion = None
            if self._type(piece_int) == PAWN:
                if (self.player == WHITE and to_r == 0) or (self.player == BLACK and to_r == 7):
                    promo_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
                    while True:
                        p = input("Promote pawn to (q/r/b/n): ").strip().lower()
                        if p in promo_map:
                            promotion = promo_map[p]
                            break
                        print("Enter q, r, b, or n.")

            self.apply_move(from_r, from_c, to_r, to_c, promotion_type=promotion)

    def to_string(self, highlighted=None):
        """Render the board. highlighted is an optional list of (row, col) targets."""
        hl_set = set(highlighted) if highlighted else set()
        reset = self.color_scheme[None]

        # Determine display order without mutating self.board
        white_view = self.player == WHITE
        row_order = range(8) if white_view else range(7, -1, -1)
        col_order = range(8) if white_view else range(7, -1, -1)

        out = ""
        for i in row_order:
            row = self.board[i]
            for display_j, j in enumerate(col_order):
                sq = row[j]
                piece_int = self._sq(i, j)
                piece_color_offset = 0 if (piece_int is None or self._color(piece_int) == WHITE) else 2
                hl_offset = 4 if (i, j) in hl_set else 0
                color = self.color_scheme.get(piece_color_offset + sq.color + hl_offset)

                if display_j == 0:
                    out += reset + f"{8 - i} "

                out += color + sq.get_piece().to_pretty_string() + reset

            out += "\n"

        # File labels
        out += reset + "   "
        for j in col_order:
            out += f"{self.files[j]}  "

        return out

    def to_fen_string(self):
        fen_type_map = {v: k for k, v in self.fen_map.items()}
        parts = []
        for row in self.board:
            rank_str = ""
            empty = 0
            for square in row:
                p = square.piece
                if p is None:
                    empty += 1
                else:
                    if empty:
                        rank_str += str(empty)
                        empty = 0
                    piece_type = p.piece - (WHITE if p.piece & WHITE == WHITE else BLACK)
                    letter = fen_type_map[piece_type]
                    rank_str += letter.upper() if p.piece & WHITE == WHITE else letter
            if empty:
                rank_str += str(empty)
            parts.append(rank_str)
        return "/".join(parts)

    def from_fen_string(self, string):
        i = 0
        j = 0

        for character in string:
            if character == "/":
                i += 1
                j = 0
                continue
            elif character == "8":
                continue
            elif not can_cast.to_int(character):
                piece = Piece(
                    self.fen_map.get(character.lower()) +
                    (16 if character.isupper() else 8)
                )
                self.board[i][j].set_piece(piece)
                j += 1
            else:
                j += int(character)


class Piece:
    def __init__(self, piece: int = None):
        self.piece = piece

        self.fen_map = {
            1: 'k',
            2: 'q',
            3: 'r',
            4: 'b',
            5: 'n',
            6: 'p'
        }

        self.unicode_map = {
            1: '♚',
            2: '♛',
            3: '♜',
            4: '♝',
            5: '♞',
            6: '♟'
        }

    def get_color(self):
        if self.piece:
            if self.piece & WHITE == WHITE:
                return 0
        return 1

    def to_fen_string(self):
        if self.piece is None:
            return " "
        elif self.piece & WHITE == WHITE:
            return self.fen_map[self.piece - WHITE].upper()
        else:
            return self.fen_map[self.piece - BLACK]

    def to_pretty_string(self):
        if self.piece is None:
            return SPACE + EMPTY_SPACE + SPACE
        elif self.piece & WHITE == WHITE:
            return SPACE + self.unicode_map[self.piece - WHITE] + SPACE
        else:
            return SPACE + self.unicode_map[self.piece - BLACK] + SPACE


class Square:
    def __init__(self, x: int, y: int, piece: Piece = None):
        self.x = x
        self.y = y
        self.color = ((x if y % 2 == 0 else x + 1) % 2)
        self.piece = piece
        self.alphabet_map = {
            1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e',
            6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j',
            11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o',
            16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't',
            21: 'u', 22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z',
        }

    def get_file(self):
        return self.alphabet_map[self.x + 1 % 26]

    def get_rank(self):
        return 8 - self.y

    def get_piece(self):
        if self.piece is None:
            return Piece()
        return self.piece

    def set_piece(self, piece: Piece):
        self.piece = piece


if __name__ == '__main__':
    os.system(CLEAR_COMMAND)
    chess = Chess()
    chess.from_fen_string(chess.starting_position)
    chess.play()
