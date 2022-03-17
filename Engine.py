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
        self.is_in_check = False
        self.pins = []
        self.checks = []
        self.check_mate = False
        self.stale_mate = False
        self.en_passant_possible = () #współrzędne pola, na którym jest możliwe bicie w przelocie
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs, self.current_castling_rights.bks)]


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
        #jeśli pionek porusza się o dwa pola, następny ruch może być biciem enpassant
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.end_row + move.start_row) // 2, move.end_column)
        else:
            self.en_passant_possible = ()
        #jeśli ruch jest biciem enpassant, trzeba zaktualizować szachownicę aby zbić pionka
        if move.en_passant:
            self.board[move.start_row][move.end_column] = "--"
        #promocja pionów
        if move.pawn_promotion:
            promoted_piece = "Q" #TO-DO do wykorzystania przy rozwijaniu UI
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + promoted_piece
        #roszada
        if move.is_castle_move:
            if move.end_column - move.start_column == 2: #król dokonuje roszady na skrzydle królewskim
                self.board[move.end_row][move.end_column-1] = self.board[move.end_row][move.end_column+1] #jedno pole po lewej od króla po roszadzie = wieża (która znajdowała się jedno pole po prawej od pola na którym wylądował króla po roszadzie)
                self.board[move.end_row][move.end_column+1] = "--" #wyczyszczenie pola na którym znajdowała się wieża przed roszadą
            else: #roszada na skrzydle hetmańskim
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-2] #jedno pole po prawej od króla po roszadzie = wieża (która znajdowała się dwa pola po lewej od pola na którym wylądował króla po roszadzie)
                self.board[move.end_row][move.end_column-2] = "--"
        #aktualizacja praw do roszady - w przypadk ruchu którejś z wież lub króli
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs, self.current_castling_rights.bks))



    def undo_move(self):
        if len(self.moveLog) != 0: #upewnienie się, że istnieje jakikolwiek ruch, który można cofnąć
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
            #aktualizacja pozycji króla po cofnięciu jego ruchu
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_column)
            #aktualizacja po ruchu enpassant
            if move.en_passant:
                self.board[move.end_row][move.end_column] = "--" #Usuwa pionka, który został dodany na niewłaściwym polu
                self.board[move.start_row][move.end_column] = move.piece_captured #Ustawia z powrotem pionka na polu z którego nastąpiło bicie
                self.en_passant_possible = (move.end_row, move.end_column) #Dzięki temu mozliwy jest ruch enpassant po cofnięciu ruchu
            #Cofnięcie ruchu o dwa pola, oraz dodanie możliwości na ponowne bicie enpassant po cofnięciu
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()
            #Cofnięcie stanu praw do roszady
            self.castle_rights_log.pop() #skasowanie praw do roszady, które były następstwem ruchu, który cofamy
            self.current_castling_rights  = self.castle_rights_log[-1] #ustawienie aktualnych praw do roszady, jako ostatni element listy (z której usunęliśmy wyżej ostatni element)
            #Cofnięcie roszady
            if move.is_castle_move:
                if move.end_column - move.start_column == 2: #roszada na skrzydle królewskim
                    self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-1] #wieża z pozycji po roszadzie na skrzydle królewskim wraca na pierwotne pole w rogu szachownicy
                    self.board[move.end_row][move.end_column-1] = "--" #wyczyszczenie pola na którym stała wieża po roszadzie na skrzydle królewskim
                else: #roszada na skrzydle hetmańskim
                    self.board[move.end_row][move.end_column-2] = self.board[move.end_row][move.end_column+1] #wieża z pozycji po roszadzie na skrzydle hetmańskim wraca na pierwotne pole w rogu szachownicy
                    self.board[move.end_row][move.end_column+1] = "--" #wyczyszczenie pola na którym stała wieża po roszadzie na skrzydle hetmańskim
   
            self.check_mate = False
            self.stale_mate = False
   
   
    """
    Aktualizuje zasady dotyczące roszady dostając na wejściu dany ruch
    """
    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_column == 0: #wieża na białym skrzydle hetmańskim
                    self.current_castling_rights.wqs = False 
                elif move.start_column == 7: #wieża na białym skrzydle królewskim
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_column == 0: #wieża na czarnym skrzydle hetmańskim
                    self.current_castling_rights.bqs = False
                elif move.start_column == 7: #wieża na czarnym skrzydle królewskim
                    self.current_castling_rights.bks = False

        #gdy wieża jest zbita
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_column == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_column == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_column == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_column == 7:
                    self.current_castling_rights.bks = False



    '''
    Wszystkie ruchy, które mogą dać szacha
    '''
    def get_valid_moves(self):
        moves = []
        self.is_in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks, self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        if self.whiteToMove:
            king_row = self.white_king_location[0]
            king_column = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_column = self.black_king_location[1]
        if self.is_in_check:
            if len(self.checks) == 1: #tylko jedna figura szachuje króla, zablokuj szacha lub porusz się królem
                moves = self.get_all_possible_moves()
                #Aby zablokować szacha powinno się mieć jakąś figurę pomiędzy przeciwną figurą dającą szacha a królem
                check = self.checks[0]
                check_row = check[0]
                check_column = check[1]
                piece_checking = self.board[check_row][check_column] #przeciwna figura dająca szacha
                valid_squares = [] #pola, na które może przejść figura
                #gdy figurą szachującą jest przeciwny skoczek, należy zbić skoczka lub ruszyć się królem, szach ze strony pozostałych figur można zablokować
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_column)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_column + check[3] * i) #check[2] oraz check[3] są to kierunki z których pochodzi szach
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_column: #zbicie szachującej figury, kończy szacha
                            break
                #pozbycie się ruchów, które nie blokują szacha lub ruszenia królem
                for i in range(len(moves)- 1, -1, -1): #w przypadku usuwania z listy bardziej opłaca się iterować od końca listy
                    if moves[i].piece_moved[1] != "K": #ruch, który nie był poruszeniem się królem, zatem blokujący lub bijący figurę szachującą
                        if not(moves[i].end_row, moves[i].end_column) in valid_squares: #ruchy, które nie blokują szacha lub nie biją figury szachującej
                            moves.remove(moves[i])
            else: #podwójny szach, wymagany ruch króla
                self.get_king_moves(king_row, king_column, moves)
        else: #nie ma szacha, wszystkie legalne ruchy dozwolone
            moves = self.get_all_possible_moves()
             

        if len(moves) == 0:
            if self.is_in_check:
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False
        if self.whiteToMove:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        self.current_castling_rights = temp_castle_rights
        return moves

                    

    def check_for_pins_and_checks(self):
        pins = [] #pola na których znajduje się włana związana figura oraz kierunek powodujący związanie
        checks = [] #pola które są szachowane przez przeciwnika
        is_in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_column = self.white_king_location[1]
        else: 
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_column = self.black_king_location[1]
        #sprawdzenie pól na kierunkach króla pod kątem związań i szachów, śledzenie związań
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #resetowanie możliwych związań
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_column = start_column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    stop_square = self.board[end_row][end_column] #figura na którą napotykamy sprawdzając kierunki wychodzące od króla
                    if stop_square[0] == ally_color and stop_square[1] != "K":
                        if possible_pin == (): #pierwsza własna figura- może być związana
                            possible_pin = (end_row, end_column, d[0], d[1])
                        else: #druga własna figura, zatem nie ma mowy o związaniu lub szachu
                            break
                    elif stop_square[0] == enemy_color:
                        type_of_piece = stop_square[1]
                        #5 możliwych scenariuszy:
                        # 1): prostopadle do króla i wrogą figurą jest wieża
                        # 2): po przekątnej od króla i wrogą figurą jest goniec
                        # 3) jedno pole po przekątnej od króla i wrogą figurą jest pionek
                        # 4) dowolny kierunek od króla i wrogą figurą jest królowa
                        # 5) dowolny kierunek i odległość jedno pole od króla i wrogą figurą jest król
                        if (0 <= j <= 3 and type_of_piece == "R") or \
                                (4 <= j <= 7 and type_of_piece == "B") or \
                                (i == 1 and type_of_piece == "p" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or \
                                (type_of_piece == "Q") or (i == 1 and type_of_piece == "K"):
                            if possible_pin == (): #brak blokującej figury, zatem pozycja szachowa
                                is_in_check = True
                                checks.append((end_row, end_column, d[0], d[1]))
                                break
                            else: #blokująca figura, zatem związanie
                                pins.append(possible_pin)
                                break
                        else: #figura przeciwnika nie daje pozycji szachowej
                            break 
                else: #poza szachownicą
                    break
        #Obsługa przypadku gdy figurą dająca szacha jest skoczek
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_column = start_column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                stop_square = self.board[end_row][end_column]
                if stop_square[0] == enemy_color and stop_square[1] == "N": #skoczek przeciwnika atakuje króla gracza 
                    is_in_check = True
                    checks.append((end_row, end_column, m[0], m[1]))
        return is_in_check, pins, checks




    """
    Funkcja sprawdzająca czy gracz, który obecnie ma turę jest szachowany
    """
    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])


    """
    Funkcja określająca, czy przeciwnik może atakować pole zadane przez (row,column)
    """
    def square_under_attack(self, row, column):
        self.whiteToMove = not self.whiteToMove #przełączenie tury, aby ocenić pozycję z perspektywy gracza atakującego
        opponent_moves = self.get_all_possible_moves() #wygenerowanie wszystkich możliwych ruchów przeciwnika
        self.whiteToMove = not self.whiteToMove  #powrót do właściwej tury (gracza, który miał turę przed sprawdzeniem czy jego pozycja jest atakowana)
        for move in opponent_moves:
            if move.end_row == row and move.end_column == column:  #pole jest atakowane
                return True
        return False #pole nie jest atakowane





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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1): 
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = 'b'
        else: 
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = 'w'
        pawn_promotion = False

        if self.board[row+move_amount][column] == "--": #ruch o 1 pole
            if not piece_pinned or pin_direction == (move_amount, 0):
                if row + move_amount == back_row: #jeśli pion dojdzie do ostatniej linii, następuje promocja piona
                    pawn_promotion = True
                moves.append(Move((row, column), (row + move_amount, column), self.board, pawn_promotion = pawn_promotion))
                if row == start_row and self.board[row + 2*move_amount][column] == "--": #ruch o 2 pola
                    moves.append(Move((row, column), (row + 2*move_amount, column), self.board))
        if column-1 >= 0: #bicie w lewo
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][column - 1][0] == enemy_color:
                    if row + move_amount == back_row: #jeśli pion dojdzie do ostatniej linii następuje promocja piona
                        pawn_promotion = True
                    moves.append(Move((row, column), (row + move_amount, column - 1), self.board, pawn_promotion = pawn_promotion))
                if (row + move_amount, column - 1) == self.en_passant_possible:
                    moves.append(Move((row, column), (row + move_amount, column - 1), self.board, en_passant= True))
        if column + 1 <= 7: #bicie w prawo
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[row + move_amount][column + 1][0] == enemy_color:
                    if row + move_amount == back_row: #jeśli pion dojdzie do ostatniej linii następuje promocja piona
                        pawn_promotion = True
                    moves.append(Move((row, column), (row + move_amount, column + 1), self.board, pawn_promotion = pawn_promotion))
                if (row + move_amount, column + 1) == self.en_passant_possible:
                    moves.append(Move((row, column), (row + move_amount, column + 1), self.board, en_passant= True))

        

    '''
    Pobiera wszystkie ruchy wież stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_rook_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][column][1] != "Q": #nie mozna usunac dam z wiazania na wiezy, jedynie gonce
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #góra, lewo, dół, prawo
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions: #sprawdzanie dostępnych pól we wszystkich kierunkach
            for i in range(1, 8): #maksymalna liczba pól o jakie może sie poruszyć to 7
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8: #zapewnienie, że znajdujemy się na planszy
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]): #ostatni warunek pozwala poruszać się wzdłuż wiązania w przeciwnym kierunku
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
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #pola na które może skoczyć skoczek, w kształcie litery L
        own_color = "w" if self.whiteToMove else "b" #figura tego samego koloru
        for m in knight_moves:
            end_row = row + m[0]
            end_column = column + m[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8: #warunek pozostawania na szachownicy
                if not piece_pinned:
                    stop_square = self.board[end_row][end_column]
                    if stop_square[0] != own_color: #puste pole lub figura przeciwnika
                        moves.append(Move((row, column), (end_row, end_column), self.board))

    '''
    Pobiera wszystkie ruchy gońców stojących na row, column i dodaje te ruchy do listy moves
    '''
    def get_bishop_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #określenie kierunków po przekątnych
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions: #sprawdzanie dostępnych pól we wszystkich określonych kierunkach
            for i in range(1, 8): #maksymalna liczba pól o jakie może sie poruszyć to 7
                end_row = row + d[0] * i
                end_column = column + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:  #zapewnienie, że znajdujemy się na planszy
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
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
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        column_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        own_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_column = column + column_moves[i]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                stop_square = self.board[end_row][end_column]
                if stop_square[0] != own_color:
                    #postawienie króla na stop_square i sprawdzenie czy występuje na nim szach 
                    if own_color == "w":
                       self.white_king_location = (end_row, end_column)
                    else: 
                        self.black_king_location = (end_row, end_column)
                    is_in_check, pins, checks = self.check_for_pins_and_checks()
                    if not is_in_check:
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    #postawienie króla z powrotem na jego oryginalnej pozycji
                    if own_color == "w":
                        self.white_king_location = (row, column)
                    else:
                        self.black_king_location = (row, column)

        

    '''
    Generuje wszystkie dozwolone ruchy związane z roszadą dla króla w (row, column) i dodaje je do listy ruchów
    '''
    def get_castle_moves(self, row, column, moves):
        if self.square_under_attack(row, column):
            return #nie można przeprowadzić roszady, gdy król znajduje się w szachu
        if (self.whiteToMove and self.current_castling_rights.wks) or (not self.whiteToMove and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, column, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (not self.whiteToMove and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, column, moves)
    
    def get_kingside_castle_moves(self, row, column, moves):
        if self.board[row][column+1] == "--" and self.board[row][column+2] == "--": #sprawdzenie, oba pola pomiędzy królem i wieżą na skrzydle królewskim sa puste
            if not self.square_under_attack(row, column+1) and not self.square_under_attack(row, column+2):
                moves.append(Move((row, column), (row, column+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, column, moves):
        if self.board[row][column-1] == "--" and self.board[row][column-2] == "--" and self.board[row][column-3] == "--": #na skrzydle hemtańskim
            if not self.square_under_attack(row, column-1) and not self.square_under_attack(row, column-2): #brak sprawdzenia column-3, ponieważ król i tak nie trafia na to pole
                moves.append(Move((row, column), (row, column-2), self.board, is_castle_move=True))


"""Klasa reprezentująca zasady związane z roszadą"""
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    
    # mapowanie kluczy na wartości
    # klucz : wartość
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b" : 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}



    def __init__(self, startSq, endSq, board, en_passant = False, pawn_promotion = False, is_castle_move = False):
        self.start_row = startSq[0]
        self.start_column = startSq[1]
        self.end_row = endSq[0]
        self.end_column = endSq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        self.en_passant = en_passant
        self.pawn_promotion = pawn_promotion
        self.is_castle_move = is_castle_move
        if en_passant:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp' #bicie w przelocie bije pionka o przeciwnym kolorze
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