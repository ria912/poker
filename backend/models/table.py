# models/table.py
from models.deck import Deck
from models.position import rotate_button, assign_positions
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer
from models.position import set_btn_index, assign_positions
from models.utils import get_active_players


class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count=6):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind

        self.seats = [None] * seat_count
        self.btn_index = None

        self.deck = Deck()
        self.round = 'preflop'  # 表示用に .title() で整形
        self.board = []
        self.pot = 0
        self.current_bet = 0
        
        self.action_log = []  # アクションログ
        self.last_raiser = None  # 最後にベットしたプレイヤー
        
        self.is_hand_in_progress = False  # フロントでの状態判定に利用

    def seat_assign_players(self):
        players = [HumanPlayer(name="YOU")]
        for i in range(1, len(self.seats)):
            players.append(AIPlayer(name=f"AI{i}"))

        for i, p in enumerate(players):
            p.seat_number = i + 1
            self.seats[i] = p

    def reset_for_new_hand(self):
        self.round = 'preflop'
        self.board = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = self.big_blind
        self.last_raiser = None
        self._reset_players()

    def start_hand(self):
        self.deck.deck_shuffle()
        # BTNのローテーション
        self.btn_index = set_btn_index(self.btn_index)
        active_players = get_active_players(self.seats)
        assign_positions(self, active_players)
        # ブラインドとカードの配布
        self._post_blinds()
        self._deal_cards()
        self.is_hand_in_progress = True

    def _reset_players(self):
        for player in self.seats:
            if player:
                player.reset_for_new_hand()

    def _post_blinds(self):
        for player in self.seats:
            if not player:
                continue
            if player.position == 'SB':
                blind = min(self.small_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.pot += blind
            elif player.position == 'BB':
                blind = min(self.big_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.current_bet = blind
                self.min_bet = blind
                self.pot += blind

    def _deal_cards(self):
        for player in self.seats:
            if player and not player.has_left:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def deal_flop(self):
        self.board.extend([self.deck.draw() for _ in range(3)])

    def deal_turn(self):
        self.board.append(self.deck.draw())

    def deal_river(self):
        self.board.append(self.deck.draw())

    def to_dict(self, show_all_hands=False):
        return {
            "round": self.round.title(),
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
            "active_players": [
                p.to_dict(show_hand=(show_all_hands or p.is_human))
                for p in self.get_active_players()
            ],
            "is_hand_in_progress": self.is_hand_in_progress
        }
