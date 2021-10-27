"""Glowny plik sterownika. Odpowiedzialny za obsługę akcji użytkownika i wyświetlanie aktualnego stanu gry."""

import pygame as p
import Engine


WIDTH = HEIGHT = 512
DIMENSION = 8 #Wymiary szachownicy to 8x8 pól
SQ_SIZE = WIDTH // DIMENSION #Rozmiar pojedynczego pola: 512/8=64
MAX_FPS = 30 #Parametr animacji, maksymalna liczba klatek na sekundę
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
                    print(move.get_chess_notation())
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                    sq_selected = () #zresetowanie kliknięc gracza
                    player_clicks = []
            #obsługa klawiszy klawiaturowych
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #cofnij ruch po kliknięci 'z' na klawiaturze
                    gs.undo_move() 
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Odpowiedzialna za grafikę powiązaną z danym stanem gry 
"""
def draw_game_state(screen, gs):
    drawBoard(screen) #rysuje pola na szachownicy
    #TODO: Podkreślanie figur, sugestie ruchów
    drawPieces(screen, gs.board) #rysuje figury szachowe na polach szachownicy 


"""
rysuje pola na szachownicy. Pole w lewym górnym rogu jest jasnego koloru
"""
def drawBoard(screen):
    colors = ["#eae2b7", "#277da1"]
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




if __name__ == "__main__":
    main()




