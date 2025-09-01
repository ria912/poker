# tests/services/test_action_service.py
import pytest
from app.models.action import Action
from app.models.enum import ActionType, SeatStatus
from app.services import action_service

class TestGetValidActions:
    def test_facing_no_bet(self, game_state):
        # ベットがない状況ではCHECKとBETが可能
        game_state.amount_to_call = 0
        actions = action_service.get_valid_actions(game_state, 0)
        action_types = [a['type'] for a in actions]
        assert ActionType.CHECK in action_types
        assert ActionType.BET in action_types
        assert ActionType.FOLD not in action_types

    def test_facing_a_bet(self, game_state):
        # ベットがある状況ではFOLD, CALL, RAISEが可能
        game_state.amount_to_call = 100
        actions = action_service.get_valid_actions(game_state, 0)
        action_types = [a['type'] for a in actions]
        assert ActionType.FOLD in action_types
        assert ActionType.CALL in action_types
        assert ActionType.RAISE in action_types
        assert ActionType.CHECK not in action_types

class TestProcessAction:
    def test_process_fold(self, game_state):
        player_id = game_state.table.seats[0].player.player_id
        action = Action(player_id, ActionType.FOLD)
        action_service.process_action(game_state, action)
        assert game_state.table.seats[0].status == SeatStatus.FOLDED

    def test_process_bet(self, game_state):
        player_id = game_state.table.seats[0].player.player_id
        action = Action(player_id, ActionType.BET, amount=200)
        action_service.process_action(game_state, action)
        
        seat = game_state.table.seats[0]
        assert seat.current_bet == 200
        assert seat.stack == 9800
        assert game_state.amount_to_call == 200
        assert game_state.min_raise_amount == 400
        assert game_state.last_raiser_seat_index == 0

    def test_process_raise_resets_acted_flags(self, game_state):
        # プレイヤー0がベット
        p0_id = game_state.table.seats[0].player.player_id
        action_bet = Action(p0_id, ActionType.BET, amount=200)
        action_service.process_action(game_state, action_bet)
        game_state.table.seats[0].acted = True

        # プレイヤー1がレイズ
        p1_id = game_state.table.seats[1].player.player_id
        action_raise = Action(p1_id, ActionType.RAISE, amount=500)
        action_service.process_action(game_state, action_raise)
        
        # プレイヤー0のactedフラグがリセットされていることを確認
        assert game_state.table.seats[0].acted is False
        assert game_state.table.seats[1].acted is True
