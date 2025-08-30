# holdem_app/app/services/ai_agent_service.py
import random
from ..models.game_state import GameState
from ..models.enum import ActionType
from . import action_service

class AIAgentService:
    def __init__(self, strategy: str = "random"):
        self.strategy = strategy

    def decide_action(self, gs: GameState, seat_index: int) -> tuple:
        """
        AIの戦略に基づいてアクションを決定する。
        :return: (ActionType, amount) のタプル
        """
        legal_actions = action_service.get_legal_actions(gs, seat_index)
        if not legal_actions:
            return (None, 0)

        # 現状はランダム戦略のみ実装
        if self.strategy == "random":
            possible_actions = list(legal_actions.keys())
            chosen_action_type = random.choice(possible_actions)
            
            amount = 0
            if chosen_action_type == ActionType.CALL:
                amount = legal_actions[ActionType.CALL]
            elif chosen_action_type == ActionType.RAISE:
                raise_info = legal_actions[ActionType.RAISE]
                amount = random.randint(raise_info['min'], raise_info['max'])
                
            return (chosen_action_type, amount)
        
        # 将来的に他の戦略も追加
        # elif self.strategy == "aggressive":
        # ...
        
        else:
            # デフォルトはフォールド
            return (ActionType.FOLD, 0)
