# backend/models/round.py
from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.player import Player
from backend.models.enum import Round, Status, Position

class RoundLogic:
    """ラウンドの状態管理も行います。"""

    def __init__(self, table: Table):
        self.table = table
        self.round = self.table.round
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
        self.active_players = self.table.get_active_players()

        self.action_order: List[Seat] = self.compute_action_order()
        self.action_index = 0
    
    def reset(self):
        """ラウンド開始時に呼び出して状態をリセット。"""
        self.active_players = self.table.get_active_players()
        self.action_order = self.compute_action_order()
        self.action_index = 0

    def compute_action_order(self) -> List[Seat]:
        """BBまたはBTNを基準に、席順でアクションプレイヤーを並べる"""
        round = self.table.round
        seats = self.table.seats
    
        base_pos = Position.BB if round == Round.PREFLOP else Position.BTN
    
        # 基準となる seat index を取得
        base_index = self.table.get_seat_index_by_position(base_pos)
        n = len(seats)
    
        action_order: List[Seat] = []
    
        for offset in range(1, n + 1):  # 1つ先から時計回りに全席走査
            i = (base_index + offset) % n
            player = seats[i].player
            if player and player.is_active and not player.has_acted:
                action_order.append(seats[i])

        return action_order

    def get_next_seat(self) -> Optional[Seat]:
        if self.action_index >= len(self.action_order):
            self.status = Status.ORDER_OVER
            return None

        seat = self.action_order[self.action_index]
        if not seat.player.has_acted:
            return seat

        # has_acted ならスキップして次へ
        self.action_index += 1
        return self.get_next_seat()

    def proceed(self):
        """次のプレイヤーにアクションしてもらう。完了時に次のラウンドに移行。"""
        if self.is_round_complete():
            self.round_logic.advance_round()
            self.reset()
            return

        player = self.get_next_player()
        if player is not None:
            # ここにプレイヤーにアクションしてもらうロジック
            # 例:
            # player.act()
            player.has_acted = True
            self.action_index += 1
    
    def is_round_complete(self) -> bool:
        """現在のラウンドが完了しているかを確認。"""
        return all(seat.player.has_acted for seat in self.action_order)