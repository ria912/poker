from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.enum import Round, Status, Position
from services import ActionManager, Dealer
from backend.utils.order_utils import get_circular_order, get_next_index


class RoundLogic:
    @staticmethod
    def advance_round(table: Table) -> Status:
        if len(table.get_active_seats()) == 1:
            return Status.ROUND_OVER

        table.round = Round.next(table.round)

        if table.round == Round.SHOWDOWN:
            return Status.ROUND_OVER

        table.reset_round()
        Dealer.deal_community_cards(table)
        return Status.ROUND_CONTINUE


class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_order: List[Seat] = []
        self.action_index = 0
        self.current_seat: Optional[Seat] = None

    def reset(self):
        self.action_order = self.compute_action_order()
        self.action_index = 0
        self.current_seat = None

    def compute_action_order(self, last_raiser: Optional[Seat] = None) -> List[Seat]:
        seats = self.table.seats
        active_seats = self.table.get_active_seats()

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
            bb_index = self.table.get_index_by_position(Position.BB)
            start_index = self.find_next_active_index(bb_index)
        else:
            start_index = self.find_next_active_index(self.table.btn_index)

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
            if seat.player and seat.player.is_active:
                self.current_seat = seat
                return seat
            self.action_index += 1
        return None

    def proceed(self) -> Status:
        seat = self.get_current_seat()

        if seat:
            self._process_action(seat)
            self.action_index += 1
            return Status.PLAYER_ACTED

        elif self.table.is_round_complete():
            return RoundLogic.advance_round(self.table)

        else:
            self.reset()
            return Status.ROUND_CONTINUE

    def _process_action(self, seat: Seat, action: str, amount: int):
        ActionManager.apply_action(seat.player, self.table, action, amount)
