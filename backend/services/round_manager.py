from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.enum import Round, Status, Position
from services import ActionManager, Dealer
from backend.utils.order_utils import get_circular_order, get_next_index


class RoundLogic:
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
    def __init__(self):
        self.round_logic = RoundLogic()
        self.action_order: List[Seat] = []
        self.action_index = 0
        self.current_seat: Optional[Seat] = None

    def reset(self):
        self.action_order = self.compute_action_order()
        self.action_index = 0

    def compute_action_order(self, table: Table, last_raiser: Optional[Seat] = None) -> List[Seat]:
        seats = table.seats
        active_seats = table.get_active_seats()
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

        if table.round == Round.PREFLOP:
            bb_index = table.get_index_by_position(Position.BB)
            start_index = self.find_next_active_index(bb_index)
        else:
            start_index = self.find_next_active_index(table.btn_index)

        return get_circular_order(
            seats,
            start_index=start_index,
            condition=lambda s: s in active_seats
        )

    def find_next_active_index(self, table: Table, start_index: int) -> int:
        return get_next_index(
            table.seats,
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