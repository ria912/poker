# services/game_service.py
from typing import Optional
from gemini_app.models.table import Table
from gemini_app.models.enum import Action, State, PlayerState
from gemini_app.models.game_state import GameState
from gemini_app.models.deck import Deck
from .table_service import TableService
from .round_service import RoundService
from .action_service import ActionService

class GameService:
    def __init__(self):
        self._table = TableService()
        self._round = RoundService()
        self._action = ActionService()
        self._deck: Optional[Deck] = None

    def start_hand(self, table: Table, gs: GameState, dealer_index: Optional[int] = None) -> None:
        self._deck = Deck(shuffle=True)
        self._round.start_new_hand(table, gs, self._deck, dealer_index)

    def legal_actions(self, table: Table, gs: GameState) -> list[Action]:
        if gs.current_turn is None:
            return []
        return self._action.get_legal_actions(table, gs, gs.current_turn)

    def act(self, table: Table, gs: GameState, action: Action, amount: Optional[int] = None) -> None:
        """現在のプレイヤーのアクションを適用し、必要ならラウンド遷移します。"""
        if gs.current_turn is None or gs.state != State.IN_PROGRESS:
            return
        actor = gs.current_turn

        # 実行
        self._action.apply(table, gs, actor, action, amount)

        # 生存者が1人なら即終了（フォールド勝ち）
        alive = [s for s in table.seats if s.player_id and s.state == PlayerState.ACTIVE]
        if len(alive) <= 1:
            gs.state = State.SHOWDOWN
            gs.current_turn = None
            return

        # ラウンド終了なら次ストリートへ
        if self._action.is_betting_round_complete(table, gs):
            self._round.deal_next_street(table, gs)
            if gs.state == State.SHOWDOWN:
                gs.current_turn = None
                return

        # 次のアクター
        nxt = self._action.next_to_act(table, gs, from_index=actor)
        gs.current_turn = nxt