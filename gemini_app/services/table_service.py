from gemini_app.models.game_state import GameState
from gemini_app.models.enum import Position
from gemini_app.utils.order_utils import get_next_active_seat_index

# ブラインドの額をここで定義（将来的には設定ファイルなどに移すのが良い）
SB_AMOUNT = 5
BB_AMOUNT = 10

def start_new_hand(game_state: GameState) -> GameState:
    """
    新しいハンドを開始するためのセットアップを行う。
    """
    # 1. 前のハンドの情報をクリア
    game_state.clear_for_new_hand()

    # 2. アクティブプレイヤーが2人未満ならゲームを開始しない
    active_players = [seat.player for seat in game_state.table.seats if seat.player]
    if len(active_players) < 2:
        raise ValueError("Cannot start hand with fewer than 2 players.")

    # 3. ディーラーボタンを次の人に回す
    game_state.table.dealer_button_position = get_next_active_seat_index(
        game_state.table.seats, game_state.table.dealer_button_position
    )

    # 4. ポジションを割り振る
    _assign_positions(game_state)

    # 5. ブラインドを徴収する
    _post_blinds(game_state)
    
    # 6. カードを配る
    _deal_hole_cards(game_state)
    
    # 7. 最初のアクションプレイヤーを決定する
    # BBの次のプレイヤーが最初のアクション番
    bb_seat_index = _find_player_index_by_position(game_state, Position.BB)
    game_state.active_seat_index = get_next_active_seat_index(game_state.table.seats, bb_seat_index)
    
    # 最初にアクションするプレイヤーが誰だったかを記録（1周したかの判定に使う）
    game_state.last_raiser_seat_index = game_state.active_seat_index
    
    return game_state


def _assign_positions(game_state: GameState):
    """各プレイヤーにポジションを割り振る"""
    seats = game_state.table.seats
    btn_index = game_state.table.dealer_button_position

    sb_index = get_next_active_seat_index(seats, btn_index)
    seats[sb_index].player.position = Position.SB

    bb_index = get_next_active_seat_index(seats, sb_index)
    seats[bb_index].player.position = Position.BB
    
    # TODO: UTG, MP, COなども同様に割り振るロジックを追加

def _post_blinds(game_state: GameState):
    """ブラインドをプレイヤーのスタックからポットに移動させる"""
    # SB
    sb_index = _find_player_index_by_position(game_state, Position.SB)
    sb_player = game_state.table.seats[sb_index].player
    sb_bet = min(sb_player.stack, SB_AMOUNT) # スタックが足りない場合も考慮
    sb_player.stack -= sb_bet
    sb_player.bet_amount_in_round = sb_bet
    game_state.table.pot += sb_bet

    # BB
    bb_index = _find_player_index_by_position(game_state, Position.BB)
    bb_player = game_state.table.seats[bb_index].player
    bb_bet = min(bb_player.stack, BB_AMOUNT)
    bb_player.stack -= bb_bet
    bb_player.bet_amount_in_round = bb_bet
    game_state.table.pot += bb_bet

    # 現在のコールすべき額とミニマムレイズ額を設定
    game_state.amount_to_call = BB_AMOUNT
    game_state.min_raise_amount = BB_AMOUNT * 2


def _deal_hole_cards(game_state: GameState):
    """各プレイヤーに2枚ずつカードを配る"""
    seats = game_state.table.seats
    deck = game_state.table.deck
    start_index = get_next_active_seat_index(seats, game_state.table.dealer_button_position)

    # 1枚ずつ2周配る
    for _ in range(2):
        current_index = start_index
        while True:
            player = seats[current_index].player
            if player and player.is_active:
                card_int = deck.draw_one()
                player.hand.append(card_int) # ここではtreysの整数表現のままハンドに追加
            
            current_index = get_next_active_seat_index(seats, current_index)
            if current_index == start_index:
                break


def _find_player_index_by_position(game_state: GameState, position: Position) -> int:
    """指定されたポジションのプレイヤーの座席インデックスを探す"""
    for i, seat in enumerate(game_state.table.seats):
        if seat.player and seat.player.position == position:
            return i
    raise ValueError(f"Player with position {position} not found.")