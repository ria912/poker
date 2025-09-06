# holdem_app/app/services/simulation/simulation_runner.py
from collections import defaultdict
from app.models.game_state import GameState
from app.models.enum import Round, GameStatus, SeatStatus, ActionType
from app.services import (
    hand_manager,
    round_manager,
    position_service,
    action_service,
)
from app.services.ai import ai_agent_service
from .player_stats import PlayerStats

class SimulationRunner:
    """AI同士の対戦を高速にシミュレートするためのクラス"""

    def __init__(self, game_state: GameState, player_stats: dict[str, PlayerStats]):
        self.game_state = game_state
        self.player_stats = player_stats

    def run_simulation(self, num_hands: int):
        """指定されたハンド数だけシミュレーションを実行する"""
        initial_stacks = {seat.player.player_id: seat.stack for seat in self.game_state.table.seats if seat.player}

        for i in range(num_hands):
            if len(position_service.get_occupied_seats(self.game_state)) < 2:
                print("Not enough players to continue.")
                break
            
            self._play_hand_silently()

            # スタックが0になったプレイヤーを退席させる
            for seat in self.game_state.table.seats:
                if seat.is_occupied and seat.stack == 0:
                    self.game_state.table.stand_player(seat.index)
            
            # 1000ハンドごとに進捗を表示
            if (i + 1) % 1000 == 0:
                print(f"  ... {i + 1} hands simulated.")
        
        # 最終結果を記録
        for seat in self.game_state.table.seats:
             if seat.player and seat.player.player_id in self.player_stats:
                stats = self.player_stats[seat.player.player_id]
                # total_winnings はハンドごとに記録されているので、ここでは何もしない

    def _play_hand_silently(self):
        """1ハンドをログ出力なしで実行する"""
        hand_manager.start_new_hand(self.game_state)
        
        if self.game_state.status != GameStatus.IN_PROGRESS:
            return
        
        # ハンド開始時のスタックを記録
        starting_stacks = {seat.player.player_id: seat.stack for seat in self.game_state.table.seats if seat.player}


        # プリフロップのアクションを追跡
        preflop_actions = defaultdict(lambda: {"did_vpip": False, "did_pfr": False})
        
        for round_enum in [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER]:
            self.game_state.current_round = round_enum
            
            if round_enum != Round.PREFLOP:
                hand_manager.proceed_to_next_round(self.game_state, verbose=False)

            if hand_manager._is_hand_over(self.game_state):
                break
            
            # --- ここで get_action を直接呼び出す ---
            # round_manager.run_betting_round は print を含む可能性があるため、
            # 内部ロジックをここで再現する
            self._run_betting_round_silently(round_enum, preflop_actions)

            if hand_manager._is_hand_over(self.game_state):
                break

        hand_manager._conclude_hand(self.game_state, verbose=False)
        
        # --- ハンド結果をPlayerStatsに記録 ---
        for seat in self.game_state.table.seats:
            if seat.player and seat.player.player_id in self.player_stats:
                player_id = seat.player.player_id
                stats = self.player_stats[player_id]
                stats.record_hand_result(seat.stack, starting_stacks[player_id])
                
                # プリフロップ統計の記録
                bb_seat = position_service.get_seat_by_position(self.game_state, "BB")
                is_blind = seat.position in ["SB", "BB"]
                # BBがオープンレイズに直面していない場合、VPIP機会から除外
                vpip_opportunity = not (seat.position == "BB" and self.game_state.amount_to_call == self.game_state.big_blind and not any(s.current_bet > self.game_state.big_blind for s in self.game_state.table.seats if s.player))
                
                # 誰かがレイズするまでがPFR機会
                pfr_opportunity = not any(s.bet_total > self.game_state.big_blind for s in self.game_state.table.seats if s.player and s.index != seat.index)

                stats.record_preflop_action(
                    vpip_opportunity=vpip_opportunity,
                    pfr_opportunity=pfr_opportunity,
                    did_vpip=preflop_actions[player_id]["did_vpip"],
                    did_pfr=preflop_actions[player_id]["did_pfr"]
                )


    def _run_betting_round_silently(self, current_round, preflop_actions):
        """ベッティングラウンドをログなしで実行する"""
        if current_round != Round.PREFLOP:
            round_manager.prepare_for_new_round(self.game_state)
        
        first_to_act_index = position_service.get_first_to_act_index(self.game_state)
        if first_to_act_index is None: return
        self.game_state.current_seat_index = first_to_act_index
        
        while True:
            current_seat = self.game_state.table.seats[self.game_state.current_seat_index]

            if current_seat.status == SeatStatus.ACTIVE:
                # AIのアクションを取得
                action = ai_agent_service.decide_action(self.game_state)
                
                # プリフロップ統計用のフラグを立てる
                if current_round == Round.PREFLOP:
                    player_id = current_seat.player.player_id
                    if action.action_type in [ActionType.CALL, ActionType.BET, ActionType.RAISE]:
                        preflop_actions[player_id]["did_vpip"] = True
                    if action.action_type in [ActionType.BET, ActionType.RAISE]:
                        preflop_actions[player_id]["did_pfr"] = True

                action_service.process_action(self.game_state, action)

            if round_manager.is_betting_round_over(self.game_state):
                break

            next_idx = position_service.get_next_active_player_index(
                self.game_state, self.game_state.current_seat_index
            )
            if next_idx is None: break
            self.game_state.current_seat_index = next_idx
        
        self.game_state.table.collect_bets()
