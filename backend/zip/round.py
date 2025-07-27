from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.enum import Round, Status
from backend.services.action import ActionManager, Action
from backend.utils.order_utils import get_circular_order, get_next_index


class RoundLogic:
    def __init__(self, table: Table):
        self.table = table

    def advance_round(self):
        if len(self.table.get_active_seats()) == 1:
            return Status.ROUND_OVER

        self.table.round = Round.next(self.table.round)

        if self.table.round == Round.SHOWDOWN:
            return Status.ROUND_OVER

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

    def compute_action_order(self, last_raiser: Optional[Seat] = None) -> List[Seat]:
        seats = self.table.seats
        active_seats = self.table.get_active_seats()
        n = len(seats)

        if len(active_seats) < 2:
            raise ValueError("アクティブプレイヤーが2人未満です")

        if last_raiser and last_raiser in active_seats:
            return get_circular_order(
                seats,
                start_index=(last_raiser.index + 1),
                condition=lambda s: s in active_seats,
                exclude=last_raiser
            )

        if self.table.round == Round.PREFLOP:
            bb_index = (self.table.btn_index + 2) % n
            start_index = (bb_index + 1) % n
        else:
            start_index = (self.table.btn_index + 1) % n

        return get_circular_order(
            seats,
            start_index=start_index,
            condition=lambda s: s in active_seats
        )

    def find_next_active_index(self, start_index: int) -> int:
        return get_next_index(
            self.table.seats,
            start_index=start_index,
            condition=lambda s: s.player and s.player.is_active
        )

    def get_current_seat(self) -> Optional[Seat]:
        while self.action_index < len(self.action_order):
            seat = self.action_order[self.action_index]
            if seat.player:
                self.current_seat = seat
                return seat
            self.action_index += 1
        return None

    def proceed(self):
        current = self.get_current_seat()

        if current and current.player:
            self._process_action(current)
            self.action_index += 1
            return Status.PLAYER_ACTED

        elif self.table.is_round_complete():
            return self.round_logic.advance_round()

        else:
            self.reset()
            return Status.ROUND_CONTINUE

    def _process_action(self, seat: Seat):
        action, amount = seat.player.act(self.table)
        ActionManager.apply_action(seat.player, self.table, action, amount)