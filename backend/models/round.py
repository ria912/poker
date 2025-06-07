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
        self.status = Status.DEF

    def reset_for_new_round(self):
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
    
    @property
    def current_player(self):
        current_player = self.action_order[self.action_index]
        return current_player
    
    def step_one_action(self):
        if self.table.round == Round.SHOWDOWN:
            return Status.ROUND_OVER
    
        if not self.action_order or self.action_index >= len(self.action_order):
            if self.is_betting_round_over():
                return self.advance_round()
            self.reset_for_new_round()
    
        current_player = self.current_player
        if current_player.is_human:
            self.status = Status.WAITING_HUMAN
            return self.status
        elif:
            self.status = Status.WAITING_AI
            return self.step_apply_action(current_player)

    def step_apply_action(self, current_player):
        if current_player is None:
            current_player = self.current_player
        try:
            action, amount = current_player.decide_action(self.table)
        except Exception as e:
            raise RuntimeError(f"アクション取得失敗: {e}")

        Action.apply_action(self.table, current_player, action, amount)
        self.log_action(current_player, action, amount)

        # レイズした場合、他プレイヤーの has_acted をリセット
        if action in [Action.BET, Action.RAISE] and current_player.current_bet == self.table.current_bet:
            self.table.last_raiser = current_player
            for p in self.table.seats:
                if p and p.is_active and p != current_player:
                    p.has_acted = False

        self.action_index += 1
        
        self.status = Status.AI_ACTED
        return self.status

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

        self.status = Status.ROUND_OVER
        return self.status
    
    def advance_until_human_or_end(self):
        while self.status == Status.AI_ACTED:
            self.step_one_action()
        return self.status

    def log_action(self, current_player, action, amount):
        self.action_log.append({
            "round": self.table.round.title(),
            "player": current_player.name,
            "current_bet": current_player.current_bet,
            "action": action,
            "amount": amount,
        })