# models/round_manager.py
from models.table import Table
from models.position import ASSIGNMENT_ORDER
from models.action import Action

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.round = self.table.round
        self.action_index = 0
        self.action_order = self.get_action_order()
        self.waiting_for_human = False

    def get_action_order(self):
        start_pos = 'BB' if self.round == 'preflop' else 'BTN'
        pos_to_player = {p.position: p for p in self.table.get_active_players()}

        # スタート位置の次から時計回りにポジションを並べる
        ordered_positions = ASSIGNMENT_ORDER
        start = ordered_positions.index(start_pos)
        rotated = ordered_positions[start + 1:] + ordered_positions[:start + 1]

        # 実際にいるプレイヤーだけ返す
        return [pos_to_player[pos] for pos in rotated if pos in pos_to_player]

    def _start_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        self.waiting_for_human = False
        for p in self.table.get_active_players():
            p.has_acted = False
            
    # 1アクション進める。人間の入力待ちなら 'waiting_for_human' を返す。
    def proceed_one_action(self):
        # ショーダウンなら終了
        if self.round == 'showdown':
            self._showdown()
            return "hand_over"
        # ベッティングラウンドが終了していれば、次のストリートへ進む
        if self.is_betting_round_over():
            return self._advance_round()
        # 行動順が一周した場合はリセット
        if self.action_index >= len(self.action_order):
            self.action_index = 0

        current_player = self.action_order[self.action_index]

        # === 人間プレイヤーの場合 ===
        if current_player.is_human:
            result = current_player.decide_action(self.table)
            if result is None:
                self.waiting_for_human = True
                return "waiting_for_human"
            action, amount = result
        # === AIプレイヤーの場合 ===
        else:
            action, amount = current_player.decide_action(self.table)
        # アクションを適用
        Action.apply_action(current_player, self.table, action, amount)
        current_player.has_acted = True
        # レイズ時の処理
        if action in [Action.BET, Action.RAISE]:
            self.table.last_raiser = current_player
            for p in self.table.get_active_players():
                if p != current_player:
                    p.has_acted = False
        # 次のプレイヤーへ
        self.action_index += 1
        # 再チェック：ベッティングラウンド終了？
        if self.is_betting_round_over():
            return self._advance_round()

        return "ai_acted"
    
    def is_betting_round_over(self):
        active_players = self.table.get_active_players()

        if len(active_players) <= 1:
            return True
        for p in active_players:
            if not p.has_acted:
                return False
            if p.current_bet != self.table.current_bet:
                return False
        return True

    def _advance_round(self):
        if self.round == 'preflop':
            self.round = 'flop'
            self.table.deal_flop()
        elif self.round == 'flop':
            self.round = 'turn'
            self.table.deal_turn()
        elif self.round == 'turn':
            self.round = 'river'
            self.table.deal_river()
        elif self.round == 'river':
            self.round = 'showdown'
            self.table.award_pot_to_winner()
            return "hand_over"

        self._start_betting_round()
        return "round_over"
