# python_ascii_chess

A two-player console chess game written in Python, rendered entirely in the terminal using Unicode chess pieces and ANSI color codes.

```
8  ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜
7  ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟
6                          
5                          
4                          
3                          
2  ♙  ♙  ♙  ♙  ♙  ♙  ♙  ♙
1  ♖  ♘  ♗  ♕  ♔  ♗  ♘  ♖
   a　 b　 c　 d　 e　 f　 g　 h
```

## Requirements

- Python 3.8+
- A terminal with ANSI color support (Windows Terminal, iTerm2, most Linux terminals)

## Running the Game

```bash
python src/python_asci_chess/__init__.py
```

## How to Play

The game uses a text-based input system:

1. **Select a piece** — enter the piece type, file, and rank (e.g., `pa2` to select the pawn on a2)

   | Code | Piece  |
   |------|--------|
   | `k`  | King   |
   | `q`  | Queen  |
   | `r`  | Rook   |
   | `b`  | Bishop |
   | `n`  | Knight |
   | `p`  | Pawn   |

2. **Select a destination square** — enter the file and rank (e.g., `a4`)
3. Type `ca` at the destination prompt to cancel and re-select a piece.

## Project Status

This project is under active development. The board renders correctly and FEN position loading works. The following features are still in progress:

- [ ] Legal move validation for all piece types
- [ ] Move execution and turn alternation
- [ ] Check, checkmate, and stalemate detection
- [ ] Castling and en passant
- [ ] Pawn promotion
- [ ] Highlighted legal moves

See the [open issues](https://github.com/kevinthelago/python_asci_chess/issues) for the full task list.

## Architecture

```
src/python_asci_chess/
├── __init__.py          # Chess, Piece, and Square classes; game entry point
└── util/
    ├── ansi_escape_codes.py   # ANSI terminal escape code reference
    ├── can_cast.py            # Type-check helpers (returns bool)
    └── safe_cast.py           # Safe type conversion helpers (returns value or default)
```

**Key design decisions:**

- Pieces are encoded as integers using bitwise flags: `piece_type | color` (e.g., `PAWN | WHITE = 6 | 16 = 22`)
- Board positions use FEN notation for loading and saving game state
- The board is a row-major 8×8 matrix of `Square` objects, each optionally holding a `Piece`
- ANSI escape codes are used for square and piece coloring; color schemes are swappable via a dict

## License

MIT
