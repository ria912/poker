# backend/models/round.py
from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.enum import Round, Status
from backend.models.action import ActionManager, Action

class RoundLogic:
    """ラウンドの状態管理も行います。"""

    def __init__(self, table: Table):
        self.table = table
        self.status = Status.ROUND_CONTINUE

    def advance_round(self):
        """次のベットラウンドに移行します。 showdown時にラウンド完了。"""
        next_round = Round.next(self.table.round)
        if next_round == Round.SHOWDOWN:
            self.table.round = Round.SHOWDOWN
            self.status = Status.ROUND_OVER
            # Showdownの処理を行う
            self.table.showdown()
            self.table.pot.get_winners() # tableにclass Potを作る？Tableに書く？

        else:
            self.table.round = next_round
            self.table.reset()
            
            if self.table.round == Round.FLOP:
                self.table.deck.deal_flop()
            elif self.table.round == Round.TURN:
                self.table.deck.deal_turn()
            elif self.table.round == Round.RIVER:
                self.table.deck.deal_river()

            self.status = Status.ROUND_CONTINUE


class OrderManager:
    """アクション管理も行うRound Manager。"""

    def __init__(self, table: Table):
        self.table = table
        self.round_logic = RoundLogic(table)

        self.action_order: List[Seat] = self.compute_action_order()
        self.action_index = 0
        self.current_seat: Optional[Seat] = None
    
    def reset(self):
        """ラウンド開始時に呼び出して状態をリセット。"""
        self.action_order = self.compute_action_order()
        self.action_index = 0

    def compute_action_order(self) -> List[Seat]:
        """プリフロップはBBの次、以降はBTNの次から時計回りにアクション順を作る。"""
        seats = self.table.seats
        n = len(seats)

        if self.table.round == Round.PREFLOP:
            base_index = (self.table.btn_index + 2) % n  # = BB
        else:
            base_index = self.table.btn_index
    
        action_order = []
    
        for offset in range(1, n + 1):  # 1つ先から時計回りに全席走査
            i = (base_index + offset) % n
            player = seats[i].player
            # アクション可能なプレイヤーのみを追加
            if player and player.is_active and not player.has_acted:
                action_order.append(seats[i])

        return action_order

    def get_current_seat(self) -> Optional[Seat]:
        while self.action_index < len(self.action_order):
            seat = self.action_order[self.action_index]
            if seat.player and not seat.player.has_acted:
                return seat
 
        self.status = Status.ORDER_OVER
        return None

    def proceed(self):
        """次のプレイヤーにアクションしてもらう。完了時に次のラウンドに移行。"""
        if self.is_round_complete():
            self.round_logic.advance_round()
            self.reset()
            return

        current = self.get_current_seat()
        if current and current.player:
            action, amount = current.player.act(self.table)  # AI,Human共通
            print(f"{current.player.name} が {action},{amount} を選択。")
            ActionManager.apply_action(current.player, self.table, action, amount)

            if action in Action.betting_actions() and current.player.stack == self.table.current_bet:
                for seat in self.action_order:
                    if seat != current and seat.player.is_active:
                        seat.player.has_acted = False
                        
            self.action_index += 1
    
    def is_round_complete(self) -> bool:
        """アクション順の全プレイヤーがアクション済みかどうかを確認。"""
        for seat in self.action_order:
            if seat.player and seat.player.is_active and not seat.player.has_acted:
                return False
        return True
