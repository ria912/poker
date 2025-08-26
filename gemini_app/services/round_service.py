# services/round_service.py
from typing import Optional
from gemini_app.models.deck import Deck
from gemini_app.models.table import Table, Seat
from gemini_app.models.enum import Round, State, PlayerState
from gemini_app.models.game_state import GameState
from .table_service import TableService

class RoundService:
    def __init__(self):
        self._table = TableService()

    # -------- ハンド開始 --------
    def start_new_hand(self, table: Table, gs: GameState, deck: Deck, next_dealer_index: Optional[int] = None) -> None:
        table.reset_for_new_hand()
        gs.state = State.IN_PROGRESS
        gs.round = Round.PREFLOP

        # ディーラー決定
        if next_dealer_index is None:
            # 直近のdealer_indexがあればその次、なければ最初のアクティブ
            if gs.dealer_index is None:
                actives = self._table.active_seat_indices(table)
                gs.dealer_index = actives[0] if actives else None
            else:
                gs.dealer_index = self._table.next_seat_index(
                    table, gs.dealer_index,
                    pred=lambda s: s.is_active()
                )
        else:
            gs.dealer_index = next_dealer_index

        # デッキを用意＆ホールカード配布（2枚ずつ）
        deck.shuffle()
        for s in table.seats:
            if s.is_active():
                s.hole_cards = [deck.draw(), deck.draw()]

        # ラウンド用フラグ初期化
        for s in table.seats:
            s.acted = not s.is_active()

        # ラウンド別投入額を初期化してブラインド
        actives = self._table.active_seat_indices(table)
        gs.reset_round_bets(actives)
        sb_index, bb_index = self._table.post_blinds(table, gs, gs.dealer_index if gs.dealer_index is not None else -1)

        # プリフロップの最初に動く人
        # 原則：BBの左（HUはSB=Dealerが先行）
        first = None
        if bb_index is not None:
            first = self._table.next_seat_index(
                table, bb_index,
                pred=lambda s: s.player_id and s.state == PlayerState.ACTIVE and s.stack > 0
            )
        gs.current_turn = first

    # -------- ボード配布（次ストリートへ） --------
    def deal_next_street(self, table: Table, gs: GameState, deck: Deck) -> None:
        if gs.round == Round.PREFLOP:
            table.board.extend([deck.draw(), deck.draw(), deck.draw()])
            gs.round = Round.FLOP
        elif gs.round == Round.FLOP:
            table.board.append(deck.draw())
            gs.round = Round.TURN
        elif gs.round == Round.TURN:
            table.board.append(deck.draw())
            gs.round = Round.RIVER
        else:
            # RIVER 後はショーダウンへ
            gs.state = State.SHOWDOWN
            return

        # 新ストリート初期化
        actives = self._table.active_seat_indices(table)
        gs.reset_round_bets(actives)
        # postflop の最小レイズは通常 BB
        gs.min_raise = gs.big_blind

        # アクションフラグ初期化（オールインは acted=True のまま）
        for s in table.seats:
            if s.player_id and s.state == PlayerState.ACTIVE:
                s.acted = (s.stack == 0)

        # postflop の最初に動く人：ディーラーの左
        if gs.dealer_index is not None:
            gs.current_turn = self._table.next_seat_index(
                table, gs.dealer_index,
                pred=lambda s: s.player_id and s.state == PlayerState.ACTIVE and s.stack > 0
            )
        else:
            gs.current_turn = None