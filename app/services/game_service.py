# app/services/game_service.py
from typing import List, Optional
from ..models.game_state import GameState
from ..models.player import Player
from ..models.enum import Round, GameStatus, SeatStatus
from .round_service import RoundService
from .action_service import ActionService
from .hand_evaluator import HandEvaluator

class GameService:
    """ゲーム全体の進行を管理するクラス"""
    
    def __init__(self, seat_count: int = 6, big_blind: int = 100, small_blind: int = 50):
        self.game_state = GameState(seat_count, big_blind, small_blind)
        self.round_service = RoundService()
        self.action_service = ActionService()
        self.hand_evaluator = HandEvaluator()

    def sit_player(self, player: Player, seat_index: int, stack: int):
        """プレイヤーを着席させます"""
        self.game_state.table.seats[seat_index].sit_down(player, stack)

    def start_hand(self) -> Optional[GameState]:
        """新しいハンドを開始します"""
        seated_players = [s for s in self.game_state.table.seats if s.is_occupied]
        if len(seated_players) < 2:
            print("Not enough players to start a hand.")
            return None

        self.game_state.clear_for_new_hand()
        self.game_state.status = GameStatus.IN_PROGRESS

        self._assign_positions()
        self._post_blinds()
        self._deal_hole_cards()

        # プリフロップのアクション開始プレイヤーを設定 (BBの左隣)
        num_seats = len(self.game_state.table.seats)
        bb_seat = next(s for s in self.game_state.table.seats if s.position == "BB")
        self.game_state.current_seat_index = self._find_next_active_player_index(bb_seat.index)
        
        return self.game_state
        
    def proceed_to_next_stage(self):
        """ラウンド終了後、次のステージ（次のラウンド or ショウダウン）へ進めます"""
        round_order = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]
        
        active_players = [s for s in self.game_state.table.seats if s.status not in [SeatStatus.FOLDED, SeatStatus.OUT]]
        if len(active_players) <= 1:
            self._handle_hand_end_without_showdown(active_players)
            return

        current_round_index = round_order.index(self.game_state.current_round)
        if current_round_index >= len(round_order) - 2: # RIVERの次
             self.game_state.current_round = Round.SHOWDOWN
             self._proceed_to_showdown()
        else:
            next_round = round_order[current_round_index + 1]
            self.game_state.current_round = next_round
            self.round_service.start_new_round(self.game_state)

    def _assign_positions(self):
        """ディーラーボタンとブラインドの位置を決定します"""
        seats = self.game_state.table.seats
        num_seats = len(seats)
        
        start_index = 0 if self.game_state.dealer_seat_index is None else self.game_state.dealer_seat_index + 1
            
        # ディーラーボタン (BTN)
        dealer_index = self._find_next_player_index_for_position(start_index)
        self.game_state.dealer_seat_index = dealer_index
        seats[dealer_index].position = "BTN"

        # スモールブラインド (SB)
        sb_index = self._find_next_player_index_for_position(dealer_index + 1)
        seats[sb_index].position = "SB"

        # ビッグブラインド (BB)
        bb_index = self._find_next_player_index_for_position(sb_index + 1)
        seats[bb_index].position = "BB"

    def _post_blinds(self):
        """SBとBBを強制的にベットさせます"""
        sb_seat = next(s for s in self.game_state.table.seats if s.position == "SB")
        sb_amount = min(self.game_state.small_blind, sb_seat.stack)
        sb_seat.bet(sb_amount)

        bb_seat = next(s for s in self.game_state.table.seats if s.position == "BB")
        bb_amount = min(self.game_state.big_blind, bb_seat.stack)
        bb_seat.bet(bb_amount)

        self.game_state.amount_to_call = self.game_state.big_blind
        self.game_state.min_raise_amount = self.game_state.big_blind * 2
        self.game_state.last_raiser_seat_index = bb_seat.index # BBのポストを最初のレイズとみなす

    def _deal_hole_cards(self):
        """各プレイヤーにホールカードを2枚ずつ配ります"""
        seated_players_in_order = self._get_seated_players_in_action_order("SB")
            
        # 1枚ずつ2周配る
        for _ in range(2):
            for seat in seated_players_in_order:
                 card = self.game_state.table.deck.draw(1)
                 seat.hole_cards.extend(card)

    def _proceed_to_showdown(self):
        """ショウダウン処理を行い、勝者にポットを分配します"""
        self.game_state.table.collect_bets()
        
        showdown_seats = [s for s in self.game_state.table.seats if s.status not in [SeatStatus.FOLDED, SeatStatus.OUT]]
        
        winners_by_pot = self.hand_evaluator.determine_winners(showdown_seats, self.game_state.table.community_cards)
        
        self._distribute_pot(winners_by_pot)
        self.game_state.status = GameStatus.HAND_COMPLETE

    def _handle_hand_end_without_showdown(self, active_seats: List):
        """ショウダウンなしでハンドが終了した場合のポット分配"""
        self.game_state.table.collect_bets()
        if active_seats:
            winner = active_seats[0]
            winner.stack += self.game_state.table.pot
        self.game_state.table.pot = 0
        self.game_state.status = GameStatus.HAND_COMPLETE
        
    def _distribute_pot(self, winners_by_pot: List[List]):
        """ポットを勝者に分配します（現状はメインポットのみ）"""
        if not winners_by_pot: return

        main_pot_winners = winners_by_pot[0]
        if not main_pot_winners: return
        
        win_amount = self.game_state.table.pot // len(main_pot_winners)
        remainder = self.game_state.table.pot % len(main_pot_winners)
        
        for winner_seat in main_pot_winners:
            winner_seat.stack += win_amount
        
        # 端数はSBに近い人から配る
        if remainder > 0:
            winners_in_order = self._get_seated_players_in_action_order("SB", main_pot_winners)
            for i in range(remainder):
                winners_in_order[i].stack += 1
            
        self.game_state.table.pot = 0

    def _find_next_active_player_index(self, start_index: int) -> Optional[int]:
        """指定インデックス以降で最初のアクティブなプレイヤーを探します"""
        seats = self.game_state.table.seats
        for i in range(len(seats)):
            next_index = (start_index + i) % len(seats)
            if seats[next_index].is_active:
                return next_index
        return None
        
    def _find_next_player_index_for_position(self, start_index: int) -> int:
        """指定インデックス以降で最初の着席しているプレイヤーを探します（ポジション割当用）"""
        seats = self.game_state.table.seats
        for i in range(len(seats)):
            next_index = (start_index + i) % len(seats)
            if seats[next_index].is_occupied:
                return next_index
        raise RuntimeError("Could not find player for position assignment.")

    def _get_seated_players_in_action_order(self, start_pos_name: str, player_subset: List = None) -> List:
        """指定ポジションからアクション順に着席プレイヤーを並べたリストを返します"""
        seats_to_check = player_subset if player_subset is not None else self.game_state.table.seats

        try:
            start_seat = next(s for s in seats_to_check if s.position == start_pos_name)
        except StopIteration:
             # サブセットに開始ポジションがない場合は、ボタンから探す
             dealer_index = self.game_state.dealer_seat_index
             for i in range(len(self.game_state.table.seats)):
                 idx = (dealer_index + 1 + i) % len(self.game_state.table.seats)
                 seat = self.game_state.table.seats[idx]
                 if seat in seats_to_check:
                     start_seat = seat
                     break
             else:
                 return []

        start_idx_in_subset = seats_to_check.index(start_seat)
        
        ordered_list = (
            seats_to_check[start_idx_in_subset:] + seats_to_check[:start_idx_in_subset]
        )
        return [s for s in ordered_list if s.is_occupied]