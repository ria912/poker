class Action:
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'
    ALL_IN = 'all-in'

    @staticmethod
    def get_legal_actions(player, table):
        """
        プレイヤーに許可されているアクション一覧を返す
        """
        actions = []
        current_bet = table.current_bet
        min_bet = table.min_bet

        if current_bet == 0:
            # 誰もベットしてない
            actions.append(Action.CHECK)
            if player.stack >= min_bet:
                actions.append(Action.BET)
            if player.stack > 0:
                actions.append(Action.ALL_IN)
            actions.append(Action.FOLD)
        else:
            # すでにベットされてる
            to_call = current_bet - player.current_bet
            if player.stack > to_call:
                actions.append(Action.CALL)
                if player.stack >= to_call + min_bet:
                    actions.append(Action.RAISE)
            if player.stack > 0:
                actions.append(Action.ALL_IN)
            actions.append(Action.FOLD)

        return actions

    @staticmethod
    def apply_action(player, action, table, amount=0):
        """
        プレイヤーのアクションを適用してテーブルの状態を更新
        """
        current_bet = table.current_bet
        min_bet = table.min_bet

        if action == Action.FOLD:
            player.has_folded = True

        elif action == Action.CHECK:
            pass  # 何もしない

        elif action == Action.BET:
            if amount < min_bet:
                raise ValueError(f"Bet must be at least {min_bet}")
                amount = min_bet
            if amount >= player.stack:
                # オールイン扱い
                amount = player.stack
            player.stack -= amount
            player.current_bet += amount
            table.current_bet = amount
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
            if amount < min_bet:
                raise ValueError(f"Raise must be at least {min_bet}")
            to_call = current_bet - player.current_bet
            total_raise = to_call + amount
            if total_raise >= player.stack:
                # オールイン扱い
                total_raise = player.stack
                amount = total_raise - to_call  # 実際のraise幅を再計算
            player.stack -= total_raise
            player.current_bet += total_raise
            table.current_bet = player.current_bet
            table.min_bet = amount
            table.pot += total_raise

        elif action == Action.ALL_IN:
            all_in_amount = player.stack
            player.current_bet += all_in_amount
            player.stack = 0
            if player.current_bet > table.current_bet:
                table.min_bet = player.current_bet - table.current_bet
                table.current_bet = player.current_bet
            table.pot += all_in_amount