# models/round_manager.py
from models.table import Table
from models.position import ASSIGNMENT_ORDER
from models.action import Action

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.street = 'preflop'
        self.action_index = 0
        self.last_raiser = None
        self.action_order = []
        self.waiting_for_human = False
        self.human_action = None  # 人間プレイヤーのアクション（action, amount）

    def set_human_action(self, action_tuple):
        """ 外部（API）から人間プレイヤーのアクションをセットする """
        self.human_action = action_tuple

    def _start_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        self.waiting_for_human = False
        for p in self.table.seats:
            if p and not p.has_folded and not p.has_all_in and not p.has_left:
                p.has_acted = False

    def proceed_one_action(self):
        """ 1アクション進める。人間の場合は 'waiting_for_human' を返す """
        if self.street == 'showdown':
            self._showdown()
            return "hand_over"

        if self.is_betting_round_over():
            return self._advance_street()

        if self.action_index >= len(self.action_order):
            self.action_index = 0  # 念のため保険

        current_player = self.action_order[self.action_index]

        if current_player.is_human == True:
            if self.human_action is None:
                self.waiting_for_human = True
                return "waiting_for_human"
            action, amount = self.human_action
            self.human_action = None
        else:
            legal_actions = Action.get_legal_actions(current_player, self.table)
            action, amount = current_player.decide_action({
            "legal_actions": legal_actions,
            "table": self.table.to_dict(),
            "current_bet": self.table.current_bet,
            "min_bet": self.table.min_bet,
            "has_acted": current_player.has_acted
    })

        Action.apply_action(current_player, action, self.table, amount)
        current_player.last_action = action
        current_player.has_acted = True

        if action == Action.FOLD:
            current_player.has_folded = True

        if action in [Action.BET, Action.RAISE]:
            self.last_raiser = current_player
            for p in self.table.seats:
                if p and not p.has_folded and not p.has_all_in and not p.has_left and p != current_player:
                    p.has_acted = False

        self.action_index += 1

        if self.is_betting_round_over():
            return self._advance_street()
        return "ai_acted"

    def resume_after_human_action(self):
        """ 人間のアクション完了後に次へ進める """
        self.waiting_for_human = False
        return self.proceed_one_action()

    def get_action_order(self):
        start_pos = 'BB' if self.street == 'preflop' else 'BTN'
        pos_to_player = {
            p.position: p for p in self.table.seats
            if p and not p.has_folded and not p.has_all_in and not p.has_left
        }
        start_index = ASSIGNMENT_ORDER.index(start_pos)
        action_order = [
            ASSIGNMENT_ORDER[(start_index + 1 + i) % len(ASSIGNMENT_ORDER)]
            for i in range(len(ASSIGNMENT_ORDER))
        ]
        # actieなプレイヤーだけを返す
        return [pos_to_player[pos] for pos in action_order if pos in pos_to_player]

    def is_betting_round_over(self):
        active_players = [
            p for p in self.table.seats
            if p and not p.has_folded and not p.has_all_in and not p.has_left
        ]
        if len(active_players) <= 1:
            return True
        for p in active_players:
            if not p.has_acted:
                return False
            if p.has_all_in == True:
                continue
            if not p.has_all_in and p.current_bet != self.table.current_bet:
                return False
        return True

    def _advance_street(self):
        """ ストリートを進行する """
        if self.street == 'preflop':
            self.street = 'flop'
            self._deal_flop()
        elif self.street == 'flop':
            self.street = 'turn'
            self._deal_turn()
        elif self.street == 'turn':
            self.street = 'river'
            self._deal_river()
        elif self.street == 'river':
            self.street = 'showdown'
            self._showdown()
            return "hand_over"

        self._start_betting_round()
        return "round_over"

    def _deal_flop(self):
        flop = [self.table.deck.draw() for _ in range(3)]
        self.table.community_cards.extend(flop)

    def _deal_turn(self):
        self.table.community_cards.append(self.table.deck.draw())

    def _deal_river(self):
        self.table.community_cards.append(self.table.deck.draw())

    def _showdown(self):
        active_players = [
            p for p in self.table.seats
            if p and not p.has_folded and not p.has_left and p.stack >= 0
        ]
        if not active_players:
            return
        winner = next((p for p in active_players if p.name == "YOU"), active_players[0])
        winner.stack += self.table.pot
        self.table.pot = 0
