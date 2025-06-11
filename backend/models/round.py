# models/round_manager.py
from backend.models.action import Action
from backend.models.enum import Round, Position, Status

class RoundManager:

    ROUND_ORDER: list[Round] = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]

    def __init__(self, table):
        self.table = table
        self.action_log = []
        self.action_order = []
        self.action_index = 0
        self.status = Status.AI_ACTED

    def reset_action_order(self):
        self.action_order = self.get_action_order()
        self.action_index = 0

    def get_action_order(self):
        action_order = Position.ASSIGN_ORDER
        active_players = [
            seat.player for seat in self.table.seats
            if seat.player and seat.player.is_active and not seat.player.has_acted
        ]

        if self.table.round == Round.PREFLOP:
            start_index = 2  # LJから
        else:
            start_index = 0  # SBから
    
        ordered_positions = action_order[start_index:] + action_order[:start_index]
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
            self.status = Status.ROUND_OVER
            return self.status
    
        if self.action_index >= len(self.action_order):
            if self.is_betting_round_over():
                return self.advance_round()
            else:
                self.reset_action_order()
    
        current_player = self.current_player
        if current_player.is_human:
            self.status = Status.WAITING_FOR_HUMAN
            return self.status
        else:
            self.status = Status.WAITING_FOR_AI
            return self.step_apply_action(current_player)

    def step_apply_action(self, current_player=None):
        if current_player is None:
            current_player = self.current_player
        try:
            action, amount = current_player.decide_action(self.table)
        except Exception as e:
            raise RuntimeError(f"アクション取得失敗: {e}")

        Action.apply_action(self.table, current_player, action, amount)
        self.log_action(current_player, action, amount)

        # レイズした場合、他プレイヤーの has_acted をリセット
        if action in [Action.BET, Action.RAISE] and current_player.bet_total == self.table.current_bet:
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
            if not p.has_acted or p.bet_total != self.table.current_bet:
                return False
        return True

    def advance_until_human_or_end(self):
        while self.status == Status.AI_ACTED:
            self.step_one_action()
        return self.status

    def advance_round(self):
        next_round = Round.next(self.table.round)

        if next_round == Round.FLOP:
            self.table.deal_flop()
        elif next_round == Round.TURN:
            self.table.deal_turn()
        elif next_round == Round.RIVER:
            self.table.deal_river()
        elif next_round == Round.SHOWDOWN:
            self.table.round = next_round
            self.table.award_pot_to_winner()
            return Status.HAND_OVER

        self.table.round = next_round
        self.reset_action_order()
        self.table.last_raiser = None
        return self.step_one_action()


    def log_action(self, current_player, action, amount):
        self.action_log.append({
            "round": self.table.round.title(),
            "player": current_player.name,
            "current_bet": current_player.current_bet,
            "action": action,
            "amount": amount,
        })