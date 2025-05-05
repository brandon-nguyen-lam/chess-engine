piece_values = {
    "P": 100,  # Pawn
    "N": 320,  # Knight
    "B": 330,  # Bishop
    "R": 500,  # Rook
    "Q": 900,  # Queen
    "K": 0     # King (not scored)
}

def evaluate(board):
    """
    Simple handcrafted evaluation:
    + Material score
    + Mobility bonus
    + Penalty for doubled/isolated pawns (placeholder)
    """
    score = 0

    for square in board.piece_map():
        piece = board.piece_at(square)
        symbol = piece.symbol()
        value = piece_values[symbol.upper()]
        if piece.color == board.turn:
            score += value
        else:
            score -= value

    # Mobility (number of legal moves for current player)
    mobility = len(list(board.legal_moves))
    score += mobility * 5

    return score
