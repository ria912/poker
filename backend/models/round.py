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
        if len(self.table.get_active_seats()) == 1:
            return Status.ROUND_OVER

        next_round = Round.next(self.table.round)
        self.table.round = next_round

        if self.table.round == Round.SHOWDOWN:
            return Status.ROUND_OVER

        else:
            self.table.reset()
            self.table.deck.deal_board(self.table)
            print(self.table.board)
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
        """ラウンドごとのアクション順を構築。初期 or レイズ後対応。"""
        if last_raiser is None:
            last_raiser = self.table.last_raiser

        seats = self.table.seats
        active_seats = self.table.get_active_seats()
        n = len(seats)

        if len(active_seats) < 2:
            raise ValueError("アクティブプレイヤーが2人未満ではアクション順を構成できません")
    
        # --- レイズ後：last_raiserの次のアクティブ席から開始し、last_raiserを除外 ---
        if last_raiser and last_raiser in active_seats:
            start_index = (last_raiser.index + 1) % n
            ordered = []
            for i in range(n):
                idx = (start_index + i) % n
                seat = seats[idx]
                if seat in active_seats and seat != last_raiser:
                    ordered.append(seat)
            return ordered
    
        # --- 初期巡回：プリフロップか、それ以外かで開始インデックスを変える ---
        if self.table.round == Round.PREFLOP:
            # BBの次のアクティブプレイヤー
            bb_index = (self.table.btn_index + 2) % n
            start_index = (bb_index + 1) % n
        else:
            # BTNの次のアクティブプレイヤー（通常ストリート）
            start_index = (self.table.btn_index + 1) % n
    
        # start_index から時計回りにアクティブプレイヤーを並べる
        ordered = []
        for i in range(n):
            idx = (start_index + i) % n
            seat = seats[idx]
            if seat in active_seats:
                ordered.append(seat)
    
        return ordered

    def find_next_active_index(self, start_index: int) -> int:
        """start_index から時計回りに最初にアクティブなプレイヤーを見つける"""
        seats = self.table.seats
        n = len(seats)
        for i in range(n):
            idx = (start_index + i) % n
            seat = seats[idx]
            if seat.player and seat.player.is_active:
                return idx
        raise RuntimeError("アクティブプレイヤーが存在しません")

    def get_current_seat(self) -> Optional[Seat]:
        while self.action_index < len(self.action_order):
            seat = self.action_order[self.action_index]
            if seat.player:
                self.current_seat = seat
                return seat
            else:
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
            self.reset() #アクション続行（オーダーリセット）
            return Status.ROUND_CONTINUE

    def _process_action(self, seat: Seat):
        action, amount = seat.player.act(self.table)
        print(f"{seat.player.name} が {action},{amount} を選択。")
        ActionManager.apply_action(seat.player, self.table, action, amount)