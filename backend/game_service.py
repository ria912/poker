from models import Deck, Player, Table, Enum
from backend.models.enum import Action
from backend.services.dealer import Dealer
from backend.services.action_manager import ActionManager
from backend.schemas.game_schema import (
    StartGameRequest,
    PlayerActionRequest,
    GameStateResponse,
    PlayerSchema,
    TableSchema,
    ActionHistorySchema,
    LegalActionSchema,
)

from typing import Optional, List
from treys import Card


class GameService:
    def __init__(self):
        self.table: Optional[Table] = None
        self.dealer: Optional[Dealer] = None
        self.action_history: List[ActionHistorySchema] = []

    def start_new_game(self, req: StartGameRequest) -> GameStateResponse:
        self.table = Table(player_count=req.player_count)
        self.dealer = Dealer(self.table)
        self.dealer.setup_game()
        self.action_history = []
        return self._build_game_state()

    def apply_player_action(self, req: PlayerActionRequest) -> GameStateResponse:
        player_seat = self.table.seats[req.seat_id]
        ActionManager.apply_action(player_seat.player, self.table, req.action, req.amount)

        self.action_history.append(ActionHistorySchema(
            seat_id=req.seat_id,
            action=req.action,
            amount=req.amount,
        ))

        # ラウンド完了チェックと進行
        if self.table.is_round_complete():
            self.dealer.proceed_to_next_round()

        return self._build_game_state()

    def _build_game_state(self) -> GameStateResponse:
        players = []
        for seat in self.table.seats:
            player = seat.player
            hand = [Card.int_to_pretty_str(c) for c in player.hand] if player.hand else None

            players.append(PlayerSchema(
                seat_id=seat.seat_id,
                is_human=player.is_human,
                name=player.name,
                position=player.position,
                stack=player.stack,
                bet_total=player.bet_total,
                hand=hand if self._show_hand(player) else None,
                is_folded=player.is_folded,
                last_action=player.last_action,
            ))

        board = [Card.int_to_pretty_str(c) for c in self.table.board]
        table_info = TableSchema(
            round=self.table.round,
            pot=self.table.pot,
            current_bet=self.table.current_bet,
            board=board,
        )

        current_seat = self.table.get_action_seat()
        legal_actions = None
        if current_seat:
            legal_actions = [
                LegalActionSchema(
                    action=info["action"],
                    min_amount=info.get("min"),
                    max_amount=info.get("max")
                )
                for info in ActionManager.get_legal_actions_info(current_seat.player, self.table)
            ]

        return GameStateResponse(
            players=players,
            table=table_info,
            action_history=self.action_history,
            current_seat_id=current_seat.seat_id if current_seat else None,
            legal_actions=legal_actions,
            is_hand_over=self.table.round.name == "SHOWDOWN"
        )

    def _show_hand(self, player: Player) -> bool:
        return player.is_human or self.table.round.name == "SHOWDOWN"
