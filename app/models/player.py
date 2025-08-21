from pydantic import BaseModel, Field
from typing import Optional
import uuid


class Player(BaseModel):

    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    initial_stack: int
    is_human: bool = True
    strategy_type: Optional[str] = None  # AI戦略のタイプ
