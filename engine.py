# engine.py

import chess
from evaluate import evaluate
from movegen import generate_moves, make_move, undo_move
from search import alpha_beta, SearchStats

def choose_best_move(board, depth=3, stats=None):
    from search import SearchStats
    if stats is None:
        stats = SearchStats()

    best_move = None
    best_score = float('-inf')

    for move in generate_moves(board):
        make_move(board, move)
        score = alpha_beta(board, depth - 1, float('-inf'), float('inf'), False,
                   evaluate, generate_moves, make_move, undo_move, stats, current_depth=1)

        undo_move(board, move)

        if score > best_score:
            best_score = score
            best_move = move

    return best_move
