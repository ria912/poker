from app.models.game_state import GameState
from app.models.game_config import GameConfig
from app.models.player import Player
from app.services.game_orchestrator import GameOrchestrator

def main():
    """
    ゲームを実行するメイン関数
    """
    # 1. ゲーム設定の初期化
    config = GameConfig(seat_count=6, big_blind=100, small_blind=50, initial_stack=10000)
    game_state = GameState(config)

    # 2. プレイヤーの作成と着席
    # 人間プレイヤー（あなた）
    human_player = Player("Human", is_ai=False)
    game_state.table.sit_player(human_player, 0, config.initial_stack)

    # AIプレイヤー
    for i in range(1, 4): # AIを3人追加
        ai_player = Player(f"AI_{i}", is_ai=True)
        game_state.table.sit_player(ai_player, i, config.initial_stack)

    # 3. ゲームオーケストレーターの準備とゲーム開始
    orchestrator = GameOrchestrator(game_state)
    
    print("--- Texas Hold'em Game Start! ---")
    # 100ハンド実行するか、プレイヤーが2人未満になったら終了
    orchestrator.run_game(num_hands=100)
    print("--- Game Over ---")


if __name__ == "__main__":
    main()
