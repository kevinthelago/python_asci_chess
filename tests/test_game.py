from __init__ import Chess, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, WHITE, BLACK


def game_from(fen, player=WHITE):
    g = Chess()
    g.from_fen_string(fen)
    g.player = player
    return g


def sq(notation):
    files = list("abcdefgh")
    return 8 - int(notation[1]), files.index(notation[0])


class TestApplyMove:
    def test_pawn_advances(self):
        g = game_from("8/8/8/8/8/8/4P3/8")
        g.apply_move(*sq("e2"), *sq("e4"))
        assert g._sq(*sq("e4")) == PAWN | WHITE
        assert g._sq(*sq("e2")) is None

    def test_turn_alternates(self):
        g = game_from(Chess.starting_position)
        assert g.player == WHITE
        g.apply_move(*sq("e2"), *sq("e4"))
        assert g.player == BLACK

    def test_capture(self):
        g = game_from("8/8/8/3p4/4P3/8/8/8")
        g.apply_move(*sq("e4"), *sq("d5"))
        assert g._sq(*sq("d5")) == PAWN | WHITE
        assert g._sq(*sq("e4")) is None

    def test_en_passant_target_set(self):
        g = game_from("8/8/8/8/8/8/4P3/8")
        g.apply_move(*sq("e2"), *sq("e4"))
        assert g.en_passant_target == sq("e3")

    def test_en_passant_target_cleared_on_other_move(self):
        g = game_from("8/8/8/8/8/8/4P3/8")
        g.apply_move(*sq("e2"), *sq("e4"))
        g.player = WHITE
        g.apply_move(*sq("e4"), *sq("e5"))
        assert g.en_passant_target is None

    def test_castling_rights_revoked_on_king_move(self):
        g = game_from("8/8/8/8/8/8/8/4K3")
        g.apply_move(*sq("e1"), *sq("f1"))
        assert g.castling_rights['K'] is False
        assert g.castling_rights['Q'] is False

    def test_castling_rights_revoked_on_rook_move(self):
        g = game_from("8/8/8/8/8/8/8/R3K2R")
        g.apply_move(*sq("h1"), *sq("h2"))
        assert g.castling_rights['K'] is False
        assert g.castling_rights['Q'] is True

    def test_pawn_promotion_defaults_to_queen(self):
        g = game_from("8/4P3/8/8/8/8/8/8")
        g.apply_move(*sq("e7"), *sq("e8"))
        assert g._sq(*sq("e8")) == QUEEN | WHITE

    def test_pawn_promotion_to_rook(self):
        g = game_from("8/4P3/8/8/8/8/8/8")
        g.apply_move(*sq("e7"), *sq("e8"), promotion_type=ROOK)
        assert g._sq(*sq("e8")) == ROOK | WHITE

    def test_move_recorded_in_history(self):
        g = game_from(Chess.starting_position)
        g.apply_move(*sq("e2"), *sq("e4"))
        assert len(g.move_history) == 1
        assert g.move_history[0] == (*sq("e2"), *sq("e4"))


class TestParseSquare:
    def test_valid_square(self):
        g = Chess()
        assert g._parse_square("e2") == (6, 4)
        assert g._parse_square("a1") == (7, 0)
        assert g._parse_square("h8") == (0, 7)

    def test_invalid_returns_none(self):
        g = Chess()
        assert g._parse_square("z9") is None
        assert g._parse_square("") is None
        assert g._parse_square("e") is None


class TestToString:
    def test_returns_string(self):
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        result = g.to_string()
        assert isinstance(result, str)

    def test_contains_rank_labels(self):
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        result = g.to_string()
        for rank in "12345678":
            assert rank in result

    def test_does_not_mutate_board(self):
        g = Chess()
        g.from_fen_string(Chess.starting_position)
        g.player = BLACK
        before = g._sq(0, 0)
        g.to_string()
        assert g._sq(0, 0) == before
