from app.models.game_state import GameState
from app.models.player import Player
from app.models.enum import Position, Round, PlayerState
from utils import order_utils
from typing import List

# 他のサービスモジュール（今後作成）
from . import evoluter
from .. import table_service

def start_preflop_round(game_state: GameState):
    """
    プリフロップラウンドを開始し、最初のアクションプレイヤーを決定する。
    プリフロップでは、BBの次のプレイヤーからアクションが始まる。
    """
    game_state.table.current_round = Round.PREFLOP
    active_seats = table_service.get_active_seats(game_state)
    # BBのプレイヤーを探す
    bb_player = table_service.get_player_by_position(game_state, Position.BB)
    if not bb_player:
        raise RuntimeError("Big Blind player not found.")

    bb_player_index = active_seats.index(bb_player)

    # 次にアクションすべきプレイヤーのインデックスを見つける
    # order_utilsを使って、BBの次から循環的に探す
    condition = lambda p: p.state == PlayerState.ACTIVE
    next_player_index = order_utils.get_next_item_index(
        items=active_seats,
        start_index=bb_player_index,
        condition=condition
    )
    
    if next_player_index is None:
        # 全員オールインなどの特殊ケース
        proceed_to_next_round(game_state)
        return

    # 次のアクションプレイヤーを設定
    game_state.active_player_id = active_seats[next_player_index].player.player_id

    # ベットの基準となるプレイヤー（アグレッサー）は最初はBB
    game_state.last_raiser_id = bb_player.player_id
    print(f"Pre-flop round started. Action is on {active_players[next_player_index].name}.")

def start_postflop_round(game_state: GameState):
    """
    フロップ、ターン、リバーのラウンドを開始する。
    ポストフロップでは、ディーラーボタンの次のプレイヤーからアクションが始まる。
    """
    # 各プレイヤーのベット額をリセット
    table_service.reset_players_bet_for_round(game_state)
    
    # アクティブなプレイヤーリストを取得
    active_players = table_service.get_active_players_in_hand(game_state)

    # ディーラーボタンの位置を基準に、次にアクションするプレイヤーを探す
    dealer_seat_index = game_state.table.dealer_position - 1
    
    # 席順のリストを作成（Noneは空席）
    seated_players = table_service.get_players_in_seat_order(game_state)
    
    # ディーラーの次から循環的にアクティブプレイヤーを探す
    condition = lambda p: p is not None and p.state == PlayerState.ACTIVE
    first_to_act_index = order_utils.get_next_item_index(
        items=seated_players,
        start_index=dealer_seat_index,
        condition=condition
    )
    
    if first_to_act_index is None:
        # アクティブプレイヤーがいない（全員オールインなど）
        proceed_to_next_round(game_state)
        return

    game_state.active_player_id = seated_players[first_to_act_index].player_id
    game_state.last_raiser_id = None # ポストフロップでは最初は誰もレイズしていない
    print(f"{game_state.table.current_round} round started. Action is on {seated_players[first_to_act_index].name}.")


def end_player_action(game_state: GameState):
    """

    プレイヤーのアクション完了後に呼び出される。
    次のアクションプレイヤーを決定するか、ラウンドを終了するかを判断する。
    """
    active_players = table_service.get_active_players_in_hand(game_state)
    
    # アクティブプレイヤーが1人になったらハンド終了
    if len(active_players) == 1:
        winner = active_players[0]
        print(f"Only one player left. {winner.name} wins the pot of {game_state.table.pot}.")
        table_service.award_pot_to_winner(game_state, winner)
        return

    # ベッティングラウンドが終了したかチェック
    if _is_betting_round_over(game_state):
        proceed_to_next_round(game_state)
        return
        
    # ラウンド継続、次のプレイヤーを決定
    current_player = game_state.get_player_by_id(game_state.active_player_id)
    seated_players = table_service.get_players_in_seat_order(game_state)
    current_player_seat_index = table_service.get_seat_index_by_player_id(game_state, current_player.player_id)

    condition = lambda p: p is not None and p.state == PlayerState.ACTIVE
    next_player_index = order_utils.get_next_item_index(
        items=seated_players,
        start_index=current_player_seat_index,
        condition=condition
    )
    
    game_state.active_player_id = seated_players[next_player_index].player_id
    print(f"Action is now on {seated_players[next_player_index].name}.")

def _is_betting_round_over(game_state: GameState) -> bool:
    """ベッティングラウンドが終了したかを判定する"""
    active_players = [p for p in game_state.players if p.state == PlayerState.ACTIVE]
    if not active_players:
        return True # アクティブプレイヤーがいない場合は終了

    # 全員のアクションが完了し、かつベット額が同額かチェック
    highest_bet = max(p.current_bet for p in active_players)
    
    # プリフロップBBのオプション行使チェック
    if game_state.table.current_round == GameRound.PREFLOP and game_state.last_raiser_id == game_state.get_bb_player().player_id and highest_bet == game_state.get_bb_player().current_bet:
        if game_state.active_player_id == game_state.last_raiser_id:
             return True

    # 全員が同じ額をベットしているか
    all_bets_equal = all(p.current_bet == highest_bet for p in active_players)
    
    # 最後にレイズしたプレイヤーまでアクションが一周したか
    # 現在アクションしたプレイヤーが、最後にレイズしたプレイヤーのすぐ左隣のプレイヤーか？
    # ここでは簡略化し、ベット額が全員同じで、最後にレイズしたプレイヤーのアクションが終わったら終了とみなす
    if all_bets_equal and game_state.active_player_id == game_state.last_raiser_id:
        return True
        
    # 全員チェックで回った場合
    if highest_bet == 0 and game_state.last_raiser_id is None:
        current_player_id = game_state.active_player_id
        # 全員のアクションが終わったかをチェックする必要があるが、簡略化のためここでは省略

    return False

def proceed_to_next_round(game_state: GameState):
    """現在のラウンドを終了し、次のラウンドへ進む"""
    current_round = game_state.table.current_round
    table_service.collect_bets_to_pot(game_state)
    print(f"--- Round {current_round} ended. Pot is now {game_state.table.pot}. ---")

    if current_round == GameRound.PREFLOP:
        game_state.table.current_round = GameRound.FLOP
        game_state.table.community_cards.extend(game_state.deck.deal(3))
        start_postflop_round(game_state)
    
    elif current_round == GameRound.FLOP:
        game_state.table.current_round = GameRound.TURN
        game_state.table.community_cards.extend(game_state.deck.deal(1))
        start_postflop_round(game_state)

    elif current_round == GameRound.TURN:
        game_state.table.current_round = GameRound.RIVER
        game_state.table.community_cards.extend(game_state.deck.deal(1))
        start_postflop_round(game_state)

    elif current_round == GameRound.RIVER:
        game_state.table.current_round = GameRound.SHOWDOWN
        # 勝者判定ロジックを呼び出す

