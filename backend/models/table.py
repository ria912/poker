# models/table.py
from models.deck import Deck
from models.position import rotate_button, assign_positions
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer

class Table:
    def __init__(self, small_blind=50, big_blind=100, seat_count=6):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.min_bet = big_blind

        self.seats = [None] * seat_count
        self.seat_assign_players()

        self.deck = Deck()
        self.round = 'preflop'  # 表示では `.title()` で整形
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0

        self.last_raiser = None  # プレイヤーインスタンス or None
        # 状態管理の補助（将来的な拡張用）
        self.is_hand_in_progress = False  # フロントで判定用

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
        self.is_hand_in_progress = True

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

    def deal_flop(self):
        self.community_cards.extend([self.deck.draw() for _ in range(3)])

    def deal_turn(self):
        self.community_cards.append(self.deck.draw())

    def deal_river(self):
        self.community_cards.append(self.deck.draw())

    def award_pot_to_winner(self):
        active_players = self.get_active_players()
        if not active_players:
            return
        winner = next((p for p in active_players if p.name == "YOU"), active_players[0])
        winner.stack += self.pot
        self.pot = 0

    def get_human_player(self):
        for player in self.seats:
            if player and player.is_human:
                return player
        raise ValueError("Human player not found")
    
    def get_active_players(self):
        return [
            player for player in self.seats
            if player and not player.has_folded and not player.has_all_in and not player.has_left
        ]

    def player_to_dict(self, p, seat_number=None):
        data = {
            "name": p.name,
            "position": p.position,
            "stack": p.stack,
            "current_bet": p.current_bet,
            "last_action": p.last_action,
        }
        if seat_number is not None:
            data["seat_number"] = seat_number
        return data

    def to_dict(self):
        return {
            "round": self.round.title(),  # 'preflop' -> 'Preflop'
            "community_cards": self.community_cards,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "last_raiser": self.last_raiser.name if self.last_raiser else None,
            "seats": [
                self.player_to_dict(p, i + 1) if p else None
                for i, p in enumerate(self.seats)
            ],
            "active_players": [
                self.player_to_dict(p)
                for p in self.get_active_players()
            ],
            "is_hand_in_progress": self.is_hand_in_progress  # フロントで判定用
        }
