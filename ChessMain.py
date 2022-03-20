"""Glowny plik sterownika. Odpowiedzialny za obsługę akcji użytkownika i wyświetlanie aktualnego stanu gry."""

import pygame as p
import Engine
import ChessAI


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 #Wymiary szachownicy to 8x8 pól
SQ_SIZE = BOARD_WIDTH // DIMENSION #Rozmiar pojedynczego pola: 512/8=64
MAX_FPS = 60 #Parametr animacji, maksymalna liczba klatek na sekundę
IMAGES = {}

"""
Inicjalizuje globalny słownik obrazów. Zostanie wywołane tylko jeden raz w funkcji main() ze względu na oszczędność zasobów 
(zasobochłonne wielkokrotne ładowanie obrazków)
"""

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("resources/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
Główny sterownik kodu. Obsługuje komendy wejściowe użytkownika i interfejs graficzny
"""

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 16, False, False)
    gs = Engine.GameState() #inicjalizacja obiektu Stanu Gry
    valid_moves = gs.get_valid_moves()
    move_made = False #flaga sprawdzająca czy ruch został wykonany
    animate = False #flaga mówiąca kiedy ruch powinien być animowany
    load_images()
    running = True
    sq_selected = () #początkowo żadne pole nie jest zaznaczone, śledzi ostatnie kliknięcie użytkownika (krotka: (row, col))
    player_clicks = [] #śledzi kliknięcia użytkownika (dwie krotki: [(6, 4), (4, 4)] - odpowiada ruchowi pionka o dwa pola)
    game_over = False
    player_one = True #Kiedy człowiek gra białymi - True, gdy AI gra białymi - False
    player_two = True #Kiedy człowiek gra czarnymi - True, gdy AI gra czarnymi - False
    while running:
        is_human_turn = (gs.whiteToMove and player_one) or (not gs.whiteToMove and player_two) #(tura białych i człowiek gra białymi) lub (tura czarnych i człowiek gra czarnymi)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #obsługa kliknięć myszy
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    location = p.mouse.get_pos() #(x,y) pozycja kursora
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8: #użytkownik kliknął na to samo pole dwukrotnie lub na obszarze z logiem ruchów, odznaczenie zaznaczenia
                        sq_selected = () #odznaczenie
                        player_clicks = [] 
                    else: 
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) #dodanie pierwszego lub drugiego kliknięcia
                    if (len(player_clicks)) == 2: #sytuacja po drugim kliknięciu
                        move = Engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i]) #valid_moves[i] to legalny ruch wygenerowany przez silnik, w przeciwieństwie do move, 
                                                            #które jest wygenerowane przez kliknięcie myszy przez użytkownika. Ma to znaczenie w przypadku ruchów posiadających flagę tj. bicie w przelocie, promocja piona
                                move_made = True
                                animate = True
                                sq_selected = () #zresetowanie kliknięc gracza
                                player_clicks = []
                                print(move.get_chess_notation())
                        if not move_made:
                            player_clicks = [sq_selected]
            #obsługa klawiszy klawiaturowych
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #cofnij ruch po kliknięci 'z' na klawiaturze
                    gs.undo_move() 
                    move_made = True
                    animate = False #przy cofaniu wykonanego ruchu animacja jest niepotrzebna
                    game_over = False
                if e.key == p.K_r: #reset całej gry
                    gs = Engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False


        #Ruchy AI
        if not game_over and not is_human_turn:
            AI_move = ChessAI.find_best_move_negamax_alphabeta_recursion_first_call(gs, valid_moves)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
            gs.make_move(AI_move)
            print(AI_move.get_chess_notation())
            move_made = True
            animate = True


        if move_made:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font)

        if gs.check_mate or gs.stale_mate:
            game_over = True
            text =  "Koniec gry - pat" if gs.stale_mate else ("BLACK WON!!!" if gs.whiteToMove else "WHITE WON!!!")
            draw_end_game_text(screen, text) #wypisanie na ekranie koncowego rezultatu gry
        clock.tick(MAX_FPS)
        p.display.flip()



"""
Odpowiedzialna za grafikę powiązaną z danym stanem gry 
"""
def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font):
    drawBoard(screen) #rysuje pola na szachownicy
    highlight_squares(screen, gs, valid_moves, sq_selected)
    drawPieces(screen, gs.board) #rysuje figury szachowe na polach szachownicy 
    drawMoveLog(screen, gs, move_log_font)

"""
rysuje pola na szachownicy. Pole w lewym górnym rogu jest jasnego koloru
"""
def drawBoard(screen):
    global colors
    colors = ["white", "gray"]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)] 
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Funkcja odpowiedzialna za podświetlenie wybranej bierki i pól na które dana bierka może przejść w danym ruchu
"""
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #zaznaczone pole należy do gracza wykonującego ruch w danej turze
            #podświetlenie zaznaczonego pola
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #poziom przezroczystości - wartość 0 oznacza pełną przezroczystość, 255 oznacza brak pezroczystości
            s.fill(p.Color('yellow'))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            #podświetlenie pól na które dana bierka może przejść w danym ruchu
            s.fill(p.Color('green'))
            for move in valid_moves:
                if move.start_row == row and move.start_column == col:
                    screen.blit(s, (move.end_column * SQ_SIZE, move.end_row * SQ_SIZE))
            s.fill(p.Color('red'))
            s.set_alpha(150)
            for move in valid_moves:
                if move.start_row == row and move.start_column == col:
                    if gs.board[move.end_row][move.end_column][0] == ('b' if gs.whiteToMove else 'w'):
                        screen.blit(s, (move.end_column * SQ_SIZE, move.end_row *SQ_SIZE))

"""
Rysuje figury na szachownicy w oparciu o aktualny stan gry: GamesState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #Sprawdzenie czy pole nie jest puste
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Wypisuje log z wykonanymi ruchami po prawej stronie szachownicy
"""
def drawMoveLog(screen, gs, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("#E7DFC6"), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i//2 + 1) + ". " + str(move_log[i]) + " " #pierwsza tura wyświetlana jako 1. a nie 0. oraz dwa ruchy stanowią jedną pełną turę
        if i+1 < len(move_log): #warunek zapewniający, że drugi gracz wykonał swój ruch
            move_string += str(move_log[i+1]) + " "
        move_texts.append(move_string) 
    
    moves_per_row = 3
    padding_text = 5
    line_spacing = 2
    text_y = padding_text
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]
        text_object = font.render(text, True, p.Color("#131B23"))
        text_location = move_log_rect.move(padding_text, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing



"""
Funkcja odpowiedzialna za animację ruchu
"""
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_column - move.start_column
    frames_per_square = 3 #liczba klatek odpowiadająca ruchowi o jedno pole
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        row, column = (move.start_row + dR*frame/frame_count, move.start_column + dC*frame/frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        #wykasowanie poruszanej bierki z jej końcowego pola
        color = colors[(move.end_row + move.end_column)%2]
        end_square = p.Rect(move.end_column*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #ponowne narysowanie zbitej figury w przypadku, gdy ruch był biciem
        if move.piece_captured != "--":
            if move.en_passant:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_column*SQ_SIZE, en_passant_row*SQ_SIZE, SQ_SIZE, SQ_SIZE) 
            screen.blit(IMAGES[move.piece_captured], end_square)
        #narysowanie poruszającej się figury
        screen.blit(IMAGES[move.piece_moved], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color("green"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_object.get_BOARD_WIDTH()/2, BOARD_HEIGHT/2 - text_object.get_BOARD_HEIGHT()/2) #wyśrodkowanie napisu na ekranie
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("blue"))
    screen.blit(text_object, text_location.move(2, 2))

if __name__ == "__main__":
    main()




