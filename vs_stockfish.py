import chess
import chess.engine
from search import SearchStats
import csv
import matplotlib.pyplot as plt
import engine as myengine

# STOCKFISH_PATH = r"C:\Users\Potato 3.0\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe"
STOCKFISH_PATH = r'C:\Users\Potato 3.0\Desktop\lczero\lc0.exe'
GAMES_TO_PLAY = 10
GAMES_PER_DEPTH = 10
DEPTH_LEVELS = [2, 3, 4, 5]

def evaluate_metrics(board):
    material = 0
    pst_bonus = 0
    mobility = len(list(board.legal_moves))
    king_safety = 0
    pawn_structure_penalty = 0

    piece_values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
                    chess.ROOK: 500, chess.QUEEN: 900}

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color_factor = 1 if piece.color == board.turn else -1
            material += color_factor * piece_values.get(piece.piece_type, 0)

            if piece.piece_type == chess.KING:
                king_file = chess.square_file(square)
                king_rank = chess.square_rank(square)
                if (board.turn == chess.WHITE and king_rank == 0) or (board.turn == chess.BLACK and king_rank == 7):
                    king_safety += color_factor * 50

            if piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                
                for rank in range(8):
                    if rank != chess.square_rank(square):
                        if board.piece_at(chess.square(file, rank)) == piece:
                            pawn_structure_penalty -= 25 * color_factor

    return {
        "material": material,
        "mobility": mobility,
        "king_safety": king_safety,
        "pawn_structure": pawn_structure_penalty,
        "pst": pst_bonus  # not implemented fully
    }

def save_to_csv(results, filename="game_results.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Game", "Engine Side", "Result", "Outcome", "Nodes", "Cutoffs", "Depth"])
        for i, r in enumerate(results):
            writer.writerow([
                i+1,
                r["engine_side"],
                r["result"],
                r["outcome"],
                r["nodes"],
                r["cutoffs"],
                r["depth"]
            ])
    print(f"\nSaved results to {filename}")

def plot_results(results):
    games = list(range(1, len(results)+1))
    nodes = [r["nodes"] for r in results]
    cutoffs = [r["cutoffs"] for r in results]
    depths = [r["depth"] for r in results]

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.plot(games, nodes, marker='o')
    plt.title("Nodes Searched per Game")
    plt.xlabel("Game")
    plt.ylabel("Nodes")

    plt.subplot(1, 3, 2)
    plt.plot(games, cutoffs, marker='o', color='orange')
    plt.title("Cutoffs per Game")
    plt.xlabel("Game")
    plt.ylabel("Cutoffs")

    plt.subplot(1, 3, 3)
    plt.plot(games, depths, marker='o', color='green')
    plt.title("Max Depth per Game")
    plt.xlabel("Game")
    plt.ylabel("Depth")

    plt.tight_layout()
    plt.show()


def plot_evaluation_metrics(results):
    import numpy as np

    avg_metrics = {"material": [], "mobility": [], "king_safety": [], "pawn_structure": []}

    for r in results:
        turns = len(r["metrics"])
        mat = [m["material"] for m in r["metrics"]]
        mob = [m["mobility"] for m in r["metrics"]]
        king = [m["king_safety"] for m in r["metrics"]]
        pawn = [m["pawn_structure"] for m in r["metrics"]]

        avg_metrics["material"].append(np.mean(mat))
        avg_metrics["mobility"].append(np.mean(mob))
        avg_metrics["king_safety"].append(np.mean(king))
        avg_metrics["pawn_structure"].append(np.mean(pawn))

    games = list(range(1, len(results)+1))
    plt.figure(figsize=(12, 8))
    for i, key in enumerate(avg_metrics.keys()):
        plt.subplot(2, 2, i+1)
        plt.plot(games, avg_metrics[key], marker='o')
        plt.title(f"Average {key.replace('_', ' ').title()} per Game")
        plt.xlabel("Game")
        plt.ylabel(key.replace('_', ' ').title())
    plt.tight_layout()
    plt.show()

def run_matches():
    totals = {
        "1-0": 0, "0-1": 0, "1/2-1/2": 0,
        "total_nodes": 0,
        "total_cutoffs": 0,
        "total_depth": 0,
        "games": 0,
        "wins": 0,
        "losses": 0,
        "draws": 0
    }
    results_list = []

    for i in range(GAMES_TO_PLAY):
        play_as_white = (i % 2 == 0)
        result, stats, side, outcome, depth, all_depths, metrics = play_single_game(play_as_white)

        print(f"Game {i+1}: Engine played {side} | Result: {result} ({outcome})")

        totals[result] += 1
        totals["total_nodes"] += stats.nodes
        totals["total_cutoffs"] += stats.cutoffs
        totals["total_depth"] += depth
        totals["games"] += 1

        if outcome == "Win":
            totals["wins"] += 1
        elif outcome == "Loss":
            totals["losses"] += 1
        else:
            totals["draws"] += 1

        results_list.append({
            "result": result,
            "engine_side": side,
            "outcome": outcome,
            "nodes": stats.nodes,
            "cutoffs": stats.cutoffs,
            "depth": depth,
            "depth_series": all_depths,
            "metrics": metrics
        })

    print("\n=== Summary ===")
    print(f"Wins: {totals['wins']}, Losses: {totals['losses']}, Draws: {totals['draws']}")
    print(f"Avg Nodes: {totals['total_nodes'] // GAMES_TO_PLAY}")
    print(f"Avg Cutoffs: {totals['total_cutoffs'] // GAMES_TO_PLAY}")
    print(f"Avg Depth: {totals['total_depth'] // GAMES_TO_PLAY}")

    save_to_csv(results_list)
    plot_results(results_list)
    plot_evaluation_metrics(results_list)

def play_single_game(play_as_white=True, depth_override=3):
    board = chess.Board()
    engine_sf = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    stats = SearchStats()
    max_depth = 0
    all_depths = []
    metrics_log = []

    while not board.is_game_over() and board.fullmove_number <= 80:
        depth = depth_override

        if board.turn == chess.WHITE and play_as_white:
            move = myengine.choose_best_move(board, depth=depth, stats=stats)
        elif board.turn == chess.BLACK and not play_as_white:
            move = myengine.choose_best_move(board, depth=depth, stats=stats)
        else:
            move = engine_sf.play(board, chess.engine.Limit(time=0.1)).move

        board.push(move)
        max_depth = max(max_depth, stats.depth_reached)
        all_depths.append(stats.depth_reached)
        metrics_log.append(evaluate_metrics(board))

    result = board.result()
    engine_sf.quit()

    winner = "White" if result == "1-0" else "Black" if result == "0-1" else "Draw"
    engine_side = "White" if play_as_white else "Black"
    outcome = "Win" if winner == engine_side else "Loss" if winner != "Draw" else "Draw"

    return result, stats, engine_side, outcome, max_depth, all_depths, metrics_log

def run_depth_trials():
    summary = {}

    for test_depth in DEPTH_LEVELS:
        print(f"\n=== Running depth {test_depth} trials ===")
        totals = {
            "1-0": 0, "0-1": 0, "1/2-1/2": 0,
            "total_nodes": 0, "total_cutoffs": 0, "total_depth": 0,
            "wins": 0, "losses": 0, "draws": 0
        }
        results_list = []

        for i in range(GAMES_PER_DEPTH):
            play_as_white = (i % 2 == 0)
            result, stats, side, outcome, depth, all_depths, metrics = play_single_game(play_as_white, test_depth)

            print(f"Game {i+1}: Engine played {side} | Result: {result} ({outcome})")

            totals[result] += 1
            totals["total_nodes"] += stats.nodes
            totals["total_cutoffs"] += stats.cutoffs
            totals["total_depth"] += depth

            if outcome == "Win":
                totals["wins"] += 1
            elif outcome == "Loss":
                totals["losses"] += 1
            else:
                totals["draws"] += 1

            results_list.append({
                "result": result,
                "engine_side": side,
                "outcome": outcome,
                "nodes": stats.nodes,
                "cutoffs": stats.cutoffs,
                "depth": depth,
                "depth_series": all_depths,
                "metrics": metrics
            })

        print(f"\n[Depth {test_depth} Summary]")
        print(f"Wins: {totals['wins']} | Losses: {totals['losses']} | Draws: {totals['draws']}")
        print(f"Avg Nodes: {totals['total_nodes'] // GAMES_PER_DEPTH}")
        print(f"Avg Cutoffs: {totals['total_cutoffs'] // GAMES_PER_DEPTH}")
        print(f"Avg Depth: {totals['total_depth'] // GAMES_PER_DEPTH}")

        summary[test_depth] = totals
        save_to_csv(results_list, f"results_depth_{test_depth}.csv")
        plot_results(results_list)
        plot_evaluation_metrics(results_list)

    print("\n=== Overall Comparison by Depth ===")
    for depth in DEPTH_LEVELS:
        s = summary[depth]
        print(f"Depth {depth}: Wins={s['wins']}, Losses={s['losses']}, Draws={s['draws']}, AvgNodes={s['total_nodes']//GAMES_PER_DEPTH}, AvgCutoffs={s['total_cutoffs']//GAMES_PER_DEPTH}, AvgDepth={s['total_depth']//GAMES_PER_DEPTH}")


if __name__ == "__main__":
    run_depth_trials()
