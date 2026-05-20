from __init__ import Chess, PAWN, WHITE, BLACK


def sq(notation):
    files = list("abcdefgh")
    return 8 - int(notation[1]), files.index(notation[0])


class TestEnPassant:
    def test_white_en_passant_capture(self):
        """White pawn on e5 captures black pawn that just double-pushed to d5."""
        g = Chess()
        g.from_fen_string("8/3p4/8/4P3/8/8/8/8")
        g.player = BLACK
        g.apply_move(*sq("d7"), *sq("d5"))   # Black double push sets en_passant_target = d6
        assert g.en_passant_target == sq("d6")

        # White's e5 pawn should now see d6 as a legal move
        legal = g.get_legal_moves(*sq("e5"))
        assert sq("d6") in legal

        g.apply_move(*sq("e5"), *sq("d6"))   # White captures en passant
        assert g._sq(*sq("d6")) == PAWN | WHITE
        assert g._sq(*sq("d5")) is None      # Captured pawn is gone
        assert g._sq(*sq("e5")) is None

    def test_black_en_passant_capture(self):
        """Black pawn on d4 captures white pawn that just double-pushed to e4."""
        g = Chess()
        g.from_fen_string("8/8/8/8/3p4/8/4P3/8")
        g.apply_move(*sq("e2"), *sq("e4"))   # White double push
        assert g.en_passant_target == sq("e3")

        legal = g.get_legal_moves(*sq("d4"))
        assert sq("e3") in legal

        g.apply_move(*sq("d4"), *sq("e3"))
        assert g._sq(*sq("e3")) == PAWN | BLACK
        assert g._sq(*sq("e4")) is None       # Captured white pawn removed
        assert g._sq(*sq("d4")) is None

    def test_en_passant_not_available_after_other_move(self):
        """En passant right expires if the next move is something else."""
        g = Chess()
        g.from_fen_string("8/3p4/8/4P3/8/8/8/4R3")
        g.player = BLACK
        g.apply_move(*sq("d7"), *sq("d5"))   # Black double push
        g.apply_move(*sq("e1"), *sq("e2"))   # White plays something else
        # En passant target should be cleared
        assert g.en_passant_target is None
        legal = g.get_legal_moves(*sq("e5"))
        assert sq("d6") not in legal

    def test_en_passant_target_set_only_for_double_push(self):
        """Single pawn push does not set en passant target."""
        g = Chess()
        g.from_fen_string("8/3p4/8/4P3/8/8/8/8")
        g.player = BLACK
        g.apply_move(*sq("d7"), *sq("d6"))   # Single push
        assert g.en_passant_target is None
