"""Klasa odpowiedzialna za przechowywanie wszystkich informacji dotyczących stanu gry
Odpowiada również za określanie legalnych ruchów przy danym stanie gry
Zawiera log z wykonanymi ruchami
"""

class GameState():
    def __init__(self):
        #Reprezentacja planszy przy pomocy 8x8 2d listy, każdy element listy składa się z 2 znaków
        #Pierwszy znak reprezentuje kolor danej figury: b-black, w-white
        #Drugi znak reprezentuje rodzaj figury: R - Rook, N - Knight, B - Bishop, Q - Queen, K - King, p - pawn
        # "--" oznacza niezajęte pole na szachownicy
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], 
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--","--", "--","--", "--"],
            ["--", "--", "--", "--","--", "--","--", "--"],
            ["--", "--", "--", "--","--", "--","--", "--"],
            ["--", "--", "--", "--","--", "--","--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []


    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.moveLog.append(move) #dodanie wykonanego ruchu do logu
        self.whiteToMove = not self.whiteToMove #zmiana tury 


    def undo_move(self):
        if len(self.moveLog) != 0: #upewnienie się, że istnieje jakikolwiek ruch, który można cofnąć
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.whiteToMove = not self.whiteToMove


class Move():
    
    # mapowanie kluczy na wartości
    # klucz : wartość
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b" : 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}



    def __init__(self, startSq, endSq, board):
        self.start_row = startSq[0]
        self.start_column = startSq[1]
        self.end_row = endSq[0]
        self.end_column = endSq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]


    def get_chess_notation(self):
        #TODO: Zmodyfikowac metode, aby notacja przypominala jeszcze bardziej prawdziwa notacje szachowa
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)



    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]