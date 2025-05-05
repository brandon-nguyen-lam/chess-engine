# search.py
class SearchStats:
    def __init__(self):
        self.nodes = 0
        self.cutoffs = 0
        self.depth_reached = 0

def alpha_beta(board, depth, alpha, beta, maximizing, evaluate, generate_moves, make_move, undo_move, stats: SearchStats, current_depth=0):
    stats.depth_reached = max(stats.depth_reached, current_depth)

    if depth == 0 or board.is_game_over():
        return evaluate(board)

    stats.nodes += 1
    legal_moves = generate_moves(board)
    ordered_moves = sorted(legal_moves, key=lambda m: board.is_capture(m), reverse=True)

    if maximizing:
        max_eval = float('-inf')
        for move in ordered_moves:
            make_move(board, move)
            eval = alpha_beta(board, depth - 1, alpha, beta, False, evaluate, generate_moves, make_move, undo_move, stats, current_depth + 1)
            undo_move(board, move)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                stats.cutoffs += 1
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in ordered_moves:
            make_move(board, move)
            eval = alpha_beta(board, depth - 1, alpha, beta, True, evaluate, generate_moves, make_move, undo_move, stats, current_depth + 1)
            undo_move(board, move)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                stats.cutoffs += 1
                break
        return min_eval
