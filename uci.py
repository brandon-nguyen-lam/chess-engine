# uci.py

import sys
import chess
from engine import choose_best_move

board = chess.Board()

def uci_loop():
    while True:
        line = input()

        if line == "uci":
            print("id name AlphaBetaEngine")
            print("id author You")
            print("uciok")

        elif line == "isready":
            print("readyok")

        elif line.startswith("position"):
            parts = line.split(" ", 2)
            if "startpos" in line:
                board.reset()
                if "moves" in line:
                    move_section = parts[2].split("moves")[1].strip()
                    for move_str in move_section.split():
                        move = board.parse_uci(move_str)
                        board.push(move)
            elif "fen" in line:
                fen = line.split("fen")[1].strip()
                board.set_fen(fen)

        elif line.startswith("go"):
            move = choose_best_move(board, depth=3)
            print(f"bestmove {move.uci()}")

        elif line == "quit":
            break
