# holdem_app/app/services/game_orchestrator.py
from app.models.game_state import GameState
from app.models.player import Player
from app.models.enum import Round, GameStatus
from app.services import hand_manager, round_manager, ai_agent_service, position_service

class GameOrchestrator:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def run_game(self, num_hands: int = 5):
        """
        指定されたハンド数だけゲームを自動で実行する
        """
        print("--- Game Start ---")
        hand_count = 0
        while hand_count < num_hands:
            active_players = position_service.get_occupied_seats(self.game_state)
            if len(active_players) < 2:
                print("Not enough players to continue. Game over.")
                break
            
            print(f"\n--- Starting Hand #{hand_count + 1} ---")
            self.play_hand()
            hand_count += 1
        
        print("\n--- Game Over ---")

    def play_hand(self):
        """1ハンドを実行する"""
        hand_manager.start_new_hand(self.game_state)
        
        if self.game_state.status != GameStatus.IN_PROGRESS:
            print("Could not start hand.")
            return

        # 各ベッティングラウンドをループ
        for round_enum in [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER]:
            self.game_state.current_round = round_enum
            
            # プリフロップ以降はコミュニティカードをめくる
            if round_enum != Round.PREFLOP:
                hand_manager.proceed_to_next_round(self.game_state)
                print(f"Community Cards: {[str(c) for c in self.game_state.table.community_cards]}")


            # 誰か一人が残った時点でハンド終了
            if hand_manager._is_hand_over(self.game_state):
                break
            
            # ベッティングラウンドを実行
            round_manager.run_betting_round(self.game_state, self._get_action_for_player)
            
            if hand_manager._is_hand_over(self.game_state):
                break
        
        # ハンドの決着
        print("--- Concluding Hand ---")
        hand_manager._conclude_hand(self.game_state)
        
        # プレイヤーのスタック情報を表示
        for seat in self.game_state.table.seats:
            if seat.is_occupied:
                print(f"Seat {seat.index} ({seat.player.name}): Stack {seat.stack}")


    def _get_action_for_player(self, game_state: GameState):
        """
        現在のプレイヤーのアクションを取得する。
        AIか人間かで処理を分岐させる（今回は全員AIを想定）
        """
        current_seat = game_state.table.seats[game_state.current_seat_index]
        if current_seat.player.is_ai:
            return ai_agent_service.decide_action(game_state)
        else:
            # TODO: 人間プレイヤーからの入力を受け付ける処理
            # 現状はAIと同じロジックを仮で呼び出す
            return ai_agent_service.decide_action(game_state)
