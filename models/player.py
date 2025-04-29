class Player:
    def __init__(self, name="player", is_human=False, stack=10000):
        self.name = name
        self.is_human = is_human
        self.stack = stack
        self.hand = []
        self.position = None
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.has_left = False

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.position = None

    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "current_bet": self.current_bet,
            "hand": self.hand if self.is_human else ["X", "X"],
            "position": self.position,
            "has_folded": self.has_folded,
            "last_action": self.last_action
        }
    
    def decide_action(self, legal_actions):
        """
        人間プレイヤーのためにUIから入力を受け付ける（仮の実装）
        """
        if self.is_human:
            action = input(f"{self.name}, choose your action: {legal_actions}")
            amount = 0
            if action in ['bet', 'raise', 'all-in']:
                amount = int(input("Enter the amount: "))
            self.last_action = action
            return action, amount
        else:
            raise NotImplementedError("AI logic not implemented yet.")