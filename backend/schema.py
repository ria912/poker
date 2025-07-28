# backend/schemas/game_schemas.py

from backend.models.enum import Round
from backend.models.table import Table
from backend.models.player import Player
from backend.models.seat import Seat
from backend.services.action_manager import ActionManager


def format_card(card_int):
    """例: 12 => 'As'（エース・スペード）"""
    from treys import Card
    return Card.int_to_pretty_str(card_int)


def player_to_dict(seat: Seat, show_hand=False) -> dict:
    player: Player = seat.player
    return {
        "seat": seat.index,
        "position": player.position.name if player.position else None,
        "name": player.name,
        "stack": player.stack,
        "bet_total": player.bet_total,
        "hand": [format_card(c) for c in player.hand] if show_hand else ["?", "?"],
        "is_allin": player.stack == 0,
        "last_action": player.last_action.name if player.last_action else None,
    }


def table_to_dict(table: Table, show_all_hands=False) -> dict:
    return {
        "round": table.round.name,
        "pot": table.pot,
        "current_bet": table.current_bet,
        "board": [format_card(c) for c in table.board],
        "players": [
            player_to_dict(seat, show_hand=(show_all_hands or seat.player.stack == 0))
            for seat in table.seats
        ],
    }


def action_info_to_dict(player: Player, table: Table) -> dict:
    action_info = ActionManager.get_legal_actions_info(player, table)
    return {
        "player": player.name,
        "legal_actions": [
            {
                "action": action.name,
                "min": info.get("min"),
                "max": info.get("max")
            }
            for action, info in action_info.items()
        ]
    }