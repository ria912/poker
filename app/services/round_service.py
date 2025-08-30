# app/services/round_service.py
from ..models.game_state import GameState
from ..models.enum import Round, SeatStatus

class RoundService:
    """ベッティングラウンドの進行を管理するクラス"""

    def start_new_round(self, game_state: GameState):
        """新しいベッティングラウンド（フロップ、ターン、リバー）を開始します"""
        # 前のラウンドのベットをポットに集める
        game_state.table.collect_bets()

        # ラウンド進行
        if game_state.current_round == Round.FLOP:
            self._deal_flop(game_state)
        elif game_state.current_round in [Round.TURN, Round.RIVER]:
            self._deal_turn_or_river(game_state)
        
        # アクション関連の状態をリセット
        game_state.amount_to_call = 0
        game_state.min_raise_amount = game_state.big_blind
        game_state.last_raiser_seat_index = None
        for seat in game_state.table.seats:
            if seat.is_occupied and seat.status != SeatStatus.FOLDED:
                seat.acted = False

        # アクション開始プレイヤーを設定 (ディーラーボタンの左隣から)
        game_state.current_seat_index = self._find_first_player_to_act(game_state)
    
    def _deal_flop(self, game_state: GameState):
        game_state.table.deck.draw(1)  # バーンカード
        flop_cards = game_state.table.deck.draw(3)
        game_state.table.community_cards.extend(flop_cards)

    def _deal_turn_or_river(self, game_state: GameState):
        game_state.table.deck.draw(1)  # バーンカード
        card = game_state.table.deck.draw(1)
        game_state.table.community_cards.extend(card)

    def is_round_over(self, game_state: GameState) -> bool:
        """現在のベッティングラウンドが終了したかどうかを判定します"""
        active_seats = [s for s in game_state.table.seats if s.status == SeatStatus.ACTIVE]
        
        # アクション可能なプレイヤーが1人以下なら終了
        if len(active_seats) <= 1:
            return True

        # アクションすべきプレイヤーがいない場合（全員がアクション済み）
        if game_state.current_seat_index is None:
            return True
            
        # 全員がアクションを完了したかチェック
        highest_bet = game_state.amount_to_call
        all_players_acted = True
        for seat in active_seats:
            if not seat.acted or seat.current_bet != highest_bet:
                all_players_acted = False
                break
        
        if all_players_acted:
            # プリフロップでレイズがなく、BBがチェックした場合も考慮
            is_preflop_bb_option_closed = (
                game_state.current_round == Round.PREFLOP and
                highest_bet == game_state.big_blind and
                game_state.last_raiser_seat_index is None
            )
            if not is_preflop_bb_option_closed:
                 return True

        return False

    def _find_first_player_to_act(self, game_state: GameState) -> int:
        """そのラウンドで最初にアクションするプレイヤーを見つけます"""
        num_seats = len(game_state.table.seats)
        start_index = (game_state.dealer_seat_index + 1) % num_seats
        
        for i in range(num_seats):
            current_index = (start_index + i) % num_seats
            seat = game_state.table.seats[current_index]
            if seat.is_active:
                return current_index
        
        raise RuntimeError("No active player found to start the round.")