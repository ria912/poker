# models/round_manager.py
from models.action import Action
from models.position import ACTION_ORDER
from models.enum import Round, State

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.action_order = []
        self.action_index = 0
        self.waiting_for_human = False

    def start_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0

        self.waiting_for_human = False

    def reset_for_new_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0

        for p in self.action_order:
            p.reset_for_new_round()

        self.table.last_raiser = None
        self.waiting_for_human = False

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
    
    def step_ai_actions(self):
        # AIが行動し、人間の番になるまで繰り返す
        while self.action_index < len(self.action_order):
            current_player = self.action_order[self.action_index]

            if current_player.is_human:
                self.waiting_for_human = True
                return State.WAITING_FOR_HUMAN

            # AIアクション
            try:
                action, amount = current_player.decide_action(self.table)
            except Exception as e:
                raise RuntimeError(f"AIアクション失敗: {e}")

            Action.apply_action(current_player, self.table, action, amount)
            self.log_action(current_player, action, amount)

            if action in [Action.BET, Action.RAISE] and current_player.current_bet == self.table.current_bet:
                self.table.last_raiser = current_player
                self.reset_has_acted_except(current_player)

            self.action_index += 1

            if self.action_index >= len(self.action_order):
                if self.is_betting_round_over():
                    return self.advance_round()
                else:
                    self.action_order = self.get_action_order()
                    self.action_index = 0

    def receive_human_action(self, action, amount):
        current_player = self.action_order[self.action_index]
        if not current_player.is_human:
            raise RuntimeError("receive_human_action内でAIを検出しました。")

        Action.apply_action(current_player, self.table, action, amount)
        self.log_action(current_player, action, amount)

        if action in [Action.BET, Action.RAISE] and current_player.current_bet == self.table.current_bet:
            self.table.last_raiser = current_player
            self.reset_has_acted_except(current_player)

        self.action_index += 1
        self.waiting_for_human = False

        return self.step_ai_actions()

    def reset_has_acted_except(self, current_player):
        for p in self.action_order:
            if p != current_player:
                p.has_acted = False

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
            self.reset_for_new_round()
            return self.step_ai_actions()

        elif self.table.round == Round.FLOP:
            self.table.deal_turn()
            self.table.round = Round.TURN
            self.reset_for_new_round()
            return self.step_ai_actions()

        elif self.table.round == Round.TURN:
            self.table.deal_river()
            self.table.round = Round.RIVER
            self.reset_for_new_round()
            return self.step_ai_actions()

        elif self.table.round == Round.RIVER:
            self.table.round = Round.SHOWDOWN
            self.table.award_pot_to_winner()
            return State.HAND_OVER

        self.start_new_betting_round()
        return State.ROUND_OVER

    def log_action(self, current_player, action, amount):
        self.table.action_log.append({
            "player": current_player.name,
            "action": action,
            "amount": amount,
            "round": self.table.round.title(),
        })