# services/table_service.py
from typing import Callable, List, Optional
from gemini_app.models.table import Table, Seat
from gemini_app.models.enum import PlayerState

class TableService:
    # -------- 基本クエリ --------
    def active_seat_indices(self, table: Table) -> List[int]:
        return [s.index for s in table.seats
                if s.player_id is not None and s.state != PlayerState.OUT and s.state != PlayerState.FOLDED]

    def next_seat_index(self, table: Table, from_index: int,
                        pred: Optional[Callable[[Seat], bool]] = None) -> Optional[int]:
        """円環で次の seat.index を返す。predがあれば条件でフィルタ。"""
        if not table.seats:
            return None
        n = len(table.seats)
        for step in range(1, n + 1):
            idx = (from_index + step) % n
            seat = table.get_seat(idx)
            if seat is None:
                continue
            if pred is None or pred(seat):
                return idx
        return None

    def recompute_pot(self, table: Table) -> int:
        table.pot = sum(s.bet_total for s in table.seats if s.player_id and s.state != PlayerState.OUT)
        return table.pot

    # -------- ブラインド --------
    def assign_blinds_preflop(self, table: Table, dealer_index: int) -> tuple[Optional[int], Optional[int]]:
        """SB/BBの seat.index を返す（アクティブ席の中から）"""
        def is_active(seat: Seat) -> bool:
            return seat.player_id is not None and seat.state == PlayerState.ACTIVE

        sb_index = self.next_seat_index(table, dealer_index, pred=is_active)
        bb_index = self.next_seat_index(table, sb_index if sb_index is not None else dealer_index, pred=is_active) \
                   if sb_index is not None else None
        return sb_index, bb_index

    def post_blinds(self, table: Table, game_state, dealer_index: int) -> tuple[Optional[int], Optional[int]]:
        """SB/BB を自動ポスト。スタックが足りなければオールイン扱い。"""
        sb_index, bb_index = self.assign_blinds_preflop(table, dealer_index)
        for name, idx, blind in (("SB", sb_index, game_state.small_blind),
                                 ("BB", bb_index, game_state.big_blind)):
            if idx is None:
                continue
            seat = table.get_seat(idx)
            if seat is None or seat.state != PlayerState.ACTIVE:
                continue
            pay = min(seat.stack, blind)
            seat.stack -= pay
            seat.bet_total += pay
            # ラウンド別の投入額に反映
            game_state.round_bets[idx] = game_state.round_bets.get(idx, 0) + pay

        # プリフロップの現在ベットと最小レイズを設定
        game_state.current_bet = max(game_state.round_bets.values()) if game_state.round_bets else 0
        game_state.min_raise = game_state.big_blind
        self.recompute_pot(table)
        return sb_index, bb_index