# models/action.py
from enum import Enum

class Action(str, Enum):
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'

    @staticmethod
    def get_legal_actions(player, table):
        actions = []
        current_bet = table.current_bet
        min_bet = table.min_bet
        to_call = current_bet - player.current_bet

        actions.append(Action.FOLD)

        if current_bet == player.current_bet:
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
            "actions": actions,
            "current_bet": current_bet,
            "min_bet": min_bet,
            "player_bet": player.current_bet,
            "pot": table.pot,
            "amount_ranges": {
                "bet": [max(0,player.stack - min_bet)],
                "raise": [max(0,player.stack - to_call - min_bet)],
            }
        }

    @staticmethod
    def apply_action(player, table, action, amount=0):
        if action == Action.FOLD:
            player.has_folded = True
        elif action == Action.CHECK:
            pass
        elif action == Action.BET:
            Action._apply_bet(player, table, amount)
        elif action == Action.CALL:
            Action._apply_call(player, table)
        elif action == Action.RAISE:
            Action._apply_raise(player, table, amount)
        
        player.has_acted = True
        player.last_action = action

        if player.stack == 0:
            player.has_all_in = True

    @staticmethod
    def _apply_bet(player, table, amount):
        if amount < 0:
            raise ValueError(f"Invalid Bet amount: {amount}. Must be >= 0.")
        min_bet = table.min_bet
        total = amount + min_bet
        total = min(player.stack, total)

        player.stack -= total
        player.current_bet += total
        table.current_bet = player.current_bet
        table.pot += total

        if total > table.min_bet:
            table.min_bet = total

    @staticmethod
    def _apply_call(player, table):      
        to_call = table.current_bet - player.current_bet
        total = min(player.stack, to_call)

        player.stack -= total
        player.current_bet += total
        table.pot += total

        if player.current_bet > table.current_bet:
            table.current_bet = player.current_bet

    @staticmethod
    def _apply_raise(player, table, amount):
        if amount < 0:
            raise ValueError(f"Invalid Bet/Raise amount: {amount}. Must be >= 0.")
        min_bet = table.min_bet
        call_amount = table.current_bet - player.current_bet
        total = amount + min_bet + call_amount
        total = min(player.stack, total)

        player.stack -= total
        player.current_bet += total
        table.pot += total
        table.current_bet = player.current_bet

        raise_amount = total - call_amount
        if raise_amount > table.min_bet:
            table.min_bet = raise_amount