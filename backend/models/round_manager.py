# models/round_manager.py
from models.action import Action
from models.human_player import WaitingForHumanAction
from models.position import ACTION_ORDER
from enum import Enum

class Round(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.action_order = []
        self.action_index = 0
        self.waiting_for_human = False

    def start_new_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        for p in self.action_order:
            p.has_acted = False

    def get_action_order(self):
        players = [p for p in self.table.seats if p.is_active]
        return sorted(players, key=lambda p: ACTION_ORDER.index(p.position))

    def step_ai_actions(self):
        """AIが行動し、人間の番になるまで繰り返す"""
        while self.action_index < len(self.action_order):
            player = self.action_order[self.action_index]

            if player.is_human:
                self.waiting_for_human = True
                return "waiting_for_human"

            # AIアクション
            action, amount = player.decide_action(self.table)
            Action.apply_action(player, self.table, action, amount)
            self.log_action(player, action, amount)

            if action in [Action.BET, Action.RAISE]:
                self.table.last_raiser = player
                for p in self.action_order:
                    if p != player:
                        p.has_acted = False

            self.action_index += 1

            if self.action_index >= len(self.action_order):
                if self.is_betting_round_over():
                    return self.advance_round()
                else:
                    self.action_order = self.get_action_order()
                    self.action_index = 0

        return "ai_done"

    def receive_human_action(self, action, amount):
        player = self.action_order[self.action_index]
        Action.apply_action(player, self.table, action, amount)
        self.log_action(player, action, amount)

        if action in [Action.BET, Action.RAISE]:
            self.table.last_raiser = player
            for p in self.action_order:
                if p != player:
                    p.has_acted = False

        self.action_index += 1
        self.waiting_for_human = False

        if self.action_index >= len(self.action_order):
            if self.is_betting_round_over():
                return self.advance_round()
            else:
                self.action_order = self.get_action_order()
                self.action_index = 0

        return self.step_ai_actions()

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
        elif self.table.round == Round.FLOP:
            self.table.deal_turn()
            self.table.round = Round.TURN
        elif self.table.round == Round.TURN:
            self.table.deal_river()
            self.table.round = Round.RIVER
        elif self.table.round == Round.RIVER:
            self.table.round = Round.SHOWDOWN
            self.table.award_pot_to_winner()
            return "hand_over"

        self.start_new_betting_round()
        return "round_over"

    def log_action(self, player, action, amount):
        self.table.action_log.append({
            "player": player.name,
            "action": action,
            "amount": amount,
            "round": self.table.round
        })