# models/action.py
from backend.models.enum import Action, State, Status
from models import Player, Table
from typing import List, Dict, Optional


class ActionManager:
    @staticmethod
    def get_legal_actions_info(player: Player, table: Table) -> Dict[str, Optional[Dict[str, int]]]:
        """
        現在のプレイヤーに対して合法なアクションと、その金額範囲（必要があれば）を返す。

        例:
        {
            "FOLD": None,
            "CALL": {"amount": 40},
            "RAISE": {"min": 80, "max": 200}
        }
        """
        actions: Dict[str, Optional[Dict[str, int]]] = {}
        
        current_bet = table.current_bet
        min_bet = table.min_bet
        to_call = current_bet - player.bet_total
        min_raise = to_call + min_bet
        stack = player.stack


        # --- FOLD ---
        if current_bet > 0:
            actions[Action.FOLD] = None

        # --- CHECK or CALL ---
        if to_call <= 0:
            actions[Action.CHECK] = None
        else:
            call_amount = min(to_call, stack)
            actions[Action.CALL] = {"amount": call_amount}

        # --- BET (no bet yet) ---
        if current_bet == 0 and stack > 0:
            min_amount = min_bet
            max_amount = stack
            if min_amount <= max_amount:
                actions[Action.BET] = {
                    "min": min_amount,
                    "max": max_amount
                }
            else:
                actions[Action.BET] = {
                    "min": stack,
                    "max": stack
                }

        # --- RAISE (someone already bet) ---
        if current_bet > 0 and stack > min_raise:
            min_amount = min_raise
            max_amount = stack
            if min_amount <= max_amount:
                actions[Action.RAISE] = {
                    "min": min_amount,
                    "max": max_amount
                }

        return actions


    @staticmethod
    def apply_action(player: Player, table: Table, action: Action, amount: int):
        if action == Action.FOLD:
            player.act(action)

        elif action == Action.CHECK:
            if table.current_bet == player.bet_total:
                player.act(action)
            else:
                raise ValueError("ベットが存在しているため、チェックはできません")

        elif action == Action.CALL:
            actual_amount = min(player.stack, amount)

            table.pot += actual_amount

            player.act(action, actual_amount)

        elif action == Action.BET:
            ActionManager._apply_bet(player, table, amount)
            table.last_raiser = player

        elif action == Action.RAISE:
            ActionManager._apply_raise(player, table, amount)
            table.last_raiser = player

    @staticmethod
    def _apply_bet(player: Player, table: Table, amount: int):
        if amount < table.min_bet:
            raise ValueError(f"BET金額はmin_bet以上である必要があります: {table.min_bet}")
        player.act(Action.BET, amount)
        table.current_bet = amount
        table.pot += amount
        if amount > table.min_bet:
            table.min_bet = amount

    @staticmethod
    def _apply_raise(player: Player, table: Table, amount: int):
        if amount < table.min_bet:
            raise ValueError(f"RAISE金額はmin_bet以上である必要があります: {table.min_bet}")
        
        player.act(Action.RAISE, amount)
        table.current_bet = player.bet_total
        table.pot += amount
        if amount > table.min_bet:
            table.min_bet = amount
    
    @staticmethod
    def _apply_all_in(player: Player, table: Table):
        amount = player.stack
        if amount <= 0:
            raise ValueError("プレイヤーはスタックがありません。ALL_INできません。")
        table.pot += amount
        player.act(Action.ALL_IN)
        if player.bet_total > table.current_bet:
            table.current_bet = player.bet_total
            table.min_bet = player.bet_total - amount
