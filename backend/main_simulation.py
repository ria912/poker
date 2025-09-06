# holdem_app/main_simulation.py
import sys
import os

# プロジェクトのルートパスをPythonのパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.game_state import GameState
from app.models.table import Table
from app.models.player import Player
from app.services.simulation.player_stats import PlayerStats
from app.services.simulation.simulation_runner import SimulationRunner

def setup_game():
    """シミュレーション用のゲーム状態をセットアップする"""
    table = Table(max_seats=6)
    game_state = GameState(table=table)
    
    # --- AIプレイヤーの定義 ---
    # ここで異なるAIをロードするように拡張できる
    players = [
        Player(player_id="ai_1", name="SimpleBot", is_ai=True),
        Player(player_id="ai_2", name="SimpleBot", is_ai=True),
        Player(player_id="ai_3", name="SimpleBot", is_ai=True),
        Player(player_id="ai_4", name="SimpleBot", is_ai=True),
        Player(player_id="ai_5", name="SimpleBot", is_ai=True),
        Player(player_id="ai_6", name="SimpleBot", is_ai=True),
    ]

    player_stats = {p.player_id: PlayerStats(p.player_id, p.name) for p in players}

    # 各プレイヤーを着席させ、スタックを持たせる
    initial_stack = 10000 # 100BB
    for i, player in enumerate(players):
        table.seat_player(player, seat_index=i, stack=initial_stack)
        
    return game_state, player_stats

def main():
    """シミュレーションを実行し、結果を表示する"""
    NUM_HANDS_TO_SIMULATE = 10000

    print("Setting up game for simulation...")
    game_state, player_stats = setup_game()

    print(f"Running simulation for {NUM_HANDS_TO_SIMULATE} hands...")
    runner = SimulationRunner(game_state, player_stats)
    runner.run_simulation(NUM_HANDS_TO_SIMULATE)

    print("\n--- Simulation Complete ---")
    print("\n--- Final Results ---")
    
    for stats in player_stats.values():
        print(stats.get_summary(game_state.big_blind))
        print("")


if __name__ == "__main__":
    main()
