# models/dealer.py

def _deal_cards(self):
        for p in self.seats:
            if p and not p.sitting_out:
                p.hand = [self.deck.draw(), self.deck.draw()]

def deal_flop(self):
        self.board.extend([self.deck.draw() for _ in range(3)])

def deal_turn(self):
        self.board.append(self.deck.draw())

def deal_river(self):
        self.board.append(self.deck.draw())