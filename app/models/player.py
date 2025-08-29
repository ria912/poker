# app/models/player.py
from typing import List, Optional
import uuid

from .deck import Card

class Player:
    def __init__(self, name: str, is_ai: bool = True):
        self.player_id: str = str(uuid.uuid4())
        self.name: str = name
        self.is_ai: bool = is_ai