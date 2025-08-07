# models/action.py
from backend.models.enum import Action, State, Status
from models import Player, Table
from typing import List, Dict, Optional


class ActionManager:
    @staticmethod
    def get_legal_actions_info(player: Player, table: Table) -> Dict[str, Optional[str, int]]:
        actions: Dict[str, Optional[str, int]] = {}
        
        current_bet = table.current_bet
        min_bet = table.min_bet
        to_call = current_bet - player.bet_total
        min_raise = to_call + min_bet
    
        if current_bet > 0:
            actions.append(Action.FOLD)

        if to_call == 0:
            actions.append(Action.CHECK)
        else:
            if player.stack >= to_call:
                actions.append(Action.CALL)
            elif player.stack > 0:
                actions.append(Action.CALL)  # オールインCALL

        if current_bet == 0:
            if player.stack >= min_bet:
                actions.append(Action.BET)
            elif player.stack > 0:
                actions.append(Action.BET)  # オールインBET

        if current_bet > 0 and player.stack >= to_call + min_bet:
            actions.append(Action.RAISE)



        return {
            "legal_actions": actions,
            "amount_ranges": {
                "bet": max(0, player.stack - min_bet),
                "raise": max(0, player.stack - min_bet - to_call),
            }
        }


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
            to_call = table.current_bet - player.bet_total
            actual_amount = min(player.stack, to_call)

            player.bet_total += actual_amount
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

        bet_amount = min(player.stack, amount)
        player.bet_total += bet_amount
        table.current_bet = player.bet_total
        table.pot += bet_amount

        table.min_bet = bet_amount  # BET後にmin_betを更新
        player.act(Action.BET, bet_amount)

    @staticmethod
    def _apply_raise(player: Player, table: Table, amount: int):
        if amount < table.min_bet:
            raise ValueError(f"RAISE金額はmin_bet以上である必要があります: {table.min_bet}")

        call_amount = table.current_bet - player.bet_total
        raise_amount = min(player.stack, amount)
        total = call_amount + raise_amount

        actual_total = min(player.stack, total)
        player.bet_total += actual_total
        table.current_bet = player.bet_total
        table.pot += actual_total

        table.min_bet = raise_amount
        player.act(Action.RAISE, actual_total)