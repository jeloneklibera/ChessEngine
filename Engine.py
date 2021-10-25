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


    '''
    Wszystkie ruchy, które mogą dać szacha
    '''
    def get_valid_moves(self):
        return self.get_all_possible_moves()

    '''
    Wszystkie ruchy, które nie mogą dać szacha
    '''
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)): #iteracja po rzędach
            for column in range(len(self.board[row])): #iteracja po kolumnach w danym rzędzie
                turn = self.board[row][column][0]  #w celu określenia koloru figury, pobiera pierwszą literę z oznaczenia figury (b: black, w: white, -: puste pole)
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1] #w celu określenia rodzaju figury, pobiera drugą literę z oznaczenia figury
                    if piece == 'p':
                        self.get_pawn_moves(row, column, moves)
                    elif piece == 'R':
                        self.get_rook_moves(row, column, moves)
        return moves


    '''
    Pobiera wszystkie ruchy pionków stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_pawn_moves(self, row, column, moves):
        if self.whiteToMove: #zasady ruchu dla białych pionków
            if self.board[row-1][column] == "--": #ruch białego pionka o jedno pole do przodu
                moves.append(Move((row, column), (row-1, column), self.board))
                if row == 6 and self.board[row-2][column] == "--": #ruch białego pionka o dwa pola do przodu, z pozycji startowej
                    moves.append(Move((row, column), (row-2, column), self.board)) 
            if column - 1 >= 0: #bicie białym pionkiem w lewo
                if self.board[row - 1][column - 1][0] == 'b':  #sprawdzenie czy na polu do bicia stoi czarna figura
                    moves.append(Move((row, column),(row-1, column-1), self.board))
            if column + 1 <= 7: #bicie białym pionkiem w prawo
                if self.board[row -1][column + 1][0] == 'b': #sprawdzenie czy na polu do bicia stoi czarna figura
                    moves.append(Move((row, column), (row-1, column+1), self.board))
            


    '''
    Pobiera wszystkie ruchy wież stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_rook_moves(self, row, column, moves):
        pass


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
        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column #unikalne ID ruchu
        



    '''
    Przesłanianie metody równościowej
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        #TODO: Zmodyfikowac metode, aby notacja przypominala jeszcze bardziej prawdziwa notacje szachowa
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)



    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]