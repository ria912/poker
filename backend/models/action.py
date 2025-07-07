# models/action.py
from backend.models.enum import Action

class ActionManager:
    @staticmethod
    def get_legal_actions_info(player, table):
        actions = []
        current_bet = table.current_bet
        min_bet = table.min_bet
        to_call = current_bet - player.bet_total

        actions.append(Action.FOLD)

        if current_bet == player.bet_total:
            actions.append(Action.CHECK)
            if current_bet == 0:
                actions.append(Action.BET)
            elif current_bet > 0:
                actions.append(Action.RAISE)
        else:
            actions.append(Action.CALL)
            if player.stack >= to_call + min_bet:
                actions.append(Action.RAISE)

        return {
            "legal_actions": actions,
            "amount_ranges": {
                "bet": max(0, player.stack - min_bet),
                "raise": max(0, player.stack - min_bet - to_call),
            }
        }


    @staticmethod
    def apply_action(player, table, action, amount: int):
        if action == Action.FOLD:
            player.has_folded = True
        elif action == Action.CHECK:
            pass
        elif action == Action.CALL:
            ActionManager._apply_call(player, table)
        elif action == Action.BET:
            ActionManager._apply_bet(player, table, amount)
            table.last_raiser = player
        elif action == Action.RAISE:
            ActionManager._apply_raise(player, table, amount)
            table.last_raiser = player

        player.last_action = action

        if player.stack == 0:
            player.has_all_in = True

    @staticmethod
    def _apply_bet(player, table, amount:int):
        if amount < 0:
            raise ValueError(f"Invalid Bet amount: {amount}. Must be >= 0.")
        min_bet = table.min_bet
        total = amount + min_bet
        total = min(player.stack, total)

        player.stack -= total
        player.bet_total += total
        table.current_bet = player.bet_total
        table.pot += total

        if total > table.min_bet:
            table.min_bet = total

    @staticmethod
    def _apply_call(player, table):      
        to_call = table.current_bet - player.bet_total
        total = min(player.stack, to_call)

        player.stack -= total
        player.bet_total += total
        table.pot += total

        if player.bet_total > table.current_bet:
            table.current_bet = player.bet_total

    @staticmethod
    def _apply_raise(player, table, amount:int):
        if amount < 0:
            raise ValueError(f"Invalid Bet/Raise amount: {amount}. Must be >= 0.")
        min_bet = table.min_bet
        call_amount = table.current_bet - player.bet_total
        total = amount + min_bet + call_amount
        total = min(player.stack, total)

        player.stack -= total
        player.bet_total += total
        table.pot += total
        table.current_bet = player.bet_total

        raise_amount = total - call_amount
        table.min_bet = raise_amount