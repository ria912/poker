# holdem_app/app/services/game_orchestrator.py
from ..models.game_state import GameState
from ..models.player import Player
from ..models.enum import GameStatus, Round, ActionType
from . import (
    position_service, 
    hand_manager, 
    round_manager, 
    action_service,
    ai_agent_service,
)

class GameOrchestrator:
    """ゲーム全体の進行を管理するクラス"""

    def __init__(self):
        self.gs = GameState()
        self.ai_service = ai_agent_service.AIAgentService()

    def add_player(self, player: Player, seat_index: int, stack: int):
        """プレイヤーをテーブルに着席させる"""
        self.gs.table.seats[seat_index].sit_down(player, stack)

    def start_new_hand(self):
        """新しいハンドを開始する"""
        self.gs.clear_for_new_hand()
        
        active_players = [s for s in self.gs.table.seats if s.is_occupied and s.stack > 0]
        if len(active_players) < 2:
            self.gs.status = GameStatus.WAITING
            return

        self.gs.status = GameStatus.IN_PROGRESS
        self.gs.current_round = Round.PREFLOP

        # 1. ポジション割り当て
        self.gs = position_service.assign_positions(self.gs)
        
        # 2. ブラインド徴収
        self.gs = hand_manager.collect_blinds(self.gs)
        
        # 3. カード配布
        self.gs = hand_manager.deal_hole_cards(self.gs)
        
        # 4. 最初のアクションプレイヤーを設定
        self.gs = round_manager.set_first_action_player(self.gs)
        
        # AIのターンなら即座にアクションさせる
        self._run_ai_action_if_turn()

    def process_player_action(self, seat_index: int, action_type: ActionType, amount: int = 0):
        """プレイヤーのアクションを処理し、ゲームを進行させる"""
        # アクション適用
        if action_type == ActionType.FOLD:
            self.gs = action_service.validate_and_apply_fold(self.gs, seat_index)
        elif action_type == ActionType.CALL:
             self.gs = action_service.validate_and_apply_call(self.gs, seat_index)
        # ... RAISEなどの他のアクションも同様に ...
        
        # 次の状態へ遷移
        self.gs = round_manager.advance_to_next_player_or_round(self.gs)
        
        self._check_hand_completion()
        
        # AIのターンなら即座にアクションさせる
        self._run_ai_action_if_turn()


    def _run_ai_action_if_turn(self):
        """現在のプレイヤーがAIであれば、アクションを決定・実行する"""
        current_seat_index = self.gs.current_seat_index
        if current_seat_index is None:
            return
            
        current_player = self.gs.table.seats[current_seat_index].player
        if current_player and current_player.is_ai:
            action_type, amount = self.ai_service.decide_action(self.gs, current_seat_index)
            if action_type:
                self.process_player_action(current_seat_index, action_type, amount)
    
    def _check_hand_completion(self):
        """ハンドが終了したか判定し、終了していれば後処理を行う"""
        players_in_hand = [s for s in self.gs.table.seats if s.status not in ["FOLDED", "OUT"]]
        
        hand_over = False
        if len(players_in_hand) <= 1:
            hand_over = True
        if self.gs.current_round == Round.SHOWDOWN:
            hand_over = True

        if hand_over:
            self.gs = hand_manager.distribute_pot(self.gs)
            self.gs.status = GameStatus.HAND_COMPLETE