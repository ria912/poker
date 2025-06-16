# models/deck.py
import random

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

    def deal_hands(self, table, seats):
        """各プレイヤーに2枚のカードを配る。"""
        for seat in seats:
            player = seat.player
            if player and not player.sitting_out:
                player.hand = [self.draw(), self.draw()]
    
    def deal_flop(self):
        table.board.extend([self.draw() for _ in range(3)])

    def deal_turn(self):
        table.board.append(self.draw())

    def deal_river(self):
        table.board.append(self.draw())