# holdem_app/app/services/game_orchestrator.py
from app.models.game_state import GameState
from app.models.game_config import GameConfig
from app.models.player import Player
from . import hand_manager
from . import ai_agent_service

class GameOrchestrator:
    """
    ゲーム全体の流れを統括するクラス。
    ゲームの開始、ハンドの進行、プレイヤーの管理などを行う。
    """
    def __init__(self, config: GameConfig):
        self.game_state = GameState(config)

    def add_player(self, player: Player, seat_index: int):
        """プレイヤーをテーブルに着席させる"""
        initial_stack = self.game_state.config.initial_stack
        self.game_state.table.sit_player(player, seat_index, initial_stack)
        print(f"{player.name} sits at seat {seat_index}.")

    def start_game(self):
        """ゲームを開始する"""
        # ここにゲームループを実装する
        # 例: プレイヤーが2人以上いるかチェックし、ハンドを開始する
        print("Game started.")
        while len(self.game_state.table.active_players()) > 1:
            self.play_hand()
        
        print("Game finished.")

    def play_hand(self):
        """1ハンドをプレイする"""
        hand_manager.start_hand(self.game_state)
        
        # ハンドが終了するまでラウンドを進行
        while not hand_manager.is_hand_over(self.game_state):
            # プレイヤーのアクションを取得・処理するロジック
            # current_player = ...
            # if current_player.is_ai:
            #     action = ai_agent_service.decide_action(self.game_state, current_player)
            # else:
            #     # 人間プレイヤーからの入力を待つ
            #     action = ...
            # action_service.process_action(self.game_state, action)
            pass

        hand_manager.end_hand(self.game_state)
