from __init__ import Chess, WHITE, BLACK


def sq(notation):
    files = list("abcdefgh")
    return 8 - int(notation[1]), files.index(notation[0])


class TestCheckmate:
    def test_scholars_mate(self):
        """White delivers Scholar's mate."""
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        # 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6?? 4. Qxf7#
        moves = [
            ("e2", "e4"), ("e7", "e5"),
            ("f1", "c4"), ("b8", "c6"),
            ("d1", "h5"), ("g8", "f6"),
            ("h5", "f7"),
        ]
        for fr, to in moves:
            g.apply_move(*sq(fr), *sq(to))
        assert g.is_in_check(g.player)
        assert not g._has_legal_moves(g.player)

    def test_fool_s_mate(self):
        """Black delivers Fool's mate."""
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        moves = [
            ("f2", "f3"), ("e7", "e5"),
            ("g2", "g4"), ("d8", "h4"),
        ]
        for fr, to in moves:
            g.apply_move(*sq(fr), *sq(to))
        assert g.is_in_check(g.player)
        assert not g._has_legal_moves(g.player)


class TestStalemate:
    def test_simple_stalemate(self):
        # Black king on a8, White queen on b6, White king on c6 — Black to move
        g = Chess()
        g.from_fen_string("k7/8/1QK5/8/8/8/8/8")
        g.player = BLACK
        assert not g.is_in_check(BLACK)
        assert not g._has_legal_moves(BLACK)

    def test_not_stalemate_when_moves_exist(self):
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        assert g._has_legal_moves(WHITE)


class TestCheckDetectionInGame:
    def test_check_flag_after_move(self):
        # After Qh5 in Scholar's mate line, black is not in check yet
        g = Chess()
        g.from_fen_string("rnbqkbnr/pppp1ppp/8/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR")
        g.player = BLACK
        assert not g.is_in_check(BLACK)

    def test_check_after_discovered_attack(self):
        # Rook on d1, pawn on d4 blocking, king on d8; pawn captures off d-file → discovered check
        g = Chess()
        g.from_fen_string("3k4/8/8/4p3/3P4/8/8/3R4")
        g.apply_move(*sq("d4"), *sq("e5"))
        assert g.is_in_check(g.player)
