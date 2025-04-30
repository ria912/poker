from collections import deque
from models.action import Action
from models.position import assignment_order

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.phase = 'preflop'  # preflop, flop, turn, river, showdown
        self.players_to_act = deque()
        self.last_raiser = None

    def start_new_round(self):
        self.table.start_hand()
        self.phase = 'preflop'
        self.setup_action_queue()

    def setup_action_queue(self):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        ordered = sorted(active, key=lambda p: assignment_order.index(p.position))

        if self.phase == "preflop":
            # BBの次からアクション開始
            bb_index = next((i for i, p in enumerate(ordered) if p.position == "BB"), 0)
            ordered = ordered[bb_index + 1:] + ordered[:bb_index + 1]

        self.players_to_act = deque(ordered)
        self.last_raiser = None

    def proceed_action(self):
        if not self.players_to_act:
            return  # 念のため

        player = self.players_to_act.popleft()
        if player.has_folded or player.stack == 0:
            return

        legal = Action.get_legal_actions(player, self.table)

        if player.is_human:
            action, amount = player.decide_action({
                "actions": legal,
                "pot": self.table.pot,
                "current_bet": self.table.current_bet,
                "min_bet": self.table.min_bet
            })
        else:
            # AIはCALLまたはCHECK（テスト用）
            if Action.CALL in legal:
                action = Action.CALL
            elif Action.CHECK in legal:
                action = Action.CHECK
            else:
                action = Action.FOLD
            amount = 0

        before_bet = self.table.current_bet
        Action.apply_action(player, action, self.table, amount)

        # レイズ系アクションによって current_bet が更新された場合
        if self.table.current_bet > before_bet and action in [Action.BET, Action.RAISE, Action.ALL_IN]:
            self.last_raiser = player
            self.reset_players_to_act_from(player)

    def reset_players_to_act_from(self, raiser):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        ordered = sorted(active, key=lambda p: assignment_order.index(p.position))

        if raiser not in ordered:
            return  # エラー防止（万が一）

        start_index = ordered.index(raiser)
        reordered = ordered[start_index + 1:] + ordered[:start_index + 1]
        self.players_to_act = deque(reordered)

    def should_advance_phase(self):
        return not self.players_to_act

    def advance_phase(self):
        phase_order = ['preflop', 'flop', 'turn', 'river', 'showdown']
        next_index = phase_order.index(self.phase) + 1
        if next_index < len(phase_order):
            self.phase = phase_order[next_index]
            if self.phase == 'flop':
                self.table.community_cards = [self.table.deck.draw() for _ in range(3)]
            elif self.phase in ['turn', 'river']:
                self.table.community_cards.append(self.table.deck.draw())
            self.setup_action_queue()
        else:
            print("Showdown or hand is over")