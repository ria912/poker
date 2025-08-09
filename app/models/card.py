from treys import Card as TreysCard

class Card:
    """トランプのカードを表すクラス。"""
    def __init__(self, rank: str, suit: str):
        '''
        rank: 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'
        suit: 's', 'h', 'd', 'c'
        '''
        self.rank = rank.upper()
        self.suit = suit.lower()
        self._treys_card = TreysCard.new(f"{self.rank}{self.suit}")

    @property
    def treys(self):
        return self._treys_card

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    @classmethod
    def from_treys(cls, treys_card_int: int):
        s = TreysCard.int_to_str(treys_card_int)
        return cls(s[0], s[1])