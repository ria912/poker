# backend/schemas/action_schema.py
from pydantic import BaseModel, Field
from typing import Optional
from backend.models.enum import Action as ActionEnum

class ActionSchema(BaseModel):
    action_type: ActionEnum = Field(..., description="アクション種別（fold, call, check, bet, raise）")
    amount: Optional[int] = Field(None, ge=0, description="チップ数（ベット／レイズ時のみ）")
