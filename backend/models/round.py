# models/round.py
from backend.models.table import Table, Player
from backend.models.action import Action, ActionManager
from backend.models.enum import Round, Status, Position
from typing import List, Optional

class ActionOrder:
    def __init__(self, table: Table):
        self.table = table
        self.action_order = []
        self.action_index = 0

    def reset(self) -> List[Player.position]:
        # is_active かつ has_acted == False のプレイヤーを取得
        active_unacted_players = [
            p for p in self.table.get_active_players() if not p.has_acted
        ]
        # ASSIGN_ORDER順にソート
        sorted_order = sorted(
            active_unacted_players,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
            if p.position in Position.ASSIGN_ORDER else 999
        )
        self.action_index = 0

        if self.table.round == Round.PREFLOP and not self.action_order:
            # BBの次からアクション開始（ASSIGN_ORDER内でのBBの次）
            try:
                bb_index = next(
                    i for i, p in enumerate(sorted_order) if p.position == Position.BB
                )
                # BBの次（UTG）スタートに並べ直して返す
                self.action_order = sorted_order[bb_index + 1:] + sorted_order[:bb_index + 1]
            except Exception as e:
                raise RuntimeError(f"bb_indexを取得できません。: {e}")
        # ポストフロップ,None以外はそのまま返す
        self.action_order = sorted_order

    def get_current_player(self) -> Optional[Table.seats]:
        if self.action_index < len(self.action_order):
            return self.action_order[self.action_index]
        return None

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_order = ActionOrder(table)
        self.status = Status.RUNNING # step()待ちフラグ（初期）

    def reset(self):
        self.table.reset()
        self.action_order.reset()

    def step(self):
        if self.action_index >= len(self.action_order):
            return self.check_next_action_or_end()

        current_player = self.action_order.get_current_player()
        if current_player.is_human:
            self.status = Status.WAITING_FOR_HUMAN
        else:
            self.status = Status.WAITING_FOR_AI
            self.step_apply_action(current_player)
        return self.status

    def step_apply_action(self, current_player, action, amount):
        if current_player is None:
            current_player = self.action_order.get_current_player()

        if action is None:
            self.status = Status.ERROR
            raise ValueError("アクションが指定されていません。")

        ActionManager.apply_action(self.table, current_player, action, amount)
        self.log_action(current_player, action, amount)
        # レイズした場合、他プレイヤーの has_acted をリセット
        if action in Action.betting_actions() and current_player.bet_total == self.table.current_bet:
            self.table.last_raiser = current_player
            for p in self.table.seats:
                if p and p.is_active and p != current_player:
                    p.has_acted = False

        self.action_index += 1
        
        if current_player.is_human:
            self.status = Status.HUMAN_ACTED
        else:
            self.status = Status.AI_ACTED
        return self.status
    
    def check_next_action_or_end(self):
        # アクティブプレイヤーが1人 → ハンド終了
        active_players = [p for p in self.table.seats if p and p.is_active]
        if len(active_players) == 1:
            self.status = Status.HAND_OVER

        self.action_order = ActionOrder.reset()
        # action_orderがない → ラウンド終了
        if not self.action_order:
            self.status = Status.ODER_OVER
            self.advance_round()
        # アクション継続
        else:
            self.status = Status.RUNNING
        return self.status

    def advance_round(self):
        next_round = Round.next(self.table.round)
        if next_round == Round.SHOWDOWN:
            self.table.round = Round.SHOWDOWN
            self.status = Status.ROUND_OVER
            return self.status
        
        self.table.round = next_round

        if self.table.round == Round.FLOP:
            self.table.deal_flop()
        elif self.table.round == Round.TURN:
            self.table.deal_turn()
        elif self.table.round == Round.RIVER:
            self.table.deal_river()

        self.start_new_round()
        self.status = Status.RUNNING
        return self.status
    
    def log_action(self, current_player, action, amount):
        """アクションをログに記録する。"""
        log_entry = {
            'player': current_player.name,
            'action': action.name,
            'amount': amount,
            'round': self.table.round.name,
            'timestamp': self.table.get_current_time()
        }
        self.table.action_log.append(log_entry)
        print(f"Action logged: {log_entry}")