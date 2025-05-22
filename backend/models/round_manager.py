# models/round_manager.py
from models.table import Table
from models.position import ASSIGNMENT_ORDER
from models.action import Action

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_index = 0
        self.action_order = self.get_action_order()
        self.waiting_for_human = False

    def get_action_order(self):
        start_pos = 'BB' if self.table.round == 'preflop' else 'BTN'
        pos_to_player = {p.position: p for p in self.table.get_active_players()}

        # ポジションをスタート位置の次から時計回りに並べる
        ordered_positions = ASSIGNMENT_ORDER
        start = ordered_positions.index(start_pos)
        rotated = ordered_positions[start + 1:] + ordered_positions[:start + 1]

        # 実際に存在するプレイヤーのみ返す
        return [pos_to_player[pos] for pos in rotated if pos in pos_to_player]

    def _start_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        self.waiting_for_human = False
        for p in self.table.get_active_players():
            p.has_acted = False

    def proceed_one_action(self):
        """
        1アクション進行する。
        人間プレイヤーの入力待ちになる場合は Exception を投げる。
        """
        if self.round == 'showdown':
            self._showdown()
            return "hand_over"

        if self.is_betting_round_over():
            return self._advance_round()

        if self.action_index >= len(self.action_order):
            self.action_index = 0  # 念のため

        current_player = self.action_order[self.action_index]

        try:
            action, amount = current_player.decide_action(self.table)
        except Exception as e:
            if str(e) == "waiting_for_human_action":
                self.waiting_for_human = True
                raise  # 呼び出し元で "waiting_for_human" を返す
            raise  # その他の例外はそのまま再スロー

        Action.apply_action(current_player, self.table, action, amount)

        if action in [Action.BET, Action.RAISE]:
            self.table.last_raiser = current_player
            for p in self.table.get_active_players():
                if p != current_player:
                    p.has_acted = False

        self.action_index += 1

        if self.is_betting_round_over():
            return self._advance_round()
        return "ai_acted"

    def is_betting_round_over(self):
        active_players = self.table.get_active_players()

        if len(active_players) <= 1:
            return True

        for p in active_players:
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
            self.table.is_hand_in_progress = False  # ✅ 追加（状態フラグ反映）
            return "hand_over"

        self._start_betting_round()
        return "round_over"
    
    # 人間アクション関連 -----------------------------------

    def resume_after_human_action(self):
        """人間アクションを受け取ったあと再開"""
        self.waiting_for_human = False
        try:
            return self.proceed_one_action()
        except Exception as e:
            if str(e) == "waiting_for_human_action":
                self.waiting_for_human = True
                return "waiting_for_human"
            raise
