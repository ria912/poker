# holdem_app/tests/services/test_round_manager.py
import pytest
from unittest.mock import MagicMock
from app.models.game_state import GameState
from app.models.game_config import GameConfig
from app.models.player import Player
from app.models.action import Action
from app.models.enum import ActionType, Round, SeatStatus  # SeatStatusをインポート
from app.services import round_manager, position_service

@pytest.fixture
def game_state_preflop():
    """プリフロップの3人プレイのセットアップ"""
    config = GameConfig(big_blind=100, small_blind=50)
    gs = GameState(config)
    
    players = [Player(f"p{i}") for i in range(3)]
    gs.table.sit_player(players[0], 0, 10000)
    gs.table.sit_player(players[1], 1, 10000)
    gs.table.sit_player(players[2], 2, 10000)
    
    gs.dealer_seat_index = 0
    position_service.assign_positions(gs)
    
    # Blinds
    gs.table.seats[1].bet(50)  # SB
    gs.table.seats[2].bet(100) # BB
    gs.amount_to_call = 100
    gs.min_raise_amount = 100
    gs.current_round = Round.PREFLOP
    
    return gs

class TestRunBettingRound:
    
    def test_everyone_folds_to_bb(self, game_state_preflop):
        gs = game_state_preflop
        
        # BTN (p0) folds, SB (p1) folds
        actions_to_take = [
            Action(player_id=gs.table.seats[0].player.player_id, action_type=ActionType.FOLD),
            Action(player_id=gs.table.seats[1].player.player_id, action_type=ActionType.FOLD)
        ]
        
        mock_get_action = MagicMock(side_effect=actions_to_take)
        
        round_manager.run_betting_round(gs, mock_get_action)
        
        assert mock_get_action.call_count == 2
        assert gs.table.pot == 150 # SB + BB
        # --- ここから修正 ---
        assert gs.table.seats[0].status == SeatStatus.FOLDED
        assert gs.table.seats[1].status == SeatStatus.FOLDED
        assert gs.table.seats[2].status != SeatStatus.FOLDED
        # --- 修正ここまで ---

    def test_raise_and_everyone_calls(self, game_state_preflop):
        gs = game_state_preflop
        p0, p1, p2 = gs.table.seats[0].player, gs.table.seats[1].player, gs.table.seats[2].player

        # BTN (p0) raises to 300
        # SB (p1) folds
        # BB (p2) calls 200
        actions_to_take = [
            Action(player_id=p0.player_id, action_type=ActionType.RAISE, amount=300),
            Action(player_id=p1.player_id, action_type=ActionType.FOLD),
            Action(player_id=p2.player_id, action_type=ActionType.CALL, amount=300),
        ]
        mock_get_action = MagicMock(side_effect=actions_to_take)
        
        round_manager.run_betting_round(gs, mock_get_action)
        
        assert mock_get_action.call_count == 3
        # 300(p0) + 50(p1) + 300(p2) = 650
        assert gs.table.pot == 650
        # --- ここから修正 ---
        assert gs.table.seats[1].status == SeatStatus.FOLDED
        # --- 修正ここまで ---

    def test_reraise_scenario(self, game_state_preflop):
        gs = game_state_preflop
        p0, p1, p2 = gs.table.seats[0].player, gs.table.seats[1].player, gs.table.seats[2].player

        # BTN(p0) raises to 300
        # SB(p1) reraises to 900
        # BB(p2) folds
        # BTN(p0) calls 600 more
        actions_to_take = [
            Action(player_id=p0.player_id, action_type=ActionType.RAISE, amount=300),
            Action(player_id=p1.player_id, action_type=ActionType.RAISE, amount=900),
            Action(player_id=p2.player_id, action_type=ActionType.FOLD),
            Action(player_id=p0.player_id, action_type=ActionType.CALL, amount=900),
        ]
        mock_get_action = MagicMock(side_effect=actions_to_take)

        round_manager.run_betting_round(gs, mock_get_action)
        
        assert mock_get_action.call_count == 4
        # 900(p0) + 900(p1) + 100(p2) = 1900
        assert gs.table.pot == 1900

