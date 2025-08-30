# app/services/action_service.py
from typing import Optional
from ..models.game_state import GameState
from ..models.enum import ActionType, SeatStatus
from ..models.seat import Seat

class ActionService:
    """プレイヤーのアクションを処理し、GameStateを更新するクラス"""

    def get_valid_actions(self, game_state: GameState, seat_index: int) -> list[ActionType]:
        """
        指定されたプレイヤーが現在実行可能なアクションのリストを返します。
        AIがアクションを選択する際の候補として利用します。
        """
        valid_actions = []
        seat = game_state.table.seats[seat_index]
        if not seat.is_active:
            return []

        # FOLDは常に可能
        valid_actions.append(ActionType.FOLD)

        # CHECK or CALL
        is_bet_placed = game_state.amount_to_call > 0
        is_facing_bet = seat.current_bet < game_state.amount_to_call
        
        if is_facing_bet:
            valid_actions.append(ActionType.CALL)
        else:
            valid_actions.append(ActionType.CHECK)

        # BET or RAISE
        # 相手のスタックがある場合のみ可能
        has_opponent_with_stack = any(
            s.is_active and s.index != seat.index and s.stack > 0
            for s in game_state.table.seats
        )
        if has_opponent_with_stack:
            if is_bet_placed:
                valid_actions.append(ActionType.RAISE)
            else:
                valid_actions.append(ActionType.BET)
        
        return valid_actions

    def perform_action(self, game_state: GameState, seat_index: int, action_type: ActionType, amount: int = 0):
        """指定されたアクションを実行し、GameStateを更新します"""
        seat = game_state.table.seats[seat_index]
        if not seat.is_active or game_state.current_seat_index != seat_index:
            raise ValueError("It's not this player's turn or player is not active.")

        # アクションに応じたハンドラを呼び出す
        handler = self._get_action_handler(action_type)
        handler(game_state, seat, amount)

        seat.acted = True
        
        # 次のアクションプレイヤーへターンを移す
        self._move_to_next_player(game_state)

    def _get_action_handler(self, action_type: ActionType):
        """アクションタイプに応じた処理メソッドを返します"""
        handlers = {
            ActionType.FOLD: self._handle_fold,
            ActionType.CHECK: self._handle_check,
            ActionType.CALL: self._handle_call,
            ActionType.BET: self._handle_bet,
            ActionType.RAISE: self._handle_raise,
        }
        if action_type not in handlers:
            raise ValueError(f"Invalid action type: {action_type}")
        return handlers[action_type]

    def _handle_fold(self, game_state: GameState, seat: Seat, amount: int):
        seat.status = SeatStatus.FOLDED

    def _handle_check(self, game_state: GameState, seat: Seat, amount: int):
        if seat.current_bet < game_state.amount_to_call:
            raise ValueError("Cannot check, there is a bet to call.")

    def _handle_call(self, game_state: GameState, seat: Seat, amount: int):
        call_amount = game_state.amount_to_call - seat.current_bet
        if call_amount <= 0:
            # 既に同額をベットしている場合（BBオプションなど）はチェックと同じ
            return
            
        if seat.stack <= call_amount: # スタックが足りなければオールイン
            self._perform_all_in(game_state, seat)
        else:
            seat.bet(call_amount)

    def _handle_bet(self, game_state: GameState, seat: Seat, amount: int):
        if game_state.amount_to_call > 0:
            raise ValueError("Cannot bet, must call or raise.")
        if amount < game_state.big_blind and amount < seat.stack:
            raise ValueError(f"Bet amount must be at least big blind({game_state.big_blind}).")
        
        if seat.stack <= amount:
            self._perform_all_in(game_state, seat)
        else:
            seat.bet(amount)
            self._update_game_state_after_raise(game_state, seat, seat.current_bet)

    def _handle_raise(self, game_state: GameState, seat: Seat, amount: int):
        if game_state.amount_to_call == 0:
            raise ValueError("Cannot raise, no bet to raise.")
        if amount < game_state.min_raise_amount and seat.stack > amount:
            raise ValueError(f"Raise amount must be at least {game_state.min_raise_amount}")

        total_bet_this_street = amount
        required_bet_amount = total_bet_this_street - seat.current_bet
        
        if seat.stack <= required_bet_amount:
            self._perform_all_in(game_state, seat)
        else:
            seat.bet(required_bet_amount)
            self._update_game_state_after_raise(game_state, seat, total_bet_this_street)

    def _perform_all_in(self, game_state: GameState, seat: Seat):
        all_in_amount = seat.stack
        seat.bet(all_in_amount)
        seat.status = SeatStatus.ALL_IN

        if seat.current_bet > game_state.amount_to_call:
            self._update_game_state_after_raise(game_state, seat, seat.current_bet)

    def _update_game_state_after_raise(self, game_state: GameState, raiser_seat: Seat, new_total_bet: int):
        """ベットまたはレイズが行われた後にゲーム状態を更新します"""
        previous_amount_to_call = game_state.amount_to_call
        game_state.amount_to_call = new_total_bet
        
        # 次のプレイヤーの最小レイズ額を計算
        raise_diff = new_total_bet - previous_amount_to_call
        game_state.min_raise_amount = new_total_bet + raise_diff
        
        game_state.last_raiser_seat_index = raiser_seat.index

        # 他のプレイヤーのアクション済みフラグをリセットして、再度アクションを求める
        for s in game_state.table.seats:
            if s.is_occupied and s.status == SeatStatus.ACTIVE:
                s.acted = False
        raiser_seat.acted = True

    def _find_next_active_player_index(self, game_state: GameState, start_index: int) -> Optional[int]:
        """指定したインデックスの次から、アクション可能なプレイヤーを探します"""
        seats = game_state.table.seats
        for i in range(1, len(seats) + 1):
            next_index = (start_index + i) % len(seats)
            if seats[next_index].is_active:
                return next_index
        return None

    def _move_to_next_player(self, game_state: GameState):
        """次のアクションプレイヤーにターンを移します"""
        next_player_index = self._find_next_active_player_index(game_state, game_state.current_seat_index)
        game_state.current_seat_index = next_player_index