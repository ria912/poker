# services/winner_service.py
from typing import List, Tuple
from gemini_app.models.table import Table, Seat
from gemini_app.models.enum import PlayerState
# from treys import Evaluator  # 接続時に使用
# evaluator = Evaluator()

class WinnerService:
    def _alive_showdown_seats(self, table: Table) -> List[Seat]:
        return [s for s in table.seats if s.player_id and s.state == PlayerState.ACTIVE]

    def _hand_strength(self, seat: Seat, board) -> int:
        """小さいほど強いスコアを返す想定（treys互換）。
        実装はプロジェクトの Card 型に合わせて後で接続してください。"""
        # 例:
        # return evaluator.evaluate(board_to_treys(board), hand_to_treys(seat.hole_cards))
        return 999999  # 仮

    def decide_winners(self, table: Table) -> List[Tuple[int, int]]:
        """(seat_index, prize) のリストを返す（サイドポット未対応の最小版）。"""
        contenders = self._alive_showdown_seats(table)
        if not contenders:
            return []

        # 最強スコアを探す
        strengths = [(s.index, self._hand_strength(s, table.board)) for s in contenders]
        best = min(x[1] for x in strengths)
        winners = [idx for idx, sc in strengths if sc == best]

        # 単純に等分配（端数は最初の勝者に乗せる）
        pot = table.pot
        share = pot // len(winners)
        remainder = pot % len(winners)
        payouts: List[Tuple[int, int]] = []
        for i, idx in enumerate(winners):
            amount = share + (1 if i < remainder else 0)
            payouts.append((idx, amount))
        return payouts