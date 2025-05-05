import chess
from engine import choose_best_move

def play_game():
    board = chess.Board()
    move_num = 1

    while not board.is_game_over():
        print(f"\nMove {move_num}: {'White' if board.turn else 'Black'} to move")
        print(board)

        move = choose_best_move(board, depth=3)
        if move is None:
            print("No legal move found. Ending game.")
            break

        print(f"Engine plays: {board.san(move)}")
        board.push(move)
        move_num += 1

    print("\nFinal position:")
    print(board)
    print("Game result:", board.result())

if __name__ == "__main__":
    play_game()
