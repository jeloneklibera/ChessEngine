"""Glowny plik sterownika. Odpowiedzialny za obsługę akcji użytkownika i wyświetlanie aktualnego stanu gry."""

import pygame as p
import Engine


WIDTH = HEIGHT = 512
DIMENSION = 8 #Wymiary szachownicy to 8x8 pól
SQ_SIZE = WIDTH // DIMENSION #Rozmiar pojedynczego pola: 512/8=64
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
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState() #inicjalizacja obiektu Stanu Gry
    valid_moves = gs.get_valid_moves()
    move_made = False #flaga sprawdzająca czy ruch został wykonany
    animate = False #flaga mówiąca kiedy ruch powinien być animowany
    load_images()
    running = True
    sq_selected = () #początkowo żadne pole nie jest zaznaczone, śledzi ostatnie kliknięcie użytkownika (krotka: (row, col))
    player_clicks = [] #śledzi kliknięcia użytkownika (dwie krotki: [(6, 4), (4, 4)] - odpowiada ruchowi pionka o dwa pola)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #obsługa kliknięć myszy
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) pozycja kursora
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col): #użytkownik kliknął na to samo pole dwukrotnie, odznaczenie zaznaczenia
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

        if move_made:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, sq_selected)
        clock.tick(MAX_FPS)
        p.display.flip()

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
Odpowiedzialna za grafikę powiązaną z danym stanem gry 
"""
def draw_game_state(screen, gs, valid_moves, sq_selected):
    drawBoard(screen) #rysuje pola na szachownicy
    highlight_squares(screen, gs, valid_moves, sq_selected)
    drawPieces(screen, gs.board) #rysuje figury szachowe na polach szachownicy 


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
Rysuje figury na szachownicy w oparciu o aktualny stan gry: GamesState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #Sprawdzenie czy pole nie jest puste
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Funkcja odpowiedzialna za animację ruchu
"""
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_column - move.start_column
    frames_per_square = 5 #liczba klatek odpowiadająca ruchowi o jedno pole
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
            screen.blit(IMAGES[move.piece_captured], end_square)
        #narysowanie poruszającej się figury
        screen.blit(IMAGES[move.piece_moved], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()




