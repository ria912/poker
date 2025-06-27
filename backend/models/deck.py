# models/deck.py
import random
from backend.models.enum import Round

class Deck:

    SUITS = ['S', 'H', 'D', 'C']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    def __init__(self):
        self.cards = [r + s for s in self.SUITS for r in self.RANKS]
        random.shuffle(self.cards)

    def reset(self):
        self.cards = [r + s for s in self.SUITS for r in self.RANKS]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    def deal_hands(self, table):
        """各プレイヤーに2枚のカードを配る。"""
        for seat in table.seats:
            player = seat.player
            if player and not player.sitting_out:
                player.hand = [self.draw(), self.draw()]
    
    def deal_board(self, table):
        round = table.round
        if round == Round.PREFROP:
            table.board.extend([self.draw() for _ in range(3)])
        elif round == "turn":
            table.board.append(self.draw())
        elif round == "river":
            table.board.append(self.draw())
        else:
            raise ValueError(f"未定義のステージです: {round}")
