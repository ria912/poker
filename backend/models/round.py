# models/round_manager.py
from backend.models.action import Action
from backend.models.position import ACTION_ORDER
from backend.models.enum import Round, Status

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.action_log = []
        self.action_order = []
        self.action_index = 0

    def start_round(self):
        self.action_log = []
        self.action_order = self.get_action_order()
        self.action_index = 0

    def reset_for_next_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0

        self.table.last_raiser = None

    def get_action_order(self):
        active_players = [p for p in self.table.seats if p.is_active and not p.has_acted]

        if self.table.round == Round.PREFLOP:
            start_index = 2  # LJから
        else:
            start_index = 0  # SBから
    
        ordered_positions = ACTION_ORDER[start_index:] + ACTION_ORDER[:start_index]
    
        # ポジション順でアクティブプレイヤーを並べ替え
        ordered_players = [
            p for pos in ordered_positions
            for p in active_players if p.position == pos
        ]
        return ordered_players
    
    def step_one_action(self):
        # 全アクション済み or ハンド終了
        if self.table.round == Round.SHOWDOWN:
            return Status.HAND_OVER

        # まだアクション順がない（ラウンド開始直後）
        if not self.action_order or self.action_index >= len(self.action_order):
            self.action_order = self.get_action_order()
            self.action_index = 0

        # 次のプレイヤーを取得
        if self.action_index < len(self.action_order):
            current_player = self.action_order[self.action_index]
        else:
            # ラウンド終了チェックと進行
            if self.is_betting_round_over():
                return self.advance_round()
            else:
                self.action_order = self.get_action_order()
                self.action_index = 0
                return Status.RUNNING

        # 人間の番なら処理を止める
        if current_player.is_human:
            return Status.WAITING_FOR_HUMAN
        else:
            return self.step_apply_action(current_player)

    def step_apply_action(self, current_player):
        try:
            action, amount = current_player.decide_action(self.table)
        except Exception as e:
            raise RuntimeError(f"アクション取得失敗: {e}")

        Action.apply_action(current_player, self.table, action, amount)
        self.log_action(current_player, action, amount)

        # レイズした場合、他プレイヤーの has_acted をリセット
        if action in [Action.BET, Action.RAISE] and current_player.current_bet == self.table.current_bet:
            self.table.last_raiser = current_player
            for p in self.table.seats:
                if p and p.is_active and p != current_player:
                    p.has_acted = False

        self.action_index += 1

        return Status.RUNNING

    def is_betting_round_over(self):
        active = [p for p in self.table.seats if p.is_active]
        if len(active) <= 1:
            return True
        for p in active:
            if not p.has_acted or p.current_bet != self.table.current_bet:
                return False
        return True

    def advance_round(self):
        # Round enum に基づく遷移
        if self.table.round == Round.PREFLOP:
            self.table.deal_flop()
            self.table.round = Round.FLOP
            self.reset_for_next_round()
            return self.step_one_action()

        elif self.table.round == Round.FLOP:
            self.table.deal_turn()
            self.table.round = Round.TURN
            self.reset_for_next_round()
            return self.step_one_action()

        elif self.table.round == Round.TURN:
            self.table.deal_river()
            self.table.round = Round.RIVER
            self.reset_for_next_round()
            return self.step_one_action()

        elif self.table.round == Round.RIVER:
            self.table.round = Round.SHOWDOWN
            self.table.award_pot_to_winner()
            return Status.HAND_OVER

        return Status.ROUND_OVER

    def log_action(self, current_player, action, amount):
        self.action_log.append({
            "player": current_player.name,
            "action": action,
            "amount": amount,
            "round": self.table.round.title(),
        })