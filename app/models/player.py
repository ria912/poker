# app/models/player.py
import uuid

class Player:
    def __init__(self, name: str, is_ai: bool = True):
        self.player_id: str = str(uuid.uuid4())
        self.name: str = name
        self.is_ai: bool = is_ai
    
    def __repr__(self):
        return f"Player(name={self.name}, is_ai={self.is_ai})"