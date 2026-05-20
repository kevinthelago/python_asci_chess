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

EMPTY_SPACE = " "
SPACE = " "

BLACK_AND_WHITE_COLOR_SCHEME = {
    0: "\033[48;2;200;200;200;38;2;255;255;255m",  # 00
    1: "\033[48;2;50;50;50;38;2;255;255;255m",     # 01
    2: "\033[48;2;200;200;200;38;2;0;0;0m",        # 10
    3: "\033[48;2;50;50;50;38;2;0;0;0m",           # 11
    None: "\033[48;2;0;0;0;38;2;50;255;255m"
}


class Chess:
    starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    player = WHITE
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
        self.error = ""

    def play(self):
        print(chess.to_string())  # <-- ToDo: Figure out why colors are weird in bash; render twice = bad

        while True:
            os.system(CLEAR_COMMAND)

            print(chess.to_string())
            print(self.error)
            piece = input("Select a piece: ")

            if piece[:1] not in self.fen_map.keys():
                self.error = f"Not a correct piece selection. Please select from these options: {' '.join(self.fen_map.keys())}"
                continue
            if piece[1:2] not in self.files:
                self.error = f"Not a correct file selection. Please select from these options: {self.files}"
                continue
            if safe_cast.to_int(piece[2:3]) not in self.ranks:
                self.error = f"Not a correct rank selection. Please select from these options: {self.ranks}"
                continue

            starting_square = self.board[safe_cast.to_int(piece[2:3]) - 1][self.files.index(piece[1:2])]
            # ToDo:
            #  Grab square from matrix
            #  verify piece selection
            #  calculate legal moves

            square = input("Select a square or type ca to ca: ")

            if square[:2] == "ca":
                continue
            if square[:1] not in self.files:
                self.error = f"Not a correct file selection. Please select from these options: {self.files}"
                continue
            if safe_cast.to_int(square[1:2]) not in self.ranks:
                self.error = f"Not a correct rank selection. Please select from these options: {self.ranks}"
                continue

            self.error = ""

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

    def to_string(self):
        if self.player & WHITE != WHITE:
            self.board.reverse()
            for rank in self.board:
                rank.reverse()

        board = ""
        reset_color = self.color_scheme.get(None)

        for i, row in enumerate(self.board):
            for j, column in enumerate(row):
                piece_color = 0
                if column.get_piece() is not None:
                    piece_color = column.get_piece().get_color() << 1
                color = self.color_scheme.get(piece_color + column.color)

                if j == 0:
                    board += reset_color + f"{row[0].get_rank()} "

                board += color + column.get_piece().to_pretty_string() + reset_color

            board += "\n" + reset_color

            if i == 7:
                for j in range(8):
                    if j == 0:
                        board += " 　"
                    board += reset_color + f"{self.board[i][j].get_file()}　"

        return board


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
            1: 'a',
            2: 'b',
            3: 'c',
            4: 'd',
            5: 'e',
            6: 'f',
            7: 'g',
            8: 'h',
            9: 'i',
            10: 'j',
            11: 'k',
            12: 'l',
            13: 'm',
            14: 'n',
            15: 'o',
            16: 'p',
            17: 'q',
            18: 'r',
            19: 's',
            20: 't',
            21: 'u',
            22: 'v',
            23: 'w',
            24: 'x',
            25: 'y',
            26: 'z',
        }

    def get_file(self):
        return self.alphabet_map[self.x + 1 % 26]

    def get_rank(self):
        return 8 - self.y

    def get_piece(self):
        # ToDo: See if this affects memory
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
