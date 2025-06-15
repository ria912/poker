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

class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count: int = 6):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind
        # Seat 0~5 までの座席を用意
        self.seats: List[Seat] = [Seat(i) for i in range(seat_count)]
        self.btn_index: Optional[int] = None
        
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
    
    def get_active_players(self): List[Seat.player]
        return [
            seat.player for seat in self.seats
            if seat.player and seat.player.is_active
        ]

    @property
    def active_seat_indices(self) -> List[int]:
        return [
            index for index, seat in enumerate(self.seats)
            if seat.player and not seat.player.sitting_out
        ]

    def reset(self):
        # 共通してリセットする情報
        self.current_bet = 0
        self.last_raiser = None
        self.min_bet = self.big_blind
    
        if self.round == Round.SHOWDOWN:
            self.round = Round.PREFLOP
            self.board = []
            self.pot = 0
    
        for seat in self.seats:
            player = seat.player
            if not player:
                continue
            if self.round == Round.SHOWDOWN:
                player.reset(hand_over=True)
            else:
                player.reset()

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

    def _seat_to_dict(self, seat: Seat):
        show_hand = False
        if not seat.player:
            return {"index": seat.index, "player": None}
       
        if seat.player.is_human or self.round == Round.SHOWDOWN:
            show_hand = True
        
        return seat.player.base_dict(show_hand)

    def to_dict(self):
        return {
            "round": self.round,
            "board": self.board,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "btn_index": self.btn_index,
            "last_raiser": self.last_raiser if self.last_raiser else None,
            "seats": [self._seat_to_dict(seat) for seat in self.seats]
        }
