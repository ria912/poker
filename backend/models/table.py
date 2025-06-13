# models/table.py
from backend.models.deck import Deck
from backend.models.player import Player
from backend.models.human_player import HumanPlayer
from backend.models.ai_player import AIPlayer
from backend.models.position import PositionManager
from backend.models.enum import Round, Position
from typing import Optional # None の可能性があることを型として明示

class Seat:
    def __init__(self, index: int):
        self.index = index  # 座席番号
        self.player: Optional[Player] = None  # 座っているプレイヤー

class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count: int = 6):

        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind

        self.seats: list[Seat] = [Seat(i) for i in range(seat_count)]
        self.btn_index: int | None = None
        
        self.deck = Deck()
        self.round = Round.PREFLOP
        self.board = []
        self.pot = 0
        self.current_bet = 0
        
        self.last_raiser = None
        self.action_log = []
        
    def assign_players_to_seats(self):
        # seat[0] に HumanPlayer、それ以降に AIPlayer を順に割り当てる。
        self.seats[0].player = HumanPlayer(name="Hero")
        
        for i in range(1, len(self.seats)):
            self.seats[i].player = AIPlayer(name=f"AI_{i}")
    
    def get_active_players(self):
        return [
            seat.player for seat in self.seats
            if seat.player and seat.player.is_active
        ]

    @property
    def active_seat_indices(self) -> list[int]:
        return [
            index for index, seat in enumerate(self.seats)
            if seat.player and not seat.player.sitting_out
        ]

    def reset_for_new_hand(self):
        self.round = Round.PREFLOP
        self.board = []
        self.pot = 0
        self.current_bet = 0
        self.last_raiser = None
        for seat in self.seats:
            player = seat.player
            if player:
                player.reset_for_new_hand()

    def reset_for_next_round(self):
        self.current_bet = 0
        self.min_bet = self.big_blind
        self.last_raiser = None
        for seat in self.seats:
            player = seat.player
            if player:
                player.reset_for_next_round()

    def start_hand(self):
        self.deck.deck_shuffle()
        # BTNのローテーション・ポジションの割り当て
        self.btn_index = PositionManager.set_btn_index(self)
        PositionManager.assign_positions(self)
        # ブラインドとカードの配布
        self._post_blinds()
        self.deal_hands()
    
    def deal_hands(self):
        for seat in self.seats:
            player = seat.player
            if player and not player.sitting_out:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def deal_flop(self):
        self.board.extend([self.deck.draw() for _ in range(3)])

    def deal_turn(self):
        self.board.append(self.deck.draw())

    def deal_river(self):
        self.board.append(self.deck.draw())

    def _post_blinds(self):
        for seat in self.seats:
            player = seat.player
            if not player:
                continue
            if player.position in (Position.SB, Position.BTN_SB):
                blind = min(self.small_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                self.pot += blind
            elif player.position == Position.BB:
                blind = min(self.big_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                self.current_bet = blind
                self.min_bet = blind
                self.pot += blind

    def showdown(self):
        pass # 後で開発

    def _seat_to_dict(self, seat: Seat, show_all_hands: bool):
        if not seat.player:
            return None
        return seat.player.base_dict(show_hand=(show_all_hands or seat.player.is_human))

    def to_dict(self, show_all_hands=False):
        return {
            "round": self.round,
            "board": self.board,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "btn_index": self.btn_index,
            "last_raiser": self.last_raiser if self.last_raiser else None,
            "seats": [
            self._seat_to_dict(seat, show_all_hands) for seat in self.seats
            ],
        }
