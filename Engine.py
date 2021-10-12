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