# server/app/models/action.py
import uuid
from sqlalchemy import String, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from .enums import ActionType

class Action(Base):
    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hand_id: Mapped[str] = mapped_column(ForeignKey("hands.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)
    amount: Mapped[int | None] = mapped_column(Integer)

    # ActionとHand, Userのリレーションシップ
    hand = relationship("Hand", back_populates="actions")
    user = relationship("User") # アクションを行ったユーザーを簡単に参照できるようにする

    def __repr__(self) -> str:
        return f"<Action(user_id={self.user_id}, type={self.action_type.name}, amount={self.amount})>"
