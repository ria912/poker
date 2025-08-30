# tests/services/test_position_service.py
from app.services import position_service
from app.models.enum import Position, Round
from app.models.game_state import GameState # 追加

def test_assign_positions_6_players(game_config, players): # 引数を変更
    """6プレイヤー時のポジション割り当てをテスト"""
    # プレイヤーがいない、まっさらなGameStateを使用
    gs = GameState(game_config)
    for i in range(6):
        gs.table.sit_player(players[i], i, 1000)
    gs.dealer_seat_index = 0
    
    position_service.assign_positions(gs)
    
    seats = gs.table.seats
    assert seats[0].position == Position.BTN
    assert seats[1].position == Position.SB
    assert seats[2].position == Position.BB
    assert seats[3].position == Position.LJ
    assert seats[4].position == Position.HJ
    assert seats[5].position == Position.CO

def test_get_first_to_act_index(game_state):
    """誰が最初にアクションするかをテスト"""
    game_state.dealer_seat_index = 0
    position_service.assign_positions(game_state)

    # 3人ハンドのプリフロップ: BTN(Dealer)が最初
    game_state.current_round = Round.PREFLOP
    assert position_service.get_first_to_act_index(game_state) == 0

    # 3人ハンドのフロップ以降: SBが最初
    game_state.current_round = Round.FLOP
    assert position_service.get_first_to_act_index(game_state) == 1

