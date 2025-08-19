from app.models.player import Player
from app.models.enum import PlayerState


class PlayerService:
    """プレイヤーのアクションやスタック操作を担当"""

    @staticmethod
    def pay(player: Player, amount: int) -> int:
        """
        プレイヤーがスタックから支払い、指定額を返す
        （呼び出し元でポット加算などを行う）
        """
        if amount > player.stack:
            raise ValueError(f"{player.name} のスタック不足")
        player.stack -= amount
        return amount

    @staticmethod
    def fold(player: Player) -> None:
        """プレイヤーをフォールド状態にする"""
        player.state = PlayerState.FOLDED

    @staticmethod
    def all_in(player: Player) -> int:
        """プレイヤーをオールインさせる"""
        amount = player.stack
        player.stack = 0
        player.state = PlayerState.ALL_IN
        return amount
