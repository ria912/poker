# holdem_app/app/services/game_orchestrator.py
from app.models.game_state import GameState
from app.models.action import Action
from app.models.enum import Round, GameStatus, SeatStatus, ActionType
from app.services import (
    hand_manager,
    round_manager,
    position_service,
    action_service,
)
from app.services.ai import ai_agent_service

class GameOrchestrator:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def run_game(self, num_hands: int = 1):
        """
        指定されたハンド数だけゲームを実行する
        """
        hand_count = 0
        while hand_count < num_hands:
            # アクティブプレイヤーが2人未満になったらゲームを終了
            if len(position_service.get_occupied_seats(self.game_state)) < 2:
                print("Not enough players to continue. Game over.")
                break
            
            print(f"\n--- Starting Hand #{hand_count + 1} ---")
            self.play_hand()
            hand_count += 1
            
            # スタックが0になったプレイヤーを退席させる
            for seat in self.game_state.table.seats:
                if seat.is_occupied and seat.stack == 0:
                    print(f"{seat.player.name} has been eliminated.")
                    self.game_state.table.stand_player(seat.index)


    def play_hand(self):
        """
        1ハンドを実行する
        """
        hand_manager.start_new_hand(self.game_state)
        
        if self.game_state.status != GameStatus.IN_PROGRESS:
            return

        # プレフロップからリバーまでの各ラウンドをループ
        for round_enum in [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER]:
            self.game_state.current_round = round_enum
            
            # フロップ以降はコミュニティカードをめくる
            if round_enum != Round.PREFLOP:
                print(f"\n--- Dealing {round_enum.name} ---")
                hand_manager.proceed_to_next_round(self.game_state)

            # 誰か一人が残るなど、ハンドが終了していないかチェック
            if hand_manager._is_hand_over(self.game_state):
                break
            
            # ベッティングラウンドを実行
            round_manager.run_betting_round(self.game_state, self._get_action_for_player)
            
            # ベッティングの結果、ハンドが終了していないか再度チェック
            if hand_manager._is_hand_over(self.game_state):
                break
        
        # ハンドの決着
        print("\n--- Showdown ---")
        hand_manager._conclude_hand(self.game_state)
        # 最終的な結果を表示
        self._display_table(self.game_state, show_all_hands=True)
        # 勝者と獲得額を表示
        winners = hand_manager.evaluation_service.find_winners(self.game_state)
        for seat, amount in winners:
            print(f"{seat.player.name} wins {amount}")


    def _get_action_for_player(self, game_state: GameState) -> Action:
        """
        現在のプレイヤーのアクションを取得する（AIと人間を切り替え）
        """
        current_seat = game_state.table.seats[game_state.current_seat_index]
        
        # アクションの前に必ずテーブル状況を表示
        self._display_table(game_state)

        if current_seat.player.is_ai:
            action = ai_agent_service.decide_action(game_state)
            print(f">>> {current_seat.player.name} chooses {action.action_type.name} {action.amount or ''}")
            return action
        else:
            # 人間プレイヤーからの入力を受け付ける
            return self._get_human_action(game_state)

    def _get_human_action(self, game_state: GameState) -> Action:
        """
        人間プレイヤーから有効なアクションを取得する
        """
        seat_index = game_state.current_seat_index
        player_id = game_state.table.seats[seat_index].player.player_id
        valid_actions = action_service.get_valid_actions(game_state, seat_index)

        while True:
            print("\n>>> Your turn. Valid actions:")
            for i, action_info in enumerate(valid_actions):
                print(f"  {i}: {action_info['type'].name}", end="")
                if 'amount' in action_info:
                    print(f" ({action_info['amount']})", end="")
                elif 'min' in action_info and 'max' in action_info:
                    print(f" (min: {action_info['min']}, max: {action_info['max']})", end="")
                print()

            try:
                choice_str = input("Choose action by number: ")
                if not choice_str.isdigit():
                    raise ValueError("Please enter a number.")
                choice = int(choice_str)

                chosen_action_info = valid_actions[choice]
                action_type = chosen_action_info['type']

                amount = chosen_action_info.get('amount') # CALLの場合
                if action_type in [ActionType.BET, ActionType.RAISE]:
                    amount_str = input(f"Enter amount ({chosen_action_info['min']} - {chosen_action_info['max']}): ")
                    if not amount_str.isdigit():
                         raise ValueError("Please enter a number for the amount.")
                    amount = int(amount_str)
                    
                    if not (chosen_action_info['min'] <= amount <= chosen_action_info['max']):
                        print(f"Amount must be between {chosen_action_info['min']} and {chosen_action_info['max']}.")
                        raise ValueError("Invalid amount.")

                return Action(player_id, action_type, amount)

            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}. Please try again.")

    def _display_table(self, game_state: GameState, show_all_hands: bool = False):
        """
        現在のテーブル状況をコンソールに表示する
        """
        print("\n" + "="*60)
        community = [str(c) for c in game_state.table.community_cards]
        print(f"Community: {' '.join(community):<25} Pot: {game_state.table.pot}")
        print("-"*60)

        for seat in game_state.table.seats:
            if seat.is_occupied:
                if show_all_hands or not seat.player.is_ai:
                    hand = ' '.join([str(c) for c in seat.hole_cards])
                else:
                    hand = "? ?"
                
                status = f"({seat.status.name})" if seat.status != SeatStatus.ACTIVE else ""
                dealer = "D" if game_state.dealer_seat_index == seat.index else " "
                turn = "*" if game_state.current_seat_index == seat.index and game_state.status == GameStatus.IN_PROGRESS else " "
                
                print(f"{turn} Seat {seat.index} [{dealer}] {seat.player.name:<8} | Stack: {seat.stack:<6} | Bet: {seat.current_bet:<5} | Hand: {hand:<6} {status}")
        print("="*60)

