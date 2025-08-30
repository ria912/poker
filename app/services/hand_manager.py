# holdem_app/app/services/hand_manager.py
from app.models.game_state import GameState
from app.models.enum import GameStatus, Round, SeatStatus
from . import position_service, round_manager, evaluation_service

def start_hand(game_state: GameState):
    """
    ハンドを開始するための準備を行う。
    - ディーラーボタンの決定
    - ブラインドの徴収
    - カードの配布
    """
    game_state.clear_for_new_hand()
    print("\n--- Starting New Hand ---")

    # 参加プレイヤーが2人未満ならハンドを開始しない
    active_players = [s for s in game_state.table.seats if s.is_occupied and s.stack > 0]
    if len(active_players) < 2:
        game_state.status = GameStatus.WAITING
        print("Not enough players to start a hand.")
        return

    # 1. ディーラーボタン決定
    position_service.rotate_dealer_button(game_state)
    
    # 2. ポジション割り当て
    position_service.assign_positions(game_state)

    # 3. ブラインドの徴収
    # ... position_service を使ってSB, BB のプレイヤーからベットさせる
    
    # 4. カード配布
    deck = game_state.table.deck
    for seat in game_state.table.seats:
        if seat.is_occupied:
            seat.receive_cards(deck.draw(2))
    
    game_state.status = GameStatus.IN_PROGRESS
    game_state.current_round = Round.PREFLOP
    
    # プリフロップのラウンドを開始
    round_manager.start_betting_round(game_state)


def end_hand(game_state: GameState):
    """
    ハンドの終了処理を行う。
    - 勝者の決定
    - ポットの分配
    """
    print("--- Ending Hand ---")
    
    # 1. ベットをポットに集める
    game_state.table.collect_bets()
    
    # 2. 勝者判定
    winners_with_pot = evaluation_service.find_winners(game_state)
    
    # 3. ポット分配
    for seat, amount in winners_with_pot:
        seat.stack += amount
        print(f"{seat.player.name} wins {amount}.")

    game_state.status = GameStatus.HAND_COMPLETE


def is_hand_over(game_state: GameState) -> bool:
    """ハンドが終了したかどうかを判定する"""
    # アクティブなプレイヤーが1人になった場合
    active_seats = [s for s in game_state.table.seats if s.status == SeatStatus.ACTIVE]
    if len(active_seats) <= 1 and game_state.status == GameStatus.IN_PROGRESS:
        return True
    
    # リバーのベッティングラウンドが終了した場合
    if game_state.current_round == Round.RIVER and round_manager.is_round_over(game_state):
        return True
        
    return False
