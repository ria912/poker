from gemini_app.models.game_state import GameState
from gemini_app.models.enum import Action
from gemini_app.utils.order_utils import get_next_active_seat_index, get_active_player_count

def handle_player_action(
    game_state: GameState, 
    action: Action, 
    raise_amount: int = 0
) -> GameState:
    """
    プレイヤーのアクションを処理し、ゲームの状態を更新する。
    """
    # 現在アクションすべきプレイヤーを取得
    active_seat_idx = game_state.active_seat_index
    player = game_state.table.seats[active_seat_idx].player

    if not player or not player.is_active:
        raise ValueError("Invalid player to perform an action.")

    # アクションに応じた処理を呼び出す
    if action == Action.FOLD:
        _handle_fold(game_state, player)
    elif action == Action.CALL:
        _handle_call(game_state, player)
    elif action == Action.RAISE:
        _handle_raise(game_state, player, raise_amount)
    elif action == Action.CHECK:
        _handle_check(game_state, player)
    else:
        raise ValueError(f"Unsupported action: {action}")

    # 次のアクションプレイヤーを決定する
    _update_next_player(game_state)

    return game_state

def _handle_fold(game_state: GameState, player):
    """フォールド処理"""
    player.is_active = False

def _handle_call(game_state: GameState, player):
    """コール処理"""
    amount_to_call = game_state.amount_to_call - player.bet_amount_in_round
    bet = min(player.stack, amount_to_call) # 所持スタック以上はベットできない

    player.stack -= bet
    player.bet_amount_in_round += bet
    game_state.table.pot += bet
    
    if player.stack == 0:
        player.is_all_in = True

def _handle_raise(game_state: GameState, player, raise_amount: int):
    """レイズ処理"""
    # バリデーション
    if raise_amount < game_state.min_raise_amount:
        raise ValueError(f"Raise amount must be at least {game_state.min_raise_amount}")
    if raise_amount > player.stack:
        raise ValueError("Cannot raise more than available stack.")

    # レイズは、前のベット額(amount_to_call) + 上乗せ分
    total_bet = raise_amount
    bet_diff = total_bet - player.bet_amount_in_round
    
    player.stack -= bet_diff
    player.bet_amount_in_round = total_bet
    game_state.table.pot += bet_diff

    # ゲーム状態の更新
    game_state.amount_to_call = total_bet
    # 次のミニマムレイズ額は、今回のレイズの上乗せ分
    game_state.min_raise_amount = total_bet + (total_bet - game_state.amount_to_call)
    game_state.last_raiser_seat_index = game_state.active_seat_index

    if player.stack == 0:
        player.is_all_in = True
        
def _handle_check(game_state: GameState, player):
    """チェック処理"""
    # チェックができるのは、誰もベットしていない場合（コール額が0の場合）のみ
    if player.bet_amount_in_round < game_state.amount_to_call:
        raise ValueError("Cannot check when there is a bet to call.")
    # チェックはベット額の変更なし

def _update_next_player(game_state: GameState):
    """次のアクションプレイヤーを決定、またはラウンドを終了する"""
    
    # 残りアクティブプレイヤーが1人なら、その人が勝者
    if get_active_player_count(game_state.table.seats) <= 1:
        # TODO: 勝者決定とポット分配のロジックを呼び出す
        print("A winner is decided by fold.")
        # game_state.status = GameStatus.FINISHED
        return

    next_player_index = get_next_active_seat_index(
        game_state.table.seats, game_state.active_seat_index
    )

    # 次のプレイヤーが、最後にレイズした人だったら、ベッティングラウンド終了
    if next_player_index == game_state.last_raiser_seat_index:
        # TODO: 次のラウンドに進むロジックを呼び出す
        print(f"Betting round finished. Pot: {game_state.table.pot}")
        # _proceed_to_next_round(game_state)
        game_state.active_seat_index = None # ラウンド終了時は一旦Noneにする
    else:
        game_state.active_seat_index = next_player_index