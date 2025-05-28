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
        self.action_index = 0
        self.waiting_for_human = False
        self.action_order = self.get_action_order()  # 初期順番

    def get_action_order(self):
        """ポジション順にアクティブプレイヤーを並べる。プリフロップのみBTNの次から。"""
        players = [p for p in self.table.seats if p and p.is_active]
        # アクション順に並び替え
        ordered = sorted(players, key=lambda p: ACTION_ORDER.index(p.position))
        
        if self.table.round == 'preflop':
            btn_index = ACTION_ORDER.index('BTN')
            # BTNの次（SB）から始めるため、BTNを基点にローテート
            rotated = ACTION_ORDER[btn_index+1:] + ACTION_ORDER[:btn_index+1]
            ordered = sorted(players, key=lambda p: rotated.index(p.position))
        return ordered

    def _start_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        self.waiting_for_human = False
        for p in self.action_order:
            p.has_acted = False

    def proceed_one_action(self):
        """1アクション進行。人間入力待ちの場合は例外で返す。"""
        if self.table.round == 'showdown':
            self._showdown()
            return "hand_over"

        if self.is_betting_round_over():
            return self._advance_round()

        if not self.action_order:
            return "round_over"  # アクティブプレイヤーがいない

        if self.action_index >= len(self.action_order):
            self.action_index = 0  # 巻き戻し

        current_player = self.action_order[self.action_index]

        if not current_player.is_active:
            self.action_index += 1
            return self.proceed_one_action()  # スキップ

        try:
            action, amount = current_player.decide_action(self.table)
        except WaitingForHumanAction:
            self.waiting_for_human = True
            raise
        except Exception:
            raise

        Action.apply_action(current_player, self.table, action, amount)
        self.log_action(current_player, action, amount)

        if action in [Action.BET, Action.RAISE]:
            self.table.last_raiser = current_player
            for p in self.action_order:
                if p != current_player:
                    p.has_acted = False

        current_player.has_acted = True
        self.action_index += 1

        if self.is_betting_round_over():
            return self._advance_round()

        return "ai_acted"

    def is_betting_round_over(self):
        """全員がコールorフォールド済みなら終了"""
        active = [p for p in self.table.seats if p and p.is_active]
        if len(active) <= 1:
            return True
        for p in active:
            if not p.has_acted or p.current_bet != self.table.current_bet:
                return False
        return True

    def _advance_round(self):
        if self.table.round == 'preflop':
            self.table.round = 'flop'
            self.table.deal_flop()
        elif self.table.round == 'flop':
            self.table.round = 'turn'
            self.table.deal_turn()
        elif self.table.round == 'turn':
            self.table.round = 'river'
            self.table.deal_river()
        elif self.table.round == 'river':
            self.table.round = 'showdown'
            self.table.award_pot_to_winner()
            self.table.is_hand_in_progress = False
            return "hand_over"

        self._start_betting_round()
        return "round_over"

    def log_action(self, player, action, amount):
        self.table.action_log.append({
            "player": player.name,
            "action": action,
            "amount": amount,
            "round": self.table.round
        })

    def resume_after_human_action(self):
        self.waiting_for_human = False
        try:
            return self.proceed_one_action()
        except WaitingForHumanAction:
            self.waiting_for_human = True
            return "waiting_for_human"