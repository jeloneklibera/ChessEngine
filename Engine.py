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
        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.moveLog.append(move) #dodanie wykonanego ruchu do logu
        self.whiteToMove = not self.whiteToMove #zmiana tury 
        #aktualizacja pozycji króla po jego ruchu
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_column)
            

    def undo_move(self):
        if len(self.moveLog) != 0: #upewnienie się, że istnieje jakikolwiek ruch, który można cofnąć
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)

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
                    self.move_functions[piece](row, column, moves)
        return moves


    '''
    Pobiera wszystkie ruchy pionków stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_pawn_moves(self, row, column, moves):
        if self.whiteToMove: #zasady ruchu dla białych pionków
            if self.board[row-1][column] == "--": #ruch białego pionka o jedno pole do przodu (w górę szachownicy)
                moves.append(Move((row, column), (row-1, column), self.board))
                if row == 6 and self.board[row-2][column] == "--": #ruch białego pionka o dwa pola do przodu, z pozycji startowej
                    moves.append(Move((row, column), (row-2, column), self.board)) 
            if column - 1 >= 0: #bicie białym pionkiem w lewo
                if self.board[row - 1][column - 1][0] == 'b':  #sprawdzenie czy na polu do bicia stoi czarna figura
                    moves.append(Move((row, column),(row-1, column-1), self.board))
            if column + 1 <= 7: #bicie białym pionkiem w prawo
                if self.board[row -1][column + 1][0] == 'b': #sprawdzenie czy na polu do bicia stoi czarna figura
                    moves.append(Move((row, column), (row-1, column+1), self.board))
        else: #zasady ruchu dla czarnych pionków
            if self.board[row+1][column == "--"]: #ruch białego pionka o jedno pole do przodu (w dół szachownicy)
                moves.append(Move((row, column), (row+1, column), self.board))
                if row == 1 and self.board[row+2][column] == "--": #ruch czarnego pionka o dwa pola do przodu (w dół szachownicy), z pozycji startowej
                    moves.append(Move((row, column), (row+2, column), self.board))
            if column - 1 >=0: #bicie czarnym pionkiem w lewo
                if self.board[row+1][column-1][0] == 'w': #sprawdzenie czy na polu do bicia stoi biała figura
                    moves.append(Move((row, column), (row+1, column-1), self.board))
            if column + 1 <= 7: #bicie czarnym pionkiem w prawo
                if self.board[row+1][column+1][0] == 'w': #sprawdzenie czy na polu do bicia stoi biała figura
                    moves.append(Move((row, column), (row+1, column+1), self.board))


    '''
    Pobiera wszystkie ruchy wież stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_rook_moves(self, row, column, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #góra, lewo, dół, prawo
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions: #sprawdzanie dostępnych pól we wszystkich kierunkach
            for i in range(1, 8): #maksymalna liczba pól o jakie może sie poruszyć to 7
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8: #zapewnienie, że znajdujemy się na planszy
                    stop_square = self.board[end_row][end_column]
                    if stop_square == "--": #puste pole
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif stop_square[0] == enemy_color: #figura przeciwnika, sprawdzanie po pierwszej literze: [0]
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break
                    else: #własna figura
                        break
                else: #sytuacja, gdy pola są poza planszą
                    break

    '''
    Pobiera wszystkie ruchy skoczków stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_knight_moves(self, row, column, moves):
        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)) #pola na które może skoczyć skoczek, w kształcie litery L
        own_color = "w" if self.whiteToMove else "b" #figura tego samego koloru
        for m in knight_moves:
            end_row = row + m[0]
            end_column = column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8: #warunek pozostawania na szachownicy
                stop_square = self.board[end_row][end_column]
                if stop_square[0] != own_color: #puste pole lub figura przeciwnika
                    moves.append(Move((row, column), (end_row, end_column), self.board))

    '''
    Pobiera wszystkie ruchy gońców stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_bishop_moves(self, row, column, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #określenie kierunków po przekątnych
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions: #sprawdzanie dostępnych pól we wszystkich określonych kierunkach
            for i in range(1, 8): #maksymalna liczba pól o jakie może sie poruszyć to 7
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:  #zapewnienie, że znajdujemy się na planszy
                    stop_square = self.board[end_row][end_column]
                    if stop_square == "--": #puste pole
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif stop_square[0] == enemy_color: #figura przeciwnika, sprawdzanie po pierwszej literze: [0]
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break
                    else: #własna figura
                        break 
                else:  #sytuacja, gdy pola są poza planszą
                    break

        '''
    Pobiera wszystkie ruchy królowych stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

        '''
    Pobiera wszystkie ruchy króli stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_king_moves(self, row, column, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, 1), (1, -1)) #pola na które może przejść król, wszystkie przyległe do obecnej pozycji
        own_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + king_moves[i][0]
            end_column = column + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                stop_square = self.board[end_row][end_column]
                if stop_square != own_color:
                    moves.append(Move((row, column), (end_row, end_column), self.board))

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