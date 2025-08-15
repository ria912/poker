# app/services/player_service.py
from typing import Optional
from ..models.player import Player, PlayerState
from ..models.game_state import GameState

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
    # ------------------------
    # アクション処理
    # ------------------------
    @staticmethod
    def fold(player: Player):
        """フォールド"""
        player.state = PlayerState.FOLDED

    @staticmethod
    def check(player: Player, current_bet: int):
        """チェック（現在の最大ベットと同額の場合）"""
        if player.bet_total != current_bet:
            raise ValueError("チェックできません。コールが必要です。")
        # 状態はACTIVEのまま

    @staticmethod
    def call(player: Player, table: Table):
        """コール（現在の最大ベットに合わせる）"""
        current_bet = max(seat.player.bet_total for seat in table.seats if seat.is_occupied)
        to_call = current_bet - player.bet_total
        if to_call > player.stack:
            to_call = player.stack  # オールイン
            player.state = PlayerState.ALL_IN
        player.stack -= to_call
        player.bet_total += to_call
        TableService.add_to_pot(table, to_call)

    @staticmethod
    def bet(player: Player, table: Table, amount: int):
        """ベット（初めての賭け）"""
        if amount > player.stack:
            amount = player.stack
            player.state = PlayerState.ALL_IN
        player.stack -= amount
        player.current_bet += amount
        TableService.add_to_pot(table, amount)

    @staticmethod
    def raise_bet(player: Player, table: Table, amount: int, current_bet: int):
        """レイズ（既存のベットより増額）"""
        to_call = current_bet - player.current_bet
        total_amount = to_call + amount
        if total_amount > player.stack:
            total_amount = player.stack
            player.state = PlayerState.ALL_IN
        player.stack -= total_amount
        player.current_bet += total_amount
        TableService.add_to_pot(table, total_amount)
