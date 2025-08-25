# services/player_service.py
from typing import Optional
from app.models.table import Table
from app.models.enum import PlayerState

class PlayerService:
    def sit_down(self, table: Table, seat_index: int, player_id: str, buy_in: int) -> bool:
        seat = table.get_seat(seat_index)
        if seat is None or not seat.is_empty():
            return False
        seat.player_id = player_id
        seat.stack = buy_in
        seat.state = PlayerState.ACTIVE if buy_in > 0 else PlayerState.OUT
        seat.acted = False
        return True

    def stand_up(self, table: Table, seat_index: int) -> bool:
        seat = table.get_seat(seat_index)
        if seat is None or seat.is_empty():
            return False
        # 残スタックはここでは「現金化」など別レイヤの責務。席からは外す。
        seat.player_id = None
        seat.stack = 0
        seat.bet_total = 0
        seat.hole_cards.clear()
        seat.state = PlayerState.OUT
        seat.acted = True
        return True