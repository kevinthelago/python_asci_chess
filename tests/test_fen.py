from __init__ import Chess, Piece, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, WHITE, BLACK


def make_game():
    g = Chess()
    g.from_fen_string(g.starting_position)
    return g


def piece_at(game, row, col):
    """Return the Piece object at (row, col) or None."""
    return game.board[row][col].piece


def piece_int(game, row, col):
    """Return the raw integer for the piece at (row, col), or None."""
    p = piece_at(game, row, col)
    return p.piece if p is not None else None


class TestFromFenString:
    def test_white_pieces_on_rank_1(self):
        g = make_game()
        assert piece_int(g, 7, 0) == ROOK | WHITE
        assert piece_int(g, 7, 1) == KNIGHT | WHITE
        assert piece_int(g, 7, 2) == BISHOP | WHITE
        assert piece_int(g, 7, 3) == QUEEN | WHITE
        assert piece_int(g, 7, 4) == KING | WHITE
        assert piece_int(g, 7, 5) == BISHOP | WHITE
        assert piece_int(g, 7, 6) == KNIGHT | WHITE
        assert piece_int(g, 7, 7) == ROOK | WHITE

    def test_white_pawns_on_rank_2(self):
        g = make_game()
        for col in range(8):
            assert piece_int(g, 6, col) == PAWN | WHITE

    def test_black_pieces_on_rank_8(self):
        g = make_game()
        assert piece_int(g, 0, 0) == ROOK | BLACK
        assert piece_int(g, 0, 1) == KNIGHT | BLACK
        assert piece_int(g, 0, 2) == BISHOP | BLACK
        assert piece_int(g, 0, 3) == QUEEN | BLACK
        assert piece_int(g, 0, 4) == KING | BLACK
        assert piece_int(g, 0, 5) == BISHOP | BLACK
        assert piece_int(g, 0, 6) == KNIGHT | BLACK
        assert piece_int(g, 0, 7) == ROOK | BLACK

    def test_black_pawns_on_rank_7(self):
        g = make_game()
        for col in range(8):
            assert piece_int(g, 1, col) == PAWN | BLACK

    def test_empty_ranks(self):
        g = make_game()
        for row in range(2, 6):
            for col in range(8):
                assert piece_int(g, row, col) is None

    def test_custom_fen(self):
        g = Chess()
        g.from_fen_string("8/8/8/8/8/8/8/4K3")
        assert piece_int(g, 7, 4) == KING | WHITE
        for row in range(7):
            for col in range(8):
                assert piece_int(g, row, col) is None
        for col in range(8):
            if col != 4:
                assert piece_int(g, 7, col) is None
