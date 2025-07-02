# models/table.py
from backend.models.deck import Deck
from backend.models.player import Player
from backend.models.human_player import HumanPlayer
from backend.models.ai_player import AIPlayer
from backend.models.position import PositionManager
from backend.models.enum import Round, Position
from typing import List, Optional # None の可能性を型で明示

class Seat:
    def __init__(self, index: int):
        self.index: int = index # 座席数0~5
        self.player: Optional[Player] = None # プレイヤー or 空席
    
    def reset_player(self, hand_over: bool = False):
        if self.player:
            self.player.reset(hand_over=hand_over)
    
    def to_dict(self, show_hand: bool = False):
        return {
            "index": self.index,
            "player": self.player.base_dict(show_hand=show_hand) if self.player else None
        }
   
class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count: int = 6):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind
        # Seat 0~5 までの席を定義
        self.seats: List[Seat] = [Seat(i) for i in range(seat_count)]
        self.btn_index: Optional[int] = None # ボタンの座席インデックス

        self.deck = Deck()
        self.round = Round.PREFLOP
        self.board = []
        self.pot = 0
        self.current_bet = 0
        
        self.last_raiser = None
        self.action_log = []
        
    def assign_players_to_seats(self, human_included=True):
        # seat[0] に HumanPlayer、それ以降に AIPlayer を順に割り当てる。
        if human_included:
            self.seats[0].player = HumanPlayer(name="You")
            ai_start = 1
        else:
            ai_start = 0

        for i in range(ai_start, len(self.seats)):
            self.seats[i].player = AIPlayer(name=f"AI_{i}")

    def get_active_seats(self) -> List[Seat]:
        return [seat for seat in self.seats if seat.player and seat.player.is_active]

    def get_active_seat_indices(self) -> list[int]:
        return [i for i, seat in enumerate(self.seats) if seat.player and seat.player.is_active]

    def is_round_complete(self) -> bool:
        active_seats = self.get_active_seats()
        current_bet = self.current_bet

        for seat in active_seats:
            player = seat.player
            if player is None:
                continue
            if player.bet_total != current_bet:
                return False
        return True

    def reset(self):
        if self.round == Round.SHOWDOWN:
            self.round = Round.PREFLOP
            self.board = []
            self.pot = 0
            for seat in self.seats:
                seat.reset_player(hand_over=True)
        else:
            for seat in self.seats:
                seat.reset_player()

        self.current_bet = 0
        self.last_raiser = None
        self.min_bet = self.big_blind

    def starting_new_hand(self):
        self.deck.reset()
        # BTNのローテーション・ポジションの割り当て
        PositionManager.set_btn_index(self)
        PositionManager.assign_positions(self)
        # ブラインドとカードの配布
        self._post_blinds()
        self.deck.deal_hands(self.seats)
 
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
        raise NotImplementedError

    def to_dict(self):
        return {
            "round": self.round,
            "board": self.board,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "last_raiser": self.last_raiser if self.last_raiser else None,
            "seats": [
            seat.to_dict(
                show_hand=seat.player.is_human or self.round == Round.SHOWDOWN
            )
            for seat in self.seats
        ]
    }