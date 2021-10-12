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
        IMAGES[piece] = p.transform.scale(p.image.load("resources/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
Główny sterownik kodu. Obsługuje komendy wejściowe użytkownika i interfejs graficzny
"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState() #inicjalizacja obiektu Stanu Gry
    print(gs.board)


main()




