# backend/models/table.py
from typing import List, Optional
from backend.models.deck import Deck
from backend.models.player import Player
from backend.models.enum import Round, Position, State

class Seat:
    def __init__(self, index: int):
        self.index: int = index
        self.player: Optional[Player] = None

    def is_occupied(self) -> bool:
        return self.player is not None

    def is_active(self) -> bool:
        return self.player is not None and self.player.is_active

    def sit(self, player: Player):
        self.player = player

    def stand(self):
        self.player = None


class Table:
    def __init__(self, max_seats: int = 6, small_blind: int = 50, big_blind: int = 100):
        self.max_seats = max_seats
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.deck: Deck = Deck()
        self.seats: List[Seat] = [Seat(i) for i in range(max_seats)]

        self.current_round: Optional[Round] = None
        self.community_cards: List[int] = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = 0

        self.btn_index: Optional[int] = None
        
    def get_active_seats(self) -> List[Seat]:
        return [seat for seat in self.seats if seat.is_active()]
    
    def get_active_seat_indices(self) -> List[int]:
        return [seat.index for seat in self.get_active_seats()]
    
    def get_index_by_position(self, position: Position) -> Optional[int]:
        for seat in self.seats:
            if seat.player and seat.player.position == position:
                return seat.index
        return None

    def add_to_pot(self, amount: int):
        self.pot += amount

    def reset_round(self):
        self.current_bet = 0
        self.min_bet = 0
        for seat in self.seats:
            if seat.is_occupied():
                player = seat.player
                player.bet_total = 0
                player.last_action = None

    def reset_hand(self):
        self.board = []
        self.round = None
        self.pot = 0
        self.current_bet = 0
        self.min_bet = 0
        for seat in self.seats:
            if seat.is_occupied():
                seat.player.reset_for_new_hand()
