# models/table.py
from models.deck import Deck
from models.position import rotate_button, assign_positions
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer

class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count=6):
        self.seats = [None] * seat_count  # プレイヤーの座席
        self.seat_assign_players()
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = big_blind
        self.big_blind = big_blind
        self.small_blind = small_blind

    #プレイヤーを座席に割り当てる
    def seat_assign_players(self):
         # 人間プレイヤーを追加
        players = [HumanPlayer(name="YOU")]
        # AIプレイヤーを追加
        for i in range(1, len(self.seats)):
            players.append(AIPlayer(name=f"AI{i}"))
        # プレイヤーを座席に割り当てる
        for i, p in enumerate(players):
            self.seats[i] = p


    def start_hand(self):
        self.deck.deck_shuffle()
        self.reset_players()
        rotate_button(self.seats)
        assign_positions(self.seats)
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.post_blinds()
        self.deal_cards()

    def reset_players(self):
        for player in self.seats:
            if player:
                player.reset_for_new_hand()

    def post_blinds(self):
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

    def deal_cards(self):
        for player in self.seats:
            if player and not player.has_left:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def get_human_player(self):
        for player in self.seats:
            if player and player.name == "YOU":
                return player
        raise ValueError("Human player not found")


    def to_dict(self):
        return {
            "community_cards": self.community_cards,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "players": [p.to_dict() if p else None for p in self.seats]
        }
