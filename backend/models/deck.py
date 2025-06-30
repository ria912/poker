import random
from backend.models.enum import Round  # Round を使ってラウンド判定

class Deck:

    SUITS = ['S', 'H', 'D', 'C']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self):
        self.cards = [r + s for s in self.SUITS for r in self.RANKS]
        random.shuffle(self.cards)

    def reset(self):
        """デッキを52枚に戻してシャッフル"""
        self.cards = [r + s for s in self.SUITS for r in self.RANKS]
        random.shuffle(self.cards)

    def draw(self):
        """1枚カードを引く（なければ例外）"""
        if not self.cards:
            raise ValueError("デッキにカードが残っていません。")
        return self.cards.pop()

    def deal_hands(self, seats):
        """各プレイヤーに2枚のカードを配る。"""
        for seat in seats:
            player = seat.player
            if player and not player.sitting_out:
                player.hand = [self.draw(), self.draw()]

    def deal_board(self, table):
        """現在のラウンドに応じてボードにカードを追加"""
        if table.round == Round.FLOP:
            table.board.extend([self.draw() for _ in range(3)])
        elif table.round in (Round.TURN, Round.RIVER):
            table.board.append(self.draw())
        else:
            raise ValueError(f"無効なラウンド: {table.round}")