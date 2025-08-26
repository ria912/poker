# services/action_service.py
from typing import List, Optional
from app.models.table import Table, Seat
from app.models.enum import Action, PlayerState
from app.models.game_state import GameState
from .table_service import TableService

class ActionService:
    def __init__(self):
        self._table = TableService()

    # -------- 合法手アセス --------
    def get_legal_actions(self, table: Table, gs: GameState, seat_index: int) -> List[Action]:
        seat = table.get_seat(seat_index)
        if seat is None or seat.state != PlayerState.ACTIVE:
            return []
        committed = gs.round_bets.get(seat_index, 0)
        to_call = max(gs.current_bet - committed, 0)

        actions: List[Action] = [Action.FOLD]
        if seat.stack <= 0:
            # スタックなし（＝オールイン済み）
            return [Action.FOLD]  # 実質アクション不可（呼び出し側でスキップされる想定）

        if to_call == 0:
            actions.append(Action.CHECK)
            actions.append(Action.BET)  # 現在ベットが無いならBET可
        else:
            actions.append(Action.CALL)
            actions.append(Action.RAISE)

        actions.append(Action.ALL_IN)  # 常に選択可（額によりベット/レイズ扱い）
        return actions

    # -------- アクション適用 --------
    def apply(self, table: Table, gs: GameState, seat_index: int, action: Action, amount: Optional[int] = None) -> None:
        seat = table.get_seat(seat_index)
        if seat is None or seat.state != PlayerState.ACTIVE:
            return

        committed = gs.round_bets.get(seat_index, 0)
        to_call = max(gs.current_bet - committed, 0)

        def mark_others_need_to_act():
            # ベット/レイズ後は他のアクティブ勢を未行動に戻す（フォールド・オールインは除く）
            for s in table.seats:
                if s.player_id and s.state == PlayerState.ACTIVE and s.index != seat_index and s.stack > 0:
                    s.acted = False

        if action == Action.FOLD:
            seat.state = PlayerState.FOLDED
            seat.acted = True

        elif action == Action.CHECK:
            if to_call != 0:
                raise ValueError("CHECK は to_call==0 のときのみ許可")
            seat.acted = True

        elif action == Action.CALL:
            pay = min(seat.stack, to_call)
            seat.stack -= pay
            seat.bet_total += pay
            gs.round_bets[seat_index] = committed + pay
            seat.acted = True

        elif action in (Action.BET, Action.RAISE, Action.ALL_IN):
            # 汎用化：実際に支払う額を決定
            if action == Action.ALL_IN:
                bet_add = seat.stack
            else:
                if amount is None or amount <= 0:
                    raise ValueError("BET/RAISE には正の amount が必要")
                bet_add = min(seat.stack, amount - committed)

            new_commit = committed + bet_add
            new_current = max(gs.current_bet, new_commit)

            # 最小レイズチェック（ALL_IN が min_raise 未満の場合の再オープン扱いは後続の高度化で対応）
            if gs.current_bet == 0 and action != Action.ALL_IN and bet_add < gs.min_raise:
                raise ValueError("BET が最小ベット（=min_raise）未満")
            if gs.current_bet > 0 and action != Action.ALL_IN and (new_current - gs.current_bet) < gs.min_raise:
                raise ValueError("RAISE が最小レイズ未満")

            # 支払い
            seat.stack -= bet_add
            seat.bet_total += bet_add
            gs.round_bets[seat_index] = new_commit

            # 現在ベット・レイズ情報更新
            if new_current > gs.current_bet:
                gs.min_raise = max(gs.min_raise, new_current - gs.current_bet)
                gs.current_bet = new_current
                gs.last_aggressor = seat_index
                mark_others_need_to_act()

            seat.acted = True

        else:
            raise ValueError("未知のアクション")

        # ポット更新
        self._table.recompute_pot(table)

    # -------- ラウンド終了判定 --------
    def is_betting_round_complete(self, table: Table, gs: GameState) -> bool:
        # ① 複数以外生存 → 即終了（他はフォールド）
        alive = [s for s in table.seats if s.player_id and s.state == PlayerState.ACTIVE]
        if len(alive) <= 1:
            return True

        # ② 全員が acted=True かつ ラウンド投入額が揃っている
        #    （オールイン者は acted=True 扱い）
        target = gs.current_bet
        everyone_acted = True
        for s in alive:
            if s.stack == 0:
                continue  # オールイン
            if not s.acted:
                everyone_acted = False
                break
        bets_aligned = all(gs.round_bets.get(s.index, 0) == target or s.stack == 0 for s in alive)
        return everyone_acted and bets_aligned

    # -------- 次アクター選出 --------
    def next_to_act(self, table: Table, gs: GameState, from_index: int) -> Optional[int]:
        def pred(seat: Seat) -> bool:
            return (seat.player_id is not None
                    and seat.state == PlayerState.ACTIVE
                    and seat.stack > 0
                    and seat.acted is False)
        return self._table.next_seat_index(table, from_index, pred=pred)