from __init__ import Chess, ROOK, WHITE, BLACK


def sq(notation):
    files = list("abcdefgh")
    return 8 - int(notation[1]), files.index(notation[0])


class TestCastling:
    def test_white_kingside_allowed(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/4K2R")
        assert sq("g1") in g.get_legal_moves(*sq("e1"))

    def test_white_queenside_allowed(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/R3K3")
        assert sq("c1") in g.get_legal_moves(*sq("e1"))

    def test_black_kingside_allowed(self):
        g = Chess()
        g.from_fen_string("4k2r/8/8/8/8/8/8/8")
        g.player = BLACK
        assert sq("g8") in g.get_legal_moves(*sq("e8"))

    def test_black_queenside_allowed(self):
        g = Chess()
        g.from_fen_string("r3k3/8/8/8/8/8/8/8")
        g.player = BLACK
        assert sq("c8") in g.get_legal_moves(*sq("e8"))

    def test_castling_blocked_by_piece_between(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/4K1NR")
        assert sq("g1") not in g.get_legal_moves(*sq("e1"))

    def test_castling_not_allowed_while_in_check(self):
        # King in check from black rook on e8
        g = Chess()
        g.from_fen_string("4r3/8/8/8/8/8/8/4K2R")
        assert sq("g1") not in g.get_legal_moves(*sq("e1"))

    def test_castling_not_allowed_through_attacked_square(self):
        # Black rook on f8 covers f1 — kingside castling path is attacked
        g = Chess()
        g.from_fen_string("5r2/8/8/8/8/8/8/4K2R")
        assert sq("g1") not in g.get_legal_moves(*sq("e1"))

    def test_castling_not_allowed_into_check(self):
        # Black rook on g8 covers g1 — landing square is attacked
        g = Chess()
        g.from_fen_string("6r1/8/8/8/8/8/8/4K2R")
        assert sq("g1") not in g.get_legal_moves(*sq("e1"))

    def test_castling_rights_revoked_prevents_castling(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/4K2R")
        g.castling_rights['K'] = False
        assert sq("g1") not in g.get_legal_moves(*sq("e1"))

    def test_castling_moves_rook(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/4K2R")
        g.apply_move(*sq("e1"), *sq("g1"))
        assert g._sq(*sq("f1")) == ROOK | WHITE
        assert g._sq(*sq("h1")) is None
        assert g._sq(*sq("g1")) is not None
        assert g._sq(*sq("e1")) is None

    def test_queenside_castling_moves_rook(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/R3K3")
        g.apply_move(*sq("e1"), *sq("c1"))
        assert g._sq(*sq("d1")) == ROOK | WHITE
        assert g._sq(*sq("a1")) is None
