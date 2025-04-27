
class Action:
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    RAISE = 'raise'
    ALL_IN = 'all-in'

    @staticmethod
    def get_legal_actions(player, current_bet, min_raise, pot):
        actions = []

        if current_bet == 0:
            # 誰もベットしてない場合
            actions.append(Action.CHECK)
            actions.append(Action.FOLD)

            if player.stack > 0:
                actions.append(Action.BET)
                if player.stack <= min_raise:
                    actions.append(Action.ALL_IN)

        else:
            # 誰かがベットしている場合
            if player.stack > (current_bet - player.current_bet):
                actions.append(Action.CALL)
            else:
                actions.append(Action.ALL_IN)
            actions.append(Action.FOLD)

            if player.stack > (current_bet - player.current_bet + min_raise):
                actions.append(Action.RAISE)
            elif player.stack > 0:
                actions.append(Action.ALL_IN)

        return actions

        @staticmethod
    def apply_action(player, action, table, amount=0):
        """アクションを適用してプレイヤーとテーブルの状態を更新"""
        if action == Action.FOLD:
            player.has_folded = True

        elif action == Action.CHECK:
            # 何もしない
            pass

        elif action == Action.BET:
            if amount > player.stack:
                amount = player.stack  # オールインになる
            player.stack -= amount
            player.current_bet += amount
            table.current_bet = amount
            table.pot += amount

        elif action == Action.CALL:
            call_amount = table.current_bet - player.current_bet
            actual_call = min(player.stack, call_amount)
            player.stack -= actual_call
            player.current_bet += actual_call
            table.pot += actual_call

        elif action == Action.RAISE:
            raise_amount = amount
            to_call = table.current_bet - player.current_bet
            total = to_call + raise_amount
            if total > player.stack:
                total = player.stack  # オールインになる場合
            player.stack -= total
            player.current_bet += total
            table.current_bet += raise_amount  # 現在のベット額にレイズ額を足す
            table.pot += total

        elif action == Action.ALL_IN:
            all_in_amount = player.stack
            player.current_bet += all_in_amount
            player.stack = 0
            if player.current_bet > table.current_bet:
                table.current_bet = player.current_bet
            table.pot += all_in_amount

