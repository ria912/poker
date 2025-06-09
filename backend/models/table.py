# models/table.py
from backend.models.deck import Deck
from backend.models.player import Player
from backend.models.human_player import HumanPlayer
from backend.models.ai_player import AIPlayer
from backend.models.position import PositionManager
from backend.models.enum import Round, Position


class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count=6):

        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind

        self.seats = [None] * seat_count
        self.btn_index = None

        self.deck = Deck()
        self.round = Round.PREFLOP
        self.board = []
        self.pot = 0
        self.current_bet = 0
        
        self.last_raiser = None
        
    def seat_assign_players(self, human_names=["YOU"], ai_count=5):
        players = [HumanPlayer(name=n) for n in human_names]
        players += [AIPlayer(name=f"AI{i+1}") for i in range(ai_count)]
        
        for i, player in enumerate(players[:len(self.seats)]):
            player.seat_number = i
            self.seats[i] = player
    
    @property
    def active_seat_indices(self) -> list[int]:
        return [
            i for i, player in enumerate(self.seats)
            if player and not player.sitting_out
        ]

    def reset_for_new_hand(self):
        self.round = Round.PREFLOP
        self.board = []
        self.pot = 0
        self.current_bet = 0
        self.last_raiser = None
        for p in self.seats:
            if p:
                Player.reset_for_new_hand(p)

    def reset_for_next_round(self):
        self.current_bet = 0
        self.min_bet = self.big_blind
        self.last_raiser = None
        for p in self.seats:
            if p and p.is_active:
                Player.reset_for_next_round(p)

    def start_hand(self):
        self.deck.deck_shuffle()
        # BTNのローテーション・ポジションの割り当て
        self.btn_index = PositionManager.set_btn_index(self)
        PositionManager.assign_positions(self)
        # ブラインドとカードの配布
        self._post_blinds()
        self._deal_cards()

    def _post_blinds(self):
        for p in self.seats:
            if not p:
                continue
            if p.position == Position.SB or Position.BTN_SB:
                blind = min(self.small_blind, p.stack)
                p.stack -= blind
                p.current_bet = blind
                self.pot += blind
            elif p.position == Position.BB:
                blind = min(self.big_blind, p.stack)
                p.stack -= blind
                p.current_bet = blind
                self.current_bet = blind
                self.min_bet = blind
                self.pot += blind

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

    def showdown(self):
        pass # 後で開発

    def to_dict(self, show_all_hands=False):
        return {
            "round": self.round,
            "board": self.board,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "btn_index": self.btn_index,
            "last_raiser": self.last_raiser.name if self.last_raiser else None,
            "seats": [
                p.to_dict(show_hand=(show_all_hands or p.is_human)) if p else None
                for p in self.seats
            ],
        }
