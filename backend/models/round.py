# backend/models/round.py
from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.enum import Round, Status
from backend.models.action import ActionManager, Action


class RoundLogic:
    """ラウンドの状態管理も行います。"""

    def __init__(self, table: Table):
        self.table = table

    def advance_round(self):
        if len(self.table.get_active_seats) == 1:
            return Status.ROUND_OVER

        next_round = Round.next(self.table.round)
        self.table.round = next_round

        if self.table.round == Round.SHOWDOWN:
            return Status.ROUND_OVER

        else:
            self.table.reset()
            self.table.deck.deal_board(self.table)
            return Status.ROUND_CONTINUE


class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.round_logic = RoundLogic(table)
        self.status: Optional[Status] = Status.ROUND_CONTINUE

        self.action_order: List[Seat] = []
        self.action_index = 0
        self.current_seat: Optional[Seat] = None
    
    def reset(self):
        self.action_order = self.compute_action_order()
        self.action_index = 0

    def compute_action_order(self) -> List[Seat]:
        seats = self.table.seats
        active_seats: list[Seat] = self.table.get_active_seats()
        round = self.table.round
        btn_index = self.table.btn_index

        if len(active_seats) < 2:
            raise ValueError("アクティブプレイヤーが2人未満ではゲームを進行できません")
        # アクション開始基準インデックスを決める
        if round == Round.PREFLOP:
            # 少人数対応は後で（4人以下でエラー？）
            base_index = (btn_index + 3) % len(seats)
        else:
            base_index = (btn_index + 1) % len(seats)
        # アクション順を作成（active_seatsを base_index から時計回りに並べる）
        ordered = []
        for i in range(len(seats)):
            idx = (base_index + i) % len(seats)
            seat = seats[idx]
            if seat in active_seats:
                ordered.append(seat)

        return ordered

    def get_current_seat(self) -> Optional[Seat]:
        while self.action_index < len(self.action_order):
            seat = self.action_order[self.action_index]
            if seat.player and not seat.player.has_acted:
                return seat
            else:
                self.action_index += 1
        return None

    def proceed(self):
        current = self.get_current_seat()

        if current and current.player:
            self._process_action(current)
            self.action_index += 1

        elif self.table.is_round_complete():
            self.round_logic.advance_round()

        else:
            self.reset() #アクション続行（オーダーリセット）
            return Status.ROUND_CONTINUE

    def _process_action(self, seat: Seat):
        action, amount = seat.player.act(self.table)
        print(f"{seat.player.name} が {action},{amount} を選択。")
        ActionManager.apply_action(seat.player, self.table, action, amount)

        if action in Action.betting_actions():
            self._reset_has_acted(exclude=seat)

    # 以下tableに仮設したis_round_overで簡略可能？
    def _reset_has_acted(self, exclude: Seat = None):
        for seat in self.action_order:
            if seat != exclude and seat.player and seat.player.is_active:
                seat.player.has_acted = False

    def is_round_complete(self) -> bool:
        """アクション順の全プレイヤーがアクション済みかどうかを確認。"""
        for seat in self.action_order:
            if seat.player and seat.player.is_active:
                if seat.player.bet_total != self.table.current_bet:
                    return False
        return True