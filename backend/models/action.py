# models/action.py
class Action:
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'
    ALL_IN = 'all-in'

    @staticmethod
    def get_legal_actions(player, table):
        actions = []
        current_bet = table.current_bet
        min_bet = table.min_bet
        to_call = current_bet - player.current_bet

        actions.append(Action.FOLD)

        if current_bet == player.current_bet:
            actions.append(Action.CHECK)
            if player.stack >= min_bet:
                actions.append(Action.BET)
                
        else:
            if player.stack >= to_call:
                actions.append(Action.CALL)
                if player.stack >= to_call + min_bet:
                    actions.append(Action.RAISE)
                

        if player.stack > 0:
            actions.append(Action.ALL_IN)

        return {
            "actions": actions,
            "current_bet": current_bet,
            "min_bet": min_bet,
            "player_bet": player.current_bet,
            "pot": table.pot,
            "amount_ranges": {
                "bet": [player.stack - min_bet],
                "raise": [player.stack - to_call - min_bet],
            }
        }

    @staticmethod
    def apply_action(player, action, table, amount=0):
        current_bet = table.current_bet
        min_bet = table.min_bet

        if action == Action.FOLD:
            pass  # フォールドは何も変更なし(round_manager.py で処理)
        elif action == Action.CHECK:
            pass  # チェックは何も変更なし
        elif action == Action.BET:
            Action._apply_bet(player, table, amount, min_bet)
        elif action == Action.CALL:
            Action._apply_call(player, table, current_bet)
        elif action == Action.RAISE:
            Action._apply_raise(player, table, amount, min_bet, is_raise=True)
        elif action == Action.ALL_IN:
            Action._apply_all_in(player, table)

    @staticmethod
    def _apply_bet(player, table, amount, min_bet):
        if amount < 0:
            raise ValueError("Bet/Raise must be a non-negative amount")
        min_bet = table.min_bet
        total = amount + min_bet
        total = min(player.stack, total)

        player.stack -= total
        player.current_bet += total
        table.current_bet = player.current_bet
        table.pot += total
        if table.min_bet < total:
            table.min_bet = total

    @staticmethod
    def _apply_call(player, table, amount):
        if amount < 0:
            raise ValueError("Call must be a non-negative amount")
        
        to_call = table.current_bet - player.current_bet
        amount = min(player.stack, to_call)
        player.stack -= amount
        player.current_bet += amount
        table.current_bet = player.current_bet
        table.pot += amount

    @staticmethod
    def _apply_raise(player, table, amount, min_bet):
        if amount < 0:
            raise ValueError("Bet/Raise must be a non-negative amount")
        min_bet = table.min_bet
        call_amount = table.current_bet - player.current_bet
        total = amount + min_bet + call_amount
        total = min(player.stack, total)

        player.stack -= total
        player.current_bet += total
        table.current_bet = player.current_bet
        table.pot += total
        if min_bet < total - call_amount:
            table.min_bet = total - call_amount

    @staticmethod
    def _apply_all_in(player, table):
        amount = player.stack
        player.stack = 0
        player.current_bet += amount
        if player.current_bet > table.current_bet:
            table.current_bet = player.current_bet
            table.min_bet = amount
        table.pot += amount