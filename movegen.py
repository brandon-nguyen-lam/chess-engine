def generate_moves(board):
    """Returns a list of all legal moves with placeholder scores."""
    return list(board.legal_moves)

def make_move(board, move):
    board.push(move)

def undo_move(board, move):
    board.pop()
