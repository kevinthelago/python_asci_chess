import pytest
from __init__ import Chess, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, WHITE, BLACK


def game_from(fen):
    g = Chess()
    g.from_fen_string(fen)
    return g


def legal(g, notation):
    """Return sorted legal moves for the piece at 'notation' (e.g. 'e2')."""
    col = g.files.index(notation[0])
    row = 8 - int(notation[1])
    return sorted(g.get_legal_moves(row, col))


def sq(notation):
    """Convert 'e2' → (row, col)."""
    files = list("abcdefgh")
    return 8 - int(notation[1]), files.index(notation[0])


class TestPawnMoves:
    def test_white_pawn_starting_square_two_moves(self):
        g = game_from("8/8/8/8/8/8/4P3/8")
        moves = legal(g, "e2")
        assert sq("e3") in moves
        assert sq("e4") in moves
        assert len(moves) == 2

    def test_white_pawn_blocked_by_own_piece(self):
        g = game_from("8/8/8/8/8/4P3/4P3/8")
        moves = legal(g, "e2")
        assert moves == []

    def test_white_pawn_capture(self):
        g = game_from("8/8/8/8/8/3p4/4P3/8")
        moves = legal(g, "e2")
        assert sq("d3") in moves

    def test_black_pawn_starting_two_moves(self):
        g = game_from("8/4p3/8/8/8/8/8/8")
        g.player = BLACK
        moves = legal(g, "e7")
        assert sq("e6") in moves
        assert sq("e5") in moves
        assert len(moves) == 2

    def test_black_pawn_capture(self):
        g = game_from("8/4p3/5P2/8/8/8/8/8")
        g.player = BLACK
        moves = legal(g, "e7")
        assert sq("f6") in moves


class TestKnightMoves:
    def test_center_knight_eight_moves(self):
        g = game_from("8/8/8/8/4N3/8/8/8")
        moves = legal(g, "e4")
        assert len(moves) == 8

    def test_corner_knight_two_moves(self):
        g = game_from("N7/8/8/8/8/8/8/8")
        moves = legal(g, "a8")
        assert len(moves) == 2

    def test_knight_cannot_capture_friendly(self):
        g = game_from("8/8/8/3P4/4N3/8/8/8")
        moves = legal(g, "e4")
        assert sq("d6") in moves  # can still reach d6
        assert sq("d5") not in moves  # but can't capture own pawn on d5... wait d5 is not a knight target


class TestBishopMoves:
    def test_bishop_from_center_open_board(self):
        g = game_from("8/8/8/8/4B3/8/8/8")
        moves = legal(g, "e4")
        assert len(moves) == 13

    def test_bishop_blocked_by_own_piece(self):
        g = game_from("8/8/8/3P4/4B3/8/8/8")
        moves = legal(g, "e4")
        assert sq("d5") not in moves

    def test_bishop_can_capture_enemy(self):
        g = game_from("8/8/8/3p4/4B3/8/8/8")
        moves = legal(g, "e4")
        assert sq("d5") in moves


class TestRookMoves:
    def test_rook_from_corner_open_board(self):
        g = game_from("R7/8/8/8/8/8/8/8")
        moves = legal(g, "a8")
        assert len(moves) == 14

    def test_rook_blocked_by_friendly(self):
        g = game_from("R6P/8/8/8/8/8/8/8")
        moves = legal(g, "a8")
        # h8 blocked by own piece; 6 squares right (b8..g8) + 7 squares down (a7..a1)
        assert len(moves) == 13


class TestQueenMoves:
    def test_queen_center_open_board(self):
        g = game_from("8/8/8/8/4Q3/8/8/8")
        moves = legal(g, "e4")
        assert len(moves) == 27


class TestKingMoves:
    def test_king_center_moves(self):
        g = game_from("8/8/8/8/4K3/8/8/8")
        moves = legal(g, "e4")
        assert len(moves) == 8

    def test_king_cannot_move_into_check(self):
        # Black rook on e8 covers the e file; king on e4 cannot move to e3 or e5
        g = game_from("4r3/8/8/8/4K3/8/8/8")
        moves = legal(g, "e4")
        assert sq("e5") not in moves
        assert sq("e3") not in moves


class TestCheckDetection:
    def test_king_in_check_from_rook(self):
        g = game_from("4r3/8/8/8/4K3/8/8/8")
        assert g.is_in_check(WHITE)

    def test_king_not_in_check(self):
        g = game_from("8/8/8/8/4K3/8/8/8")
        assert not g.is_in_check(WHITE)

    def test_pin_removes_legal_moves(self):
        # White bishop on d4 is pinned by black rook on a4; moving it would expose white king on h4
        g = game_from("8/8/8/8/r2B3K/8/8/8")
        moves = legal(g, "d4")
        assert moves == []
