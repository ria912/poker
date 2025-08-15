# app/services/player_service.py
from typing import Optional
from ..models.player import Player, PlayerState
from ..models.game_state import GameState

def reset_player(player: Player):
    """プレイヤーの状態をリセット"""
    player.position = None
    player.hand.clear()
    player.bet_total = 0
    player.state = PlayerState.ACTIVE if player.stack > 0 else PlayerState.OUT

def reset_bet_total(player: Player):
    player.bet_total = 0

def add_player(game_state: GameState, name: str, stack: int) -> Optional[Player]:
    """空いている席にプレイヤーを追加"""
    for seat in game_state.table.seats:
        if not seat.is_occupied:
            player = Player(name=name, stack=stack, state=PlayerState.ACTIVE)
            seat.player = player
            return player
    return None

def remove_player(game_state: GameState, player_id: str) -> bool:
    """プレイヤーを削除"""
    for seat in game_state.table.seats:
        if seat.is_occupied and seat.player.player_id == player_id:
            seat.player = None
            return True
    return False