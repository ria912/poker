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
            "pot": table.pot
        }

    @staticmethod
    def apply_action(player, action, table, amount=0):
        current_bet = table.current_bet
        min_bet = table.min_bet

        if action == Action.FOLD:
            player.has_folded = True

        elif action == Action.CHECK:
            pass

        elif action == Action.BET:
            if amount < min_bet:
                raise ValueError(f"Bet must be at least {min_bet}")
            if amount >= player.stack:
                action = Action.ALL_IN
            else:
                player.stack -= amount
                player.current_bet += amount
                table.current_bet = player.current_bet
                table.min_bet = amount
                table.pot += amount

        elif action == Action.CALL:
            to_call = current_bet - player.current_bet
            call_amount = min(player.stack, to_call)
            player.stack -= call_amount
            player.current_bet += call_amount
            table.current_bet = player.current_bet
            table.pot += call_amount

        elif action == Action.RAISE:
            to_call = current_bet - player.current_bet
            if amount < min_bet:
                raise ValueError(f"Raise must be at least {min_bet}")
            total = to_call + amount
            total = min(player.stack, total)
            raise_amount = total - to_call
            player.stack -= total
            player.current_bet += total
            table.current_bet = player.current_bet
            table.min_bet = raise_amount
            table.pot += total

        elif action == Action.ALL_IN:
            all_in_amount = player.stack
            player.stack = 0
            player.current_bet += all_in_amount
            raise_amt = player.current_bet - table.current_bet
            if raise_amt >= min_bet:
                table.min_bet = raise_amt
                table.current_bet = player.current_bet
            table.pot += all_in_amount
