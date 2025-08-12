# backend/services/round_manager.py
from typing import List, Optional
from backend.models.table import Table, Seat
from backend.models.player import Player
from backend.models.enum import Round, Status, Position, Action
from backend.services.game.action_manager import ActionManager
from backend.services.game.dealer import Dealer  # Dealerをインポート
from backend.utils.order_utils import get_circular_order

class RoundLogic:
    """
    ラウンド間の進行ロジックを責務とする静的クラス。
    RoundManagerから呼び出される。
    """
    @staticmethod
    def advance_to_next_round(table: Table) -> Status:
        """
        現在のラウンドを終了し、次のラウンドに進める。

        Args:
            table (Table): ゲームテーブル。

        Returns:
            Status: 次のラウンドに進んだ結果の状態。
        """
        # 1人しか残っていない場合、そのラウンド（＝ハンド）は終了
        if len(table.get_active_players()) <= 1:
            return Status.GAME_OVER

        table.round = table.round.next()

        if table.round == Round.SHOWDOWN:
            return Status.GAME_OVER

        # 次のラウンドのためにテーブルの状態をリセット
        table.reset_round_state()
        Dealer.deal_community_cards(table) # Dealerにコミュニティカードを配らせる
        return Status.ROUND_OVER # 次のラウンドが開始されることを示す


class RoundManager:
    """
    1つのベッティングラウンド内のアクション進行を管理するクラス。
    """
    def __init__(self, table: Table):
        self.table = table
        self.action_order: List[Seat] = []
        self.action_index: int = 0

    def start_round(self) -> Optional[Seat]:
        """
        新しいベッティングラウンドを開始する。
        アクション順序を計算し、最初に行動するプレイヤーを返す。

        Returns:
            Optional[Seat]: 最初に行動するプレイヤーのシート。
        """
        self.action_order = self._compute_action_order()
        self.action_index = 0
        return self.get_current_seat()

    def handle_action(self, seat: Seat, action: Action, amount: int = 0) -> Status:
        """
        プレイヤーのアクションを処理し、ゲームの次の状態を返す。

        Args:
            seat (Seat): アクションを実行したプレイヤーのシート。
            action (Action): 実行されたアクション。
            amount (int): ベット/レイズ額。

        Returns:
            Status: アクション処理後のゲーム状態。
        """
        if seat != self.get_current_seat():
            raise ValueError("不正なプレイヤーのアクションです。")

        # 1. アクションをテーブルに適用
        ActionManager.apply_action(seat.player, self.table, action, amount)

        # 2. レイズが発生した場合、アクション順序を再計算
        if action in [Action.BET, Action.RAISE]:
            # レイズしたプレイヤーを基準に、新しいアクション順序を作成
            self.action_order = self._compute_action_order(last_raiser_seat=seat)
            self.action_index = 0 # インデックスをリセット
        else:
            # CALL, CHECK, FOLDの場合は、次のプレイヤーへ
            self.action_index += 1

        # 3. ラウンドの賭けが完了したかチェック
        if self._is_betting_complete():
            # 完了した場合、次のラウンドへ進む
            return RoundLogic.advance_to_next_round(self.table)
        else:
            # 継続する場合
            return Status.ROUND_CONTINUE

    def get_current_seat(self) -> Optional[Seat]:
        """現在アクションすべきプレイヤーのシートを返す。"""
        if self.action_index < len(self.action_order):
            return self.action_order[self.action_index]
        return None

    def _is_betting_complete(self) -> bool:
        """このラウンドの全ての賭けが完了したか（全員が行動を終えたか）を判定する。"""
        return self.action_index >= len(self.action_order)

    def _compute_action_order(self, last_raiser_seat: Optional[Seat] = None) -> List[Seat]:
        """
        状況に応じてアクション順序のリストを作成する。
        - 通常時: ラウンドの開始ポジションから順。
        - レイズ発生時: レイズしたプレイヤーの次から、レイズした本人を除く全員。
        """
        active_seats = self.table.get_active_seats()

        if len(active_seats) < 2 and not last_raiser_seat:
             return active_seats

        # レイズが発生した場合のアクション順序
        if last_raiser_seat:
            # レイズした人の次の人から、レイズした人以外の全員が時計回りに行動
            order = get_circular_order(
                self.table.seats,
                start_index=last_raiser_seat.index,
                condition=lambda s: s in active_seats and s != last_raiser_seat
            )
            return order

        # 通常のラウンド開始時のアクション順序
        if self.table.round == Round.PREFLOP:
            # プリフロップはBBの左隣(UTG)から
            start_pos = self.table.get_index_by_position(Position.BB)
        else:
            # ポストフロップはBTNの左隣(SB)から
            start_pos = self.table.btn_index

        # 開始ポジションの次のアクティブプレイヤーを探す
        start_seat_index = get_circular_order(self.table.seats, start_pos, lambda s: s in active_seats)[0].index

        # そのプレイヤーから始まるアクティブプレイヤー全員のリストを返す
        return get_circular_order(self.table.seats, start_seat_index, lambda s: s in active_seats)